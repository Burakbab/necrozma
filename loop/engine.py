"""The decision cycle, and the backtest that replays it over history.

One tick:
    mark portfolio  ->  Guardian forced exits  ->  Analyst briefing
    ->  3 Consults  ->  Risk Judge  ->  Superior Judge  ->  Trader
    ->  fills at the NEXT bar's open

The same function runs a 4-year backtest and (later) a single live bar. There
is exactly one code path for "what does the system do right now", which is the
only way a live run can ever be expected to match its own backtest.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import asdict
from typing import Any

import numpy as np

from agents.analyst import Analyst
from agents.consults import build_consults
from agents.judges import RiskJudge, SuperiorJudge, flag_hard_call
from agents.trader import Guardian, Trader
from core import market
from core.genome import Genome
from core.market import Replay
from core.portfolio import PaperBroker
from core.types import Order, Verdict
from constitution import (CIRCUIT_BREAKER_DD, CIRCUIT_BREAKER_COOLDOWN,
                          CIRCUIT_BREAKER_FLATTEN, fitness)


class Council:
    """The whole roster, assembled from a genome."""

    def __init__(self, genome: Genome, broker: PaperBroker):
        self.genome = genome
        self.broker = broker
        self.analyst = Analyst(genome)
        self.consults = build_consults(genome)
        self.risk_judge = RiskJudge(genome)
        self.superior = SuperiorJudge(genome)
        self.guardian = Guardian(genome)
        self.trader = Trader(broker)
        self.decision_log: list[dict[str, Any]] = []

    def tick(self, window, prices: dict[str, float], fill_prices: dict[str, float],
             log_detail: bool = True) -> None:
        b = self.broker
        ts = str(window.ts)
        nav = b.mark(ts, prices, dd_halt=CIRCUIT_BREAKER_DD,
                     cooldown=CIRCUIT_BREAKER_COOLDOWN)

        forced = self.guardian.forced_exits(b, prices)
        if b.just_halted and CIRCUIT_BREAKER_FLATTEN:
            # A breaker that freezes new entries but keeps the existing book is
            # theatre — the damage is already in the positions you hold.
            held = {o.symbol for o in forced}
            for sym, pos in list(b.positions.items()):
                if pos.is_open and sym not in held:
                    forced.append(Order(symbol=sym, side="sell", fraction=1.0,
                                        reason_chain=["circuit_breaker: flatten book"],
                                        conviction=1.0, agreement=1.0))
        if forced:
            self.trader.execute(ts, forced, fill_prices)

        weights = {s: b.position_weight(s, prices) for s in b.positions if b.positions[s].is_open}
        briefing = self.analyst.brief(window, nav, b.cash, weights)
        proposals = [c.consider(briefing) for c in self.consults]
        verdict = self.risk_judge.rule(briefing, proposals, len(self.consults))
        overrides_before = self.superior.override_count
        final: Verdict = self.superior.review(briefing, verdict, b.halted)
        overrides_this_bar = self.superior.override_count - overrides_before
        fills = self.trader.execute(ts, final.orders, fill_prices)

        if log_detail and (fills or forced or final.vetoes):
            self.decision_log.append({
                "ts": ts, "nav": nav, "regime": briefing.regime,
                "breadth": briefing.breadth, "cash_pct": briefing.cash_pct,
                "proposals": {p.agent: [
                    {"symbol": i.symbol, "side": i.side,
                     "conviction": round(i.conviction, 3), "why": i.rationale}
                    for i in p.intents] for p in proposals},
                "forced_exits": [{"symbol": o.symbol, "why": o.reason_chain[0]} for o in forced],
                "orders": [{"symbol": o.symbol, "side": o.side,
                            "amount": round(o.quote_amount, 2), "fraction": o.fraction,
                            "agreement": round(o.agreement, 2),
                            "why": o.reason_chain} for o in final.orders],
                "vetoes": [asdict(v) for v in final.vetoes[:12]],
                "fills": fills,
                "notes": final.notes,
                "hard_call": flag_hard_call(final.orders, b.just_halted, overrides_this_bar,
                                            nav=nav, min_size_pct=0.10),
            })


def benchmark_buy_hold(replay: Replay, symbols: list[str], start: int, end: int,
                       cash: float, bars_per_year: float = 365.25) -> dict[str, Any]:
    """Equal-weight buy-and-hold. The honest bar to clear — beating your own
    ancestors means nothing if a lazy index beats you both."""
    usable = [s for s in symbols if replay.next_open(s, start) not in (None, 0)]
    if not usable:
        return {}
    per = cash / len(usable)
    qty = {s: per / replay.next_open(s, start) for s in usable}
    navs = []
    for i in range(start + 1, end):
        v = 0.0
        for s in usable:
            px = replay.close_at(s, i)
            if px:
                v += qty[s] * px
        navs.append(v)
    if len(navs) < 3:
        return {}
    import numpy as np
    a = np.array(navs)
    rets = np.diff(a) / np.maximum(a[:-1], 1e-9)
    peaks = np.maximum.accumulate(a)
    import math
    vol = float(np.std(rets, ddof=1)) * math.sqrt(bars_per_year)
    return {
        "total_return": float(a[-1] / a[0] - 1),
        "max_dd": float(np.min(a / peaks - 1)),
        "sharpe": float(np.mean(rets) * bars_per_year / vol) if vol > 1e-9 else 0.0,
        "end_nav": float(a[-1]), "start_nav": float(a[0]),
    }


def pairwise_correlation_stats(rets: dict[str, np.ndarray],
                               threshold: float = 0.5) -> dict[str, Any]:
    """Every pairwise Pearson correlation across a set of return series, summarised.

    Originally built to answer a structural question the live mechanism at
    the time (agents.judges.RiskJudge._correlation_scale, a gene that only
    ever compared a *new* buy against symbols already held, on the
    reasoning that unheld correlation can't hurt a portfolio that isn't
    exposed to it) never asked. That gene has since been removed as dead
    weight (AGENTS.md item 3, 2026-08-20) once the evidence this function
    helped gather settled on "drop". This function stays: it looks at the
    whole universe's pairwise structure -- whether there's a tightly
    correlated cluster, or a correlation regime (crisis contagion) a
    held-vs-candidate check would only catch after a position is already
    open -- independent of any genome, still useful for any future
    concentration/diversification question. Read-only: takes
    already-sliced return arrays, never a genome, broker, or replay -- it
    cannot touch anything by construction.

    A symbol with too little history or a near-zero-variance return series
    over the window is silently dropped from the pair count rather than
    raising -- fail toward nothing to report.
    """
    syms = sorted(rets.keys())
    pairs: list[float] = []
    for i, a in enumerate(syms):
        ra = rets[a]
        for b in syms[i + 1:]:
            rb = rets[b]
            n = min(len(ra), len(rb))
            if n < 5:
                continue
            xa, xb = ra[-n:], rb[-n:]
            if not (np.all(np.isfinite(xa)) and np.all(np.isfinite(xb))):
                continue
            sa, sb = np.std(xa), np.std(xb)
            if sa < 1e-12 or sb < 1e-12:
                continue
            c = float(np.corrcoef(xa, xb)[0, 1])
            if np.isfinite(c):
                pairs.append(c)
    if len(syms) < 3 or not pairs:
        return {"error": "fewer than 3 usable symbols or no valid pairs",
                "n_symbols": len(syms), "n_pairs": len(pairs)}
    arr = np.array(pairs)
    return {
        "n_symbols": len(syms),
        "n_pairs": int(len(arr)),
        "mean_corr": float(np.mean(arr)),
        "median_corr": float(np.median(arr)),
        "min_corr": float(np.min(arr)),
        "max_corr": float(np.max(arr)),
        "frac_above_threshold": float(np.mean(arr >= threshold)),
        "threshold": threshold,
    }


def holding_mask(closed_trades: list[dict], open_positions: list[dict],
                ts_index: dict[str, int], n: int) -> dict[str, np.ndarray]:
    """Boolean per-bar mask of which symbols the account actually held,
    reconstructed purely from closed_trades' entry/exit timestamps plus
    any positions still open at the end of the replay window -- no genome
    or broker access needed, just run_backtest's own returned records.

    Exists to answer the follow-up `correlation-universe` left open:
    raw universe-wide pairwise correlation (what `pairwise_correlation_
    stats` measures across every symbol) is not the same question as
    portfolio-realized correlation -- whether the symbols the champion
    actually holds *together* happen to be more or less correlated than
    the universe at large. This mask is the bridge: index it by bar to
    get the held set, then feed that subset into the same
    `pairwise_correlation_stats` function.

    Bar i counts as held for [entry_i, exit_i) -- half-open, matching
    core.portfolio's own fill-to-fill convention (a position is open from
    the bar it fills on up to, not including, the bar the closing fill
    lands on). A timestamp missing from ts_index is silently skipped
    rather than raising -- the same fail-toward-nothing-to-report
    convention `pairwise_correlation_stats` already uses for degenerate
    input.
    """
    mask: dict[str, np.ndarray] = {}

    def mark(symbol, entry_ts, exit_i):
        entry_i = ts_index.get(entry_ts)
        if entry_i is None or symbol is None:
            return
        arr = mask.setdefault(symbol, np.zeros(n, dtype=bool))
        lo, hi = max(0, entry_i), min(n, exit_i)
        if hi > lo:
            arr[lo:hi] = True

    for t in closed_trades:
        exit_i = ts_index.get(t.get("exit_ts"))
        if exit_i is not None:
            mark(t.get("symbol"), t.get("entry_ts"), exit_i)
    for p in open_positions:
        mark(p.get("symbol"), p.get("opened_ts"), n)
    return mask



def drawdown_episodes(nav_history: list[tuple[str, float]],
                      top_n: int = 5) -> list[dict[str, Any]]:
    """Break a nav_history series into peak-to-trough drawdown episodes.

    `stats()`'s `max_dd` is a single number: the deepest point relative to
    its own running peak. It doesn't say *when* that happened or whether it
    was one bad stretch or several. This walks the same nav series and
    returns each episode (peak date/nav, trough date/nav, depth, recovery
    date if any) so the answer to "what period drives the drawdown" is a
    date range, not a guess. Deepest episode's `dd_pct` reproduces
    `stats()`'s `max_dd` exactly (same running-peak definition).
    """
    if len(nav_history) < 3:
        return []
    episodes: list[dict[str, Any]] = []
    peak_ts, peak_nav, peak_i = nav_history[0][0], nav_history[0][1], 0
    trough_ts, trough_nav, trough_i = peak_ts, peak_nav, 0
    in_drawdown = False

    def close_episode(recovery_ts):
        dd = trough_nav / peak_nav - 1 if peak_nav > 0 else 0.0
        episodes.append({
            "peak_ts": peak_ts, "peak_nav": float(peak_nav),
            "trough_ts": trough_ts, "trough_nav": float(trough_nav),
            "dd_pct": float(dd),
            "peak_to_trough_bars": trough_i - peak_i,
            "recovery_ts": recovery_ts,
        })

    for i, (ts, nav) in enumerate(nav_history[1:], start=1):
        if nav >= peak_nav:
            if in_drawdown:
                close_episode(recovery_ts=ts)
                in_drawdown = False
            peak_ts, peak_nav, peak_i = ts, nav, i
            trough_ts, trough_nav, trough_i = ts, nav, i
        else:
            in_drawdown = True
            if nav < trough_nav:
                trough_ts, trough_nav, trough_i = ts, nav, i
    if in_drawdown:
        close_episode(recovery_ts=None)
    episodes.sort(key=lambda e: e["dd_pct"])
    return episodes[:top_n]


def trade_anatomy(result: dict[str, Any], top_n: int = 5) -> dict[str, Any]:
    """The full post-mortem on every closed trade.

    A 60% win rate sitting next to a large negative stop-loss total is not a
    contradiction, it is a shape: many small wins funding a few structural
    losers. Aggregate stats hide that; this does not. Nothing here feeds
    fitness — it exists so a human can see the internal economy before
    deciding that another evolution generation is the useful next move.
    """
    trades = result.get("closed_trades", [])
    if not trades:
        return {"error": "no closed trades"}

    # entry timestamp -> market regime, so P&L can be cut by conditions
    regime_at = {d.get("ts"): d.get("regime") for d in result.get("decision_log", [])}

    pnls = [float(t.get("pnl", 0.0)) for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    gross_win, gross_loss = sum(wins), -sum(losses)
    ranked = sorted(trades, key=lambda t: float(t.get("pnl", 0.0)))

    def bucket(t):
        b = int(t.get("bars_held", 0) or 0)
        if b <= 1:
            return "1 bar"
        if b <= 5:
            return "2-5 bars"
        if b <= 20:
            return "6-20 bars"
        return "21+ bars"

    def group(keyfn):
        out: dict[str, dict] = {}
        for t in trades:
            for k in keyfn(t):
                g = out.setdefault(str(k), {"n": 0, "pnl": 0.0, "wins": 0})
                g["n"] += 1
                g["pnl"] += float(t.get("pnl", 0.0))
                if float(t.get("pnl", 0.0)) > 0:
                    g["wins"] += 1
        for g in out.values():
            g["mean"] = g["pnl"] / max(g["n"], 1)
            g["win_rate"] = g["wins"] / max(g["n"], 1)
        return dict(sorted(out.items(), key=lambda kv: kv[1]["pnl"]))

    def brief(t):
        return {"symbol": t.get("symbol"), "pnl": round(float(t.get("pnl", 0.0)), 2),
                "pnl_pct": round(float(t.get("pnl_pct", 0.0)), 4),
                "bars_held": t.get("bars_held"),
                "exit_reason": str(t.get("exit_reason", ""))[:60],
                "entry_ts": str(t.get("entry_ts", ""))[:10]}

    top_losses = [brief(t) for t in ranked[:top_n]]
    return {
        "n_trades": len(trades),
        "expectancy": sum(pnls) / len(pnls),
        "total_pnl": sum(pnls),
        "win_rate": len(wins) / len(trades),
        "median_win": float(np.median(wins)) if wins else 0.0,
        "median_loss": float(np.median(losses)) if losses else 0.0,
        "mean_win": float(np.mean(wins)) if wins else 0.0,
        "mean_loss": float(np.mean(losses)) if losses else 0.0,
        "profit_factor": (gross_win / gross_loss) if gross_loss > 1e-9 else float("inf"),
        "largest_losses": top_losses,
        "largest_wins": [brief(t) for t in ranked[::-1][:top_n]],
        # If a handful of trades explain most of the damage, the real risk is
        # tail-shaped and no amount of win-rate tuning addresses it.
        "top_loss_share_of_gross_loss": (
            sum(-x["pnl"] for x in top_losses) / gross_loss if gross_loss > 1e-9 else 0.0),
        "by_entry_agent": group(lambda t: (t.get("entry_agents") or ["unattributed"])),
        "by_exit_reason": group(lambda t: [str(t.get("exit_reason", "")).split(":")[0].strip()[:30]
                                           or "unknown"]),
        "by_symbol": group(lambda t: [t.get("symbol", "?")]),
        "by_holding_period": group(lambda t: [bucket(t)]),
        "by_regime": group(lambda t: [regime_at.get(t.get("entry_ts")) or "unrecorded"]),
    }


def consult_correlation(result: dict[str, Any]) -> dict[str, Any]:
    """Are the three consults actually three opinions?

    The design claims momentum, mean reversion and confirmed trend are
    different theories, and that their agreement therefore carries
    information. That is a hypothesis about the *outputs*, and it has never
    been measured. If two consults are 0.85 correlated, their agreement is one
    opinion counted twice and the Risk Judge is reading its own echo.

    Caveat, stated in the output because it changes the reading: the decision
    log only records bars where something happened (a fill, a forced exit or a
    veto), so these correlations describe agreement on active bars, not on all
    bars.
    """
    log = result.get("decision_log", [])
    if not log:
        return {"error": "no decision log — run the backtest with log_detail=True"}

    agents, signals = set(), {}
    for d in log:
        ts, regime = d.get("ts"), d.get("regime")
        for agent, intents in (d.get("proposals") or {}).items():
            agents.add(agent)
            for i in intents:
                side = i.get("side")
                if side == "hold":
                    continue
                v = float(i.get("conviction", 0.0)) * (1.0 if side == "buy" else -1.0)
                signals.setdefault(agent, {})[(ts, i.get("symbol"))] = (v, regime)
    agents = sorted(agents)
    if len(agents) < 2:
        return {"error": "fewer than two consults recorded"}

    keys = sorted({k for a in agents for k in signals.get(a, {})})

    def vec(a, subset):
        return np.array([signals.get(a, {}).get(k, (0.0, None))[0] for k in subset])

    def corr(x, y):
        if len(x) < 3 or float(np.std(x)) < 1e-9 or float(np.std(y)) < 1e-9:
            return None
        return float(np.corrcoef(x, y)[0, 1])

    pairs: dict[str, Any] = {}
    for i, a in enumerate(agents):
        for b in agents[i + 1:]:
            ka, kb = set(signals.get(a, {})), set(signals.get(b, {}))
            union, inter = ka | kb, ka & kb
            same_side = sum(1 for k in inter
                            if (signals[a][k][0] > 0) == (signals[b][k][0] > 0))
            pairs[f"{a} vs {b}"] = {
                "signal_correlation": corr(vec(a, keys), vec(b, keys)),
                "proposal_overlap_jaccard": len(inter) / len(union) if union else 0.0,
                "same_side_when_both_act": (same_side / len(inter)) if inter else None,
                "n_shared_proposals": len(inter),
            }

    by_regime: dict[str, Any] = {}
    for r in sorted({v[1] for a in agents for v in signals.get(a, {}).values() if v[1]}):
        sub = [k for k in keys
               if any(signals.get(a, {}).get(k, (0.0, None))[1] == r for a in agents)]
        if len(sub) < 10:
            continue
        by_regime[r] = {f"{a} vs {b}": corr(vec(a, sub), vec(b, sub))
                        for i, a in enumerate(agents) for b in agents[i + 1:]}

    trades = result.get("closed_trades", [])
    multi = sum(1 for t in trades if len(t.get("entry_agents") or ()) > 1)
    return {
        "note": ("correlations cover bars the decision log recorded (fills, forced "
                 "exits, vetoes) — not every bar"),
        "n_active_bars": len(log),
        "n_proposal_points": len(keys),
        "pairs": pairs,
        "by_regime": by_regime,
        "trades_with_multiple_entry_agents": (multi / len(trades)) if trades else 0.0,
    }


def edge_vs_benchmark(stats: dict[str, Any], bench: dict[str, Any],
                      bars_per_year: float = 365.25) -> dict[str, Any]:
    """What the council added over doing nothing at all.

    Fitness is Sortino-shaped, and Sortino is perfectly capable of looking
    healthy while the strategy quietly trails an equal-weight basket of the
    same coins. That is the failure this exists to make unhideable: a rising
    market lifts the council too, and "we made money" is not the claim — "we
    made more than sitting still" is.

    Reported, never optimised. Folding excess return into fitness would only
    move the overfitting target; the point is that no promotion can be read
    without also seeing what the lazy alternative did over the same bars.
    """
    if not bench or stats.get("error"):
        return {}
    yrs = max(float(stats.get("bars", 0)) / max(bars_per_year, 1e-9), 1e-6)

    def annualise(total_return: float) -> float:
        base = 1.0 + float(total_return)
        if base <= 0.0:            # a wipeout has no meaningful CAGR
            return -1.0
        return base ** (1.0 / yrs) - 1.0

    s_ret = float(stats.get("total_return", 0.0))
    b_ret = float(bench.get("total_return", 0.0))
    s_dd, b_dd = abs(float(stats.get("max_dd", 0.0))), abs(float(bench.get("max_dd", 0.0)))
    return {
        "excess_return": s_ret - b_ret,
        "excess_return_annual": annualise(s_ret) - annualise(b_ret),
        "excess_sharpe": float(stats.get("sharpe", 0.0)) - float(bench.get("sharpe", 0.0)),
        "drawdown_delta": s_dd - b_dd,      # negative means shallower than the benchmark
        "trades_per_year": float(stats.get("trades", 0)) / yrs,
        "beat_benchmark": bool(s_ret > b_ret),
    }


def run_backtest(genome: Genome, data: dict, start_frac: float = 0.0,
                 end_frac: float = 1.0, log_detail: bool = True,
                 warmup: int = 60) -> dict[str, Any]:
    """Replay a slice of history through the full council."""
    replay = Replay({s: df for s, df in data.items() if s in genome.universe})
    n = len(replay)
    if n < warmup + 120:
        return {"error": f"not enough bars ({n})"}

    start = max(warmup, int(n * start_frac))
    end = min(n - 1, int(n * end_frac))
    if end - start < 120:
        return {"error": f"slice too short ({end - start} bars)"}

    bcfg = genome.data.get("broker", {})
    broker = PaperBroker(cash=float(bcfg.get("start_cash", 10_000.0)),
                         fee_bps=float(bcfg.get("fee_bps", 10.0)),
                         slippage_bps=float(bcfg.get("slippage_bps", 5.0)))
    council = Council(genome, broker)

    for i, window in replay.walk(start, end):
        prices = {s: replay.close_at(s, i) for s in replay.data}
        prices = {s: p for s, p in prices.items() if p is not None}
        fills = {s: replay.next_open(s, i) for s in replay.data}
        fills = {s: p for s, p in fills.items() if p is not None}
        council.tick(window, prices, fills, log_detail=log_detail)

    # final mark
    last_prices = {s: replay.close_at(s, end) for s in replay.data}
    last_prices = {s: p for s, p in last_prices.items() if p is not None}
    broker.mark(str(replay.index[end]), last_prices, dd_halt=CIRCUIT_BREAKER_DD,
                cooldown=CIRCUIT_BREAKER_COOLDOWN)

    bpy = market.BARS_PER_YEAR.get(genome.bar_interval, 365.25)
    stats = broker.stats(bars_per_year=bpy)
    bench = benchmark_buy_hold(replay, genome.universe, start, end,
                               float(bcfg.get("start_cash", 10_000.0)),
                               bars_per_year=bpy)
    return {
        "genome_version": genome.version,
        "window": {"start": str(replay.index[start]), "end": str(replay.index[end]),
                   "bars": end - start},
        "stats": stats,
        "fitness": fitness(stats),
        "benchmark": bench,
        "edge": edge_vs_benchmark(stats, bench, bars_per_year=bpy),
        "nav_history": broker.nav_history,
        "closed_trades": [asdict(t) for t in broker.closed],
        "open_positions": [{"symbol": p.symbol, "opened_ts": p.opened_ts}
                           for p in broker.positions.values() if p.is_open],
        "decision_log": council.decision_log,
        "superior_overrides": council.superior.override_count,
        "override_samples": council.superior.overrides[:20],
        "exec": {"filled": council.trader.executed, "rejected": council.trader.rejected},
    }


def block_bootstrap_resample(rets: np.ndarray, length: int, block_size: int,
                             rng: np.random.Generator) -> np.ndarray:
    """Circular moving-block bootstrap of a return series.

    Resamples `rets` into a new series of `length` bars, built from
    `block_size`-bar chunks starting at randomly chosen (circularly wrapped)
    positions in the original series. A per-bar i.i.d. resample would destroy
    the short-range autocorrelation real return series have (volatility
    clustering, multi-bar trends); sampling whole blocks instead preserves
    that local structure while still letting the *sequence of blocks* vary.
    Standard technique for bootstrapping a Sharpe/Sortino-style ratio's
    sampling distribution from one observed path.

    `block_size` is clamped to `[1, len(rets)]` so a too-large request
    degenerates to "one block, still random start" rather than raising.
    """
    n = len(rets)
    if n == 0:
        return rets.copy()
    block_size = max(1, min(block_size, n))
    n_blocks = math.ceil(length / block_size)
    starts = rng.integers(0, n, size=n_blocks)
    chunks = [rets[(s + np.arange(block_size)) % n] for s in starts]
    return np.concatenate(chunks)[:length]


def stats_from_returns(rets: np.ndarray, trades: int, turnover_annual: float,
                       bars_per_year: float) -> dict[str, Any]:
    """The return-derived subset of `core.portfolio.PaperBroker.stats()`,
    computed from a bare return series instead of a live broker.

    Deliberately duplicates that method's formulas (total_return, cagr, vol,
    sharpe, sortino, max_dd) rather than importing them, because
    `PaperBroker.stats()` reads `self.closed`/`self.fills` for the
    trade-derived fields (trades, win_rate, turnover, ...) that a bootstrap
    resample of *returns* has no way to regenerate -- reordering bars doesn't
    tell you which trades would have fired in that order. `trades` and
    `turnover_annual` are passed through unchanged from the real backtest
    instead: this function only asks "how much does the *return path*, on
    its own, move the return-derived half of fitness". Verified to reproduce
    `PaperBroker.stats()` exactly when fed that broker's own realized returns
    unshuffled (`tests/test_bootstrap_holdout_noise.py`).
    """
    nav = np.concatenate([[1.0], np.cumprod(1.0 + rets)])
    if len(nav) < 3:
        return {"error": "insufficient history", "trades": trades}
    total = nav[-1] / nav[0] - 1
    yrs = max(len(nav) / bars_per_year, 1e-6)
    cagr = (nav[-1] / nav[0]) ** (1 / yrs) - 1 if nav[0] > 0 else 0.0
    vol = float(np.std(rets, ddof=1)) * math.sqrt(bars_per_year) if len(rets) > 2 else 0.0
    downside = rets[rets < 0]
    dd_dev = float(np.std(downside, ddof=1)) * math.sqrt(bars_per_year) if len(downside) > 2 else 0.0
    sharpe = float(np.mean(rets)) * bars_per_year / vol if vol > 1e-9 else 0.0
    sortino = float(np.mean(rets)) * bars_per_year / dd_dev if dd_dev > 1e-9 else 0.0
    peaks = np.maximum.accumulate(nav)
    max_dd = float(np.min(nav / np.maximum(peaks, 1e-9) - 1))
    return {
        "total_return": float(total), "cagr": float(cagr), "vol": vol,
        "sharpe": sharpe, "sortino": sortino, "max_dd": max_dd,
        "bars": len(nav), "trades": trades, "turnover_annual": turnover_annual,
    }


def bootstrap_fitness_distribution(nav_history: list[tuple[str, float]], trades: int,
                                   turnover_annual: float, bars_per_year: float,
                                   n_boot: int = 1000, block_size: int = 10,
                                   seed: int = 0) -> dict[str, Any]:
    """How noisy is a single sealed-holdout fitness score, just from the
    order returns happened to arrive in?

    `constitution.holdout_accepts()`'s own docstring says the margin it
    applies "is a floor, not a calibration... Measure the sigma before
    trusting the number" -- this is that measurement. Block-bootstraps the
    observed holdout-window return path `n_boot` times (see
    `block_bootstrap_resample`), recomputes the return-derived stats and
    `constitution.fitness()` for each resample via `stats_from_returns`
    (holding `trades`/`turnover_annual` fixed at the real backtest's own
    values -- see that function's docstring for why), and reports the
    resulting distribution. `boot_fitness_std` is the empirical sigma to
    compare against `constitution.MULTIPLE_TESTING_SIGMA` (0.08): if the
    empirical sigma is meaningfully larger, the sealed-holdout margin is
    tuned too tight for how noisy a short holdout window actually is, and a
    "beats the champion" verdict from `holdout_accepts()` is less trustworthy
    than the margin implies.

    Read-only and genome-independent in itself -- takes an already-computed
    `nav_history` from one real `run_backtest()` call, never runs a genome or
    touches `live_state.json`. `seed` is fixed by default for a reproducible
    report; pass a different one to sanity-check the result isn't a seed
    artifact.
    """
    nav = np.array([v for _, v in nav_history], dtype=float)
    if len(nav) < 3:
        return {"error": "insufficient nav history"}
    rets = np.diff(nav) / np.maximum(nav[:-1], 1e-9)
    real_stats = stats_from_returns(rets, trades, turnover_annual, bars_per_year)
    real_fitness = fitness(real_stats)

    rng = np.random.default_rng(seed)
    bs = max(1, min(block_size, len(rets)))
    fits, sortinos, maxdds, tot_rets = [], [], [], []
    for _ in range(n_boot):
        sample = block_bootstrap_resample(rets, len(rets), bs, rng)
        st = stats_from_returns(sample, trades, turnover_annual, bars_per_year)
        fits.append(fitness(st))
        sortinos.append(st.get("sortino", 0.0))
        maxdds.append(st.get("max_dd", 0.0))
        tot_rets.append(st.get("total_return", 0.0))

    fits_arr = np.array(fits)
    finite = fits_arr[np.isfinite(fits_arr)]
    return {
        "n_boot": n_boot, "block_size": bs, "bars": len(rets),
        "real_fitness": real_fitness,
        "real_sortino": real_stats.get("sortino", 0.0),
        "real_max_dd": real_stats.get("max_dd", 0.0),
        "real_total_return": real_stats.get("total_return", 0.0),
        "boot_fitness_mean": float(np.mean(finite)) if len(finite) else float("-inf"),
        "boot_fitness_std": float(np.std(finite, ddof=1)) if len(finite) > 2 else 0.0,
        "boot_fitness_p05": float(np.percentile(finite, 5)) if len(finite) else float("-inf"),
        "boot_fitness_p95": float(np.percentile(finite, 95)) if len(finite) else float("-inf"),
        "frac_hard_fail": float(np.mean(~np.isfinite(fits_arr))),
        "sortino_std": float(np.std(sortinos, ddof=1)) if len(sortinos) > 2 else 0.0,
        "total_return_std": float(np.std(tot_rets, ddof=1)) if len(tot_rets) > 2 else 0.0,
        "max_dd_p05": float(np.percentile(maxdds, 5)) if maxdds else 0.0,
        "max_dd_p95": float(np.percentile(maxdds, 95)) if maxdds else 0.0,
    }
