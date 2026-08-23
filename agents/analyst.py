"""ANALYST — the only agent that touches raw candles.

Everyone downstream reasons about the Briefing it produces. That's a design
choice with teeth: it means a change to how the market is *perceived* is one
isolated, testable gene set, and no consult can quietly invent its own private
indicator that nobody else can audit.
"""
from __future__ import annotations

import math

import numpy as np

from core.genome import Genome
from core.market import ReplayWindow
from core.types import Briefing, Features


def _sma(a: np.ndarray, n: int) -> float:
    if len(a) < n or n <= 0:
        return float("nan")
    return float(np.mean(a[-n:]))


def _rsi(a: np.ndarray, n: int) -> float:
    if len(a) < n + 1:
        return 50.0
    d = np.diff(a[-(n + 1):])
    up = float(np.mean(np.clip(d, 0, None)))
    dn = float(np.mean(np.clip(-d, 0, None)))
    if dn < 1e-12:
        return 100.0 if up > 0 else 50.0
    rs = up / dn
    return float(100 - 100 / (1 + rs))


def _ann_vol(a: np.ndarray, n: int, bars_per_year: float = 365.0) -> float:
    if len(a) < n + 1:
        return float("nan")
    r = np.diff(a[-(n + 1):]) / np.maximum(a[-(n + 1):-1], 1e-12)
    return float(np.std(r, ddof=1) * math.sqrt(bars_per_year)) if len(r) > 1 else float("nan")


class Analyst:
    name = "analyst"

    def __init__(self, genome: Genome):
        self.g = genome
        self.genes = genome.genes("analyst")

    def brief(self, w: ReplayWindow, equity: float, cash: float,
              weights: dict[str, float]) -> Briefing:
        g = self.genes
        fast = int(g.get("trend_fast", 10))
        slow = int(g.get("trend_slow", 50))
        need = max(slow, int(g.get("z_len", 30)), int(g.get("breakout_len", 20))) + 5

        feats: dict[str, Features] = {}
        raw_mom: dict[str, float] = {}

        for sym in self.g.universe:
            c = w.closes(sym, need + 10)
            c = c[~np.isnan(c)]
            if len(c) < need:
                continue
            price = float(c[-1])
            ma_f = _sma(c, fast)
            ma_s = _sma(c, slow)
            if not (math.isfinite(ma_f) and math.isfinite(ma_s)) or ma_s <= 0:
                continue

            prev_ma_f = _sma(c[:-3], fast) if len(c) > fast + 3 else ma_f
            slope = (ma_f / prev_ma_f - 1) if prev_ma_f > 0 else 0.0

            zwin = c[-int(g.get("z_len", 30)):]
            sd = float(np.std(zwin, ddof=1))
            z = (price - float(np.mean(zwin))) / sd if sd > 1e-12 else 0.0

            bl = int(g.get("breakout_len", 20))
            hi = float(np.max(c[-bl:]))
            breakout = price / hi - 1 if hi > 0 else 0.0

            run_high = float(np.max(c[-slow:]))
            dd_high = price / run_high - 1 if run_high > 0 else 0.0

            v_s = _ann_vol(c, int(g.get("vol_short", 10)))
            v_l = _ann_vol(c, int(g.get("vol_long", 40)))
            vol_ratio = (v_s / v_l) if (math.isfinite(v_s) and math.isfinite(v_l) and v_l > 1e-9) else 1.0

            vv = w.volumes(sym, int(g.get("volume_len", 20)) + 1)
            vv = vv[~np.isnan(vv)]
            vol_shock = 1.0
            if len(vv) > 3 and np.mean(vv[:-1]) > 0:
                vol_shock = float(vv[-1] / np.mean(vv[:-1]))

            r1 = c[-1] / c[-2] - 1 if len(c) > 1 else 0.0
            r5 = c[-1] / c[-6] - 1 if len(c) > 5 else 0.0
            r20 = c[-1] / c[-21] - 1 if len(c) > 20 else 0.0

            feats[sym] = Features(
                symbol=sym, price=price, ret_1=r1, ret_5=r5, ret_20=r20,
                trend=ma_f / ma_s - 1, slope=slope, rsi=_rsi(c, int(g.get("rsi_len", 14))),
                vol=v_s if math.isfinite(v_s) else 0.0, vol_ratio=vol_ratio,
                dd_from_high=dd_high, dist_ma=price / ma_s - 1, zscore=z,
                volume_shock=vol_shock, breakout=breakout, rank_mom=0.0)
            raw_mom[sym] = r20

        # cross-sectional momentum rank: 1.0 = strongest in the universe.
        # Relative strength matters more than absolute in a market where
        # everything moves together.
        if raw_mom:
            order = sorted(raw_mom, key=lambda s: raw_mom[s])
            n = max(len(order) - 1, 1)
            for i, sym in enumerate(order):
                f = feats[sym]
                feats[sym] = Features(**{**f.as_dict(), "rank_mom": i / n})

        regime, score, breadth = self._regime(w, feats)
        return Briefing(
            ts=str(w.ts), regime=regime, regime_score=score, breadth=breadth,
            features=feats, equity=equity,
            cash_pct=(cash / equity) if equity > 0 else 1.0,
            open_positions=dict(weights))

    def _regime(self, w: ReplayWindow, feats: dict[str, Features]) -> tuple[str, float, float]:
        g = self.genes
        anchor = g.get("regime_anchor", "BTCUSDT")
        n = int(g.get("regime_ma", 50))
        c = w.closes(anchor, n + 10)
        c = c[~np.isnan(c)]

        anchor_score, anchor_dd, anchor_volr = 0.0, 0.0, 1.0
        if len(c) >= n:
            ma = _sma(c, n)
            anchor_score = (c[-1] / ma - 1) if ma > 0 else 0.0
            hi = float(np.max(c[-n:]))
            anchor_dd = c[-1] / hi - 1 if hi > 0 else 0.0
            vs, vl = _ann_vol(c, 10), _ann_vol(c, 40)
            if math.isfinite(vs) and math.isfinite(vl) and vl > 1e-9:
                anchor_volr = vs / vl

        breadth = (sum(1 for f in feats.values() if f.trend > 0) / len(feats)) if feats else 0.0
        score = float(np.clip(anchor_score * 4 + (breadth - 0.5) * 2, -1, 1))

        # crisis is not just "down" — it's down *and* violent. Distinguishing
        # them matters: a slow bear is tradable, a crash is not.
        if anchor_dd < -0.22 and anchor_volr > 1.35:
            return "crisis", score, breadth
        if anchor_score > 0.02 and breadth > 0.5:
            return "bull", score, breadth
        if anchor_score < -0.03 or breadth < 0.30:
            return "bear", score, breadth
        return "chop", score, breadth
