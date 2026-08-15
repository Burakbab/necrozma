#!/usr/bin/env python3
"""Build the EvoTrader dashboard — one self-contained HTML file.
 
Shows what the system is actually doing right now: the live paper account, the
book, what each agent argued for on the last bar, and the genome's lineage.
Hand-rolled SVG so the page has zero external dependencies and renders the
same everywhere.
"""
from __future__ import annotations
 
import html
import json
import os
from datetime import datetime, timezone
 
ROOT = os.path.dirname(os.path.abspath(__file__))
 
# Path overrides so the dashboard can be rebuilt in a bare container that only
# has the state JSON — no repo checkout required.
P_LIVE = os.environ.get("EVO_STATE", os.path.join(ROOT, "state", "live", "account.json"))
P_BT = os.environ.get("EVO_BACKTEST", os.path.join(ROOT, "reports", "backtest.json"))
P_LIN = os.environ.get("EVO_LINEAGE", os.path.join(ROOT, "state", "lineage.jsonl"))
P_CHAMP = os.environ.get("EVO_CHAMPION", os.path.join(ROOT, "state", "genomes", "champion.json"))
# index.html at the repo root, so GitHub Pages can serve it as-is with no build
# step and no branch juggling.
P_OUT = os.environ.get("EVO_DASHBOARD", os.path.join(ROOT, "index.html"))
 
# One palette, used consistently: teal = the system, amber = benchmark,
# red/green reserved exclusively for money outcomes so they always mean the
# same thing wherever they appear.
C = {
    "bg": "#0f1216", "panel": "#161b22", "line": "#242c37",
    "text": "#e6edf3", "dim": "#8b949e", "faint": "#5a6472",
    "accent": "#2dd4bf", "accent2": "#f0b429",
    "up": "#3fb950", "down": "#f85149", "violet": "#a78bfa",
}
 
 
def _read(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return default
 
 
def _readl(path):
    out = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    except Exception:  # noqa: BLE001
        pass
    return out
 
 
def sparkline(values, w=760, h=180, color=None, baseline=None, label=""):
    """A line chart with an explicit zero/start reference — a NAV chart without
    the starting line is a chart you can't read."""
    color = color or C["accent"]
    if not values or len(values) < 2:
        return (f'<div class="empty">not enough data yet — {html.escape(label)}</div>')
    lo, hi = min(values), max(values)
    if baseline is not None:
        lo, hi = min(lo, baseline), max(hi, baseline)
    pad = (hi - lo) * 0.12 or (abs(hi) * 0.02 or 1)
    lo, hi = lo - pad, hi + pad
    n = len(values)
 
    def X(i):
        return 44 + (w - 60) * (i / max(n - 1, 1))
 
    def Y(v):
        return h - 26 - (h - 46) * ((v - lo) / (hi - lo or 1))
 
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(values))
    area = f"{X(0):.1f},{h - 26} " + pts + f" {X(n - 1):.1f},{h - 26}"
    base_line = ""
    if baseline is not None:
        by = Y(baseline)
        base_line = (f'<line x1="44" y1="{by:.1f}" x2="{w - 16}" y2="{by:.1f}" '
                     f'stroke="{C["faint"]}" stroke-width="1" stroke-dasharray="3 4"/>'
                     f'<text x="{w - 14}" y="{by + 3:.1f}" fill="{C["faint"]}" '
                     f'font-size="10" text-anchor="end">start</text>')
    grid = ""
    for frac in (0.0, 0.5, 1.0):
        v = lo + (hi - lo) * frac
        y = Y(v)
        grid += (f'<line x1="44" y1="{y:.1f}" x2="{w - 16}" y2="{y:.1f}" '
                 f'stroke="{C["line"]}" stroke-width="1"/>'
                 f'<text x="38" y="{y + 3:.1f}" fill="{C["faint"]}" font-size="10" '
                 f'text-anchor="end">{v:,.0f}</text>')
    return f'''<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" role="img"
      aria-label="{html.escape(label)}"><defs><linearGradient id="g{abs(hash(label)) % 9999}"
      x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{color}" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>
      {grid}{base_line}
      <polygon points="{area}" fill="url(#g{abs(hash(label)) % 9999})"/>
      <polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"
        stroke-linejoin="round" stroke-linecap="round"/></svg>'''
 
 
def stat(label, value, sub="", tone=""):
    color = {"up": C["up"], "down": C["down"]}.get(tone, C["text"])
    return f'''<div class="stat"><div class="stat-l">{html.escape(label)}</div>
      <div class="stat-v" style="color:{color}">{value}</div>
      <div class="stat-s">{sub}</div></div>'''
 
 
def build(out_path: str | None = None) -> str:
    out_path = out_path or P_OUT
    live = _read(P_LIVE, {}) or {}
    bt = _read(P_BT, {}) or {}
    # Lineage lives in two places: the local jsonl a run appends to, and the
    # live state blob that survives the container. Merge, keeping order and
    # dropping exact duplicates — otherwise a promotion made in a previous
    # container silently vanishes from the history.
    lineage = []
    _seen = set()
    for rec in (live.get("lineage") or []) + _readl(P_LIN):
        k = json.dumps(rec, sort_keys=True, default=str)[:400]
        if k in _seen:
            continue
        _seen.add(k)
        lineage.append(rec)
    champ = _read(P_CHAMP, {}) or live.get("genome", {}) or {}
 
    broker = live.get("broker", {})
    nav_hist = broker.get("nav_history", [])
    navs = [float(v) for _, v in nav_hist] if nav_hist else []
    start_cash = float(broker.get("start_cash", 10_000))
    nav_now = navs[-1] if navs else start_cash
    ret = nav_now / start_cash - 1
    journal = live.get("journal", [])
    ticks = live.get("ticks", 0)
    started = str(live.get("started", ""))[:10]
 
    # ---- header stats
    closed = broker.get("closed", [])
    wins = [t for t in closed if t.get("pnl", 0) > 0]
    stats_html = "".join([
        stat("live NAV", f"${nav_now:,.2f}", f"started ${start_cash:,.0f} on {started}",
             "up" if ret >= 0 else "down"),
        stat("since inception", f"{ret:+.2%}", f"{ticks} trading day(s)",
             "up" if ret >= 0 else "down"),
        stat("cash", f"${float(broker.get('cash', 0)):,.0f}",
             f"{float(broker.get('cash', 0)) / max(nav_now, 1):.0%} of book"),
        stat("closed trades", f"{len(closed)}",
             f"{len(wins) / len(closed):.0%} winners" if closed else "none yet"),
        stat("genome", f"v{champ.get('version', 1)}",
             f"{len(lineage)} generation(s) run"),
    ])
 
    # ---- live NAV chart
    nav_chart = sparkline(navs, baseline=start_cash, label="live paper NAV")
 
    # ---- the book
    positions = broker.get("positions", {})
    last = journal[-1] if journal else {}
    mkt = (last.get("positions") or {})
    rows = ""
    for sym, p in positions.items():
        val = mkt.get(sym, p.get("qty", 0) * p.get("avg_cost", 0))
        pnl = (val / (p["qty"] * p["avg_cost"]) - 1) if p.get("qty") and p.get("avg_cost") else 0
        rows += f'''<tr><td class="sym">{html.escape(sym)}</td>
          <td>${val:,.0f}</td><td>{val / max(nav_now, 1):.1%}</td>
          <td style="color:{C['up'] if pnl >= 0 else C['down']}">{pnl:+.2%}</td>
          <td>{p.get('bars_held', 0)}d</td>
          <td class="dim">{html.escape(', '.join(x.replace('consult_', '') for x in p.get('entry_agents', [])) or '—')}</td></tr>'''
    book = (f'<table><thead><tr><th>symbol</th><th>value</th><th>weight</th>'
            f'<th>P&amp;L</th><th>held</th><th>bought on the advice of</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>') if rows else '<div class="empty">all cash</div>'
 
    # ---- what the council said on the last bar
    dec = (last.get("decision") or {})
    council = ""
    if dec:
        for agent, intents in (dec.get("proposals") or {}).items():
            chips = "".join(
                f'<span class="chip {"buy" if i["side"] == "buy" else "sell"}">'
                f'{html.escape(i["symbol"].replace("USDT", ""))} '
                f'<b>{i["side"]}</b> {i["conviction"]:.2f}</span>'
                for i in intents[:8]) or '<span class="chip none">no view</span>'
            council += (f'<div class="agent"><div class="agent-n">'
                        f'{html.escape(agent.replace("consult_", ""))}</div>'
                        f'<div class="chips">{chips}</div></div>')
        vet = (dec.get("vetoes") or [])[:6]
        if vet:
            council += ('<div class="agent"><div class="agent-n judge">judges vetoed</div>'
                        '<div class="chips">' + "".join(
                            f'<span class="chip veto">{html.escape(v["symbol"].replace("USDT", ""))} '
                            f'— {html.escape(v["reason"])}</span>' for v in vet) + '</div></div>')
        fl = dec.get("fills") or []
        if fl:
            council += ('<div class="agent"><div class="agent-n exec">executed</div>'
                        '<div class="chips">' + "".join(
                            f'<span class="chip {"buy" if f["side"] == "buy" else "sell"}">'
                            f'{html.escape(f["symbol"].replace("USDT", ""))} {f["side"]} '
                            f'({f["status"]})</span>' for f in fl) + '</div></div>')
        council = (f'<div class="regime">market read: <b>{html.escape(str(dec.get("regime")))}</b> '
                   f'· breadth {dec.get("breadth", 0):.0%} · '
                   f'bar {html.escape(str(last.get("bar", ""))[:10])}</div>' + council)
    else:
        council = '<div class="empty">no decision recorded yet</div>'
 
    # ---- evolution lineage
    lin = ""
    for i, gen in enumerate(lineage):
        acc = gen.get("accepted")
        if acc:
            lin += f'''<div class="gen accepted"><div class="gen-h">
              <span class="badge ok">v{acc['new_version']} promoted</span>
              <span class="gen-f">fitness {acc['was']} → {acc['fitness']}</span></div>
              <div class="gen-b">{html.escape(acc['hypothesis'])}</div>
              <div class="gen-p">{html.escape(json.dumps(acc['patch']))}</div></div>'''
        else:
            rej = (gen.get("rejections") or [{}])[0]
            top = (gen.get("top") or [{}])[0]
            lin += f'''<div class="gen"><div class="gen-h">
              <span class="badge no">champion held</span>
              <span class="gen-f">{gen.get('n_candidates', 0)} candidates tested</span></div>
              <div class="gen-b">best idea: {html.escape(str(top.get('hypothesis', '—')))}</div>
              <div class="gen-p">rejected: {html.escape(str(rej.get('why', 'did not clear the bar')))}</div></div>'''
    lin = lin or '<div class="empty">no generations run yet</div>'
 
    # ---- backtest panel
    bt_html = ""
    for label, r in bt.items():
        if not isinstance(r, dict) or "stats" not in r:
            continue
        s, bm = r["stats"], r.get("benchmark", {})
        bt_html += f'''<div class="bt"><div class="bt-l">{html.escape(label)}</div>
          <div class="bt-r"><span>return <b style="color:{C['up'] if s.get('total_return', 0) >= 0 else C['down']}">
          {s.get('total_return', 0):+.1%}</b></span>
          <span>sortino <b>{s.get('sortino', 0):.2f}</b></span>
          <span>maxDD <b>{s.get('max_dd', 0):.1%}</b></span>
          <span>trades <b>{s.get('trades', 0)}</b></span>
          <span class="dim">buy&amp;hold {bm.get('total_return', 0):+.1%}</span></div></div>'''
    bt_html = bt_html or '<div class="empty">no backtest report yet</div>'
 
    gen_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
 
    doc = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EvoTrader — a trading system that rewrites itself</title>
<meta name="description" content="Live record of a self-improving paper-trading
system: what it owns, how it decided, and every attempt it has made to rewrite
its own rules. Imaginary money, real prices.">
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:{C['bg']};color:{C['text']};
 font:14px/1.55 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;
 -webkit-font-smoothing:antialiased}}
.wrap{{max-width:1080px;margin:0 auto;padding:28px 20px 64px}}
h1{{font-size:22px;margin:0 0 2px;letter-spacing:-.01em}}
.sub{{color:{C['dim']};font-size:13px;margin-bottom:22px}}
.panel{{background:{C['panel']};border:1px solid {C['line']};border-radius:12px;
 padding:18px 20px;margin-bottom:16px}}
h2{{font-size:12px;text-transform:uppercase;letter-spacing:.09em;color:{C['dim']};
 margin:0 0 14px;font-weight:600}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:2px;
 background:{C['line']};border:1px solid {C['line']};border-radius:12px;overflow:hidden;
 margin-bottom:16px}}
.stat{{background:{C['panel']};padding:15px 18px}}
.stat-l{{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:{C['dim']}}}
.stat-v{{font-size:22px;font-weight:650;margin:3px 0 1px;letter-spacing:-.02em;
 font-variant-numeric:tabular-nums}}
.stat-s{{font-size:11.5px;color:{C['faint']}}}
table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}}
th{{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;
 color:{C['faint']};font-weight:600;padding:0 10px 8px 0;border-bottom:1px solid {C['line']}}}
td{{padding:9px 10px 9px 0;border-bottom:1px solid {C['line']};font-size:13px}}
tr:last-child td{{border-bottom:0}}
.sym{{font-weight:600}}
.dim{{color:{C['dim']}}}
.empty{{color:{C['faint']};font-size:13px;padding:14px 0;font-style:italic}}
.regime{{color:{C['dim']};font-size:12.5px;margin-bottom:14px;padding-bottom:12px;
 border-bottom:1px solid {C['line']}}}
.regime b{{color:{C['accent']}}}
.agent{{display:flex;gap:14px;padding:9px 0;align-items:flex-start;
 border-bottom:1px solid {C['line']}}}
.agent:last-child{{border-bottom:0}}
.agent-n{{min-width:118px;font-size:12px;color:{C['dim']};padding-top:3px;font-weight:600}}
.agent-n.judge{{color:{C['accent2']}}} .agent-n.exec{{color:{C['accent']}}}
.chips{{display:flex;flex-wrap:wrap;gap:6px}}
.chip{{font-size:11.5px;padding:3px 9px;border-radius:20px;border:1px solid {C['line']};
 background:{C['bg']};color:{C['dim']}}}
.chip b{{font-weight:600}}
.chip.buy{{color:{C['up']};border-color:#1d3b26}}
.chip.sell{{color:{C['accent2']};border-color:#3d3520}}
.chip.veto{{color:{C['faint']}}}
.chip.none{{font-style:italic;color:{C['faint']}}}
.gen{{padding:11px 0;border-bottom:1px solid {C['line']}}}
.gen:last-child{{border-bottom:0}}
.gen-h{{display:flex;gap:10px;align-items:center;margin-bottom:4px}}
.badge{{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;padding:2px 8px;
 border-radius:5px;font-weight:650}}
.badge.ok{{background:#10291a;color:{C['up']}}}
.badge.no{{background:#232830;color:{C['dim']}}}
.gen-f{{font-size:11.5px;color:{C['faint']};font-variant-numeric:tabular-nums}}
.gen-b{{font-size:13px}}
.gen-p{{font-size:11.5px;color:{C['faint']};font-family:ui-monospace,monospace;
 margin-top:3px;word-break:break-all}}
.bt{{display:flex;justify-content:space-between;align-items:center;gap:16px;
 padding:10px 0;border-bottom:1px solid {C['line']};flex-wrap:wrap}}
.bt:last-child{{border-bottom:0}}
.bt-l{{font-weight:600;font-size:13px}}
.bt-r{{display:flex;gap:16px;font-size:12px;color:{C['dim']};flex-wrap:wrap;
 font-variant-numeric:tabular-nums}}
.bt-r b{{color:{C['text']};font-weight:600}}
.note{{font-size:12.5px;color:{C['dim']};line-height:1.65}}
.note b{{color:{C['text']}}}
footer{{color:{C['faint']};font-size:11.5px;margin-top:26px;text-align:center}}
.paper{{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.08em;
 text-transform:uppercase;color:{C['accent2']};background:#3d3520;border:1px solid #5c4d24;
 padding:3px 10px;border-radius:20px;vertical-align:middle;margin-left:10px}}
.hero{{background:{C['panel']};border:1px solid {C['line']};border-left:3px solid {C['accent']};
 border-radius:12px;padding:18px 22px;margin-bottom:16px}}
.hero p{{margin:0 0 10px;font-size:14px;color:{C['text']};line-height:1.7}}
.hero p:last-child{{margin-bottom:0}}
.hero .q{{font-weight:650;color:{C['accent']};font-size:13px;text-transform:uppercase;
 letter-spacing:.06em;margin-bottom:6px}}
.h2sub{{font-size:12.5px;color:{C['dim']};margin:-8px 0 14px;line-height:1.6;
 text-transform:none;letter-spacing:0;font-weight:400}}
.gloss{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px 26px}}
.g-t{{font-weight:650;font-size:13px;color:{C['text']};margin-bottom:2px}}
.g-d{{font-size:12.5px;color:{C['dim']};line-height:1.6}}
</style></head><body><div class="wrap">
<h1>EvoTrader <span class="paper">paper money · not real</span></h1>
<div class="sub">a trading system that rewrites itself · updated {gen_time}</div>

<div class="hero">
<div class="q">What am I looking at?</div>
<p>A trading system that runs itself. Once a day it looks at real crypto prices,
argues with itself about what to buy, places the trades, and writes down what it
did. Nobody presses any buttons.</p>
<p>The unusual part is the second loop: it also tries to <b>improve its own
trading rules</b>. It proposes a tweak to itself, tests that tweak on years of
past data it wasn't tuned on, and only adopts it if the result clears a
statistical bar it is not allowed to move. Everything below is the live record of
that process — including the parts where it loses money.</p>
<p><b>No real money is involved.</b> The prices are real and every fee is charged,
but the account is imaginary.</p>
</div>

<div class="stats">{stats_html}</div>

<div class="panel"><h2>The account over time</h2>
<div class="h2sub">What the imaginary $10,000 is worth now. The dashed line is where
it started — above it means up, below means down.</div>{nav_chart}</div>

<div class="panel"><h2>What it currently owns</h2>
<div class="h2sub">Each row is one holding: how much it's worth, what share of the
account it is, and whether it's up or down since it was bought. The last column
names which of the internal advisors argued for buying it.</div>{book}</div>

<div class="panel"><h2>How today's decision was made</h2>
<div class="h2sub">The system runs as a committee. Three advisors with genuinely
different theories of the market each propose trades and how strongly they believe
in them; two judges can shrink or veto anything; then a trader executes whatever
survives. This is that argument, verbatim.</div>{council}</div>

<div class="panel"><h2>Attempts to improve itself</h2>
<div class="h2sub">Each entry is one round of self-improvement. "Champion held"
means it tried a batch of ideas and none of them were good enough to adopt —
which is the normal, healthy outcome. "Promoted" means one cleared the bar.</div>
{lin}</div>

<div class="panel"><h2>How the current rules did on past data</h2>
<div class="h2sub">A replay of the current ruleset over history. Treat these
numbers with suspicion — see the caveats at the bottom.</div>{bt_html}</div>

<div class="panel"><h2>Jargon, translated</h2>
<div class="gloss">
<div><div class="g-t">Paper trading</div><div class="g-d">Trading with fake money at
real prices. A flight simulator for a strategy.</div></div>
<div><div class="g-t">Genome</div><div class="g-d">The system's rulebook — every
number it's allowed to change about how it trades. "v2" is the second version it
has written for itself.</div></div>
<div><div class="g-t">Backtest</div><div class="g-d">Replaying a strategy over past
data to see how it would have done. Easy to fool yourself with.</div></div>
<div><div class="g-t">Holdout</div><div class="g-d">A slice of history deliberately
hidden from the tuning process, used once at the end. It's the difference between
a real exam and one where you saw the answers.</div></div>
<div><div class="g-t">Drawdown</div><div class="g-d">The worst peak-to-trough fall.
"−24%" means that at some point the account was down 24% from its high.</div></div>
<div><div class="g-t">Sortino</div><div class="g-d">Return earned per unit of
<em>downside</em> risk. Higher is better; below zero means it lost money.</div></div>
<div><div class="g-t">Buy &amp; hold</div><div class="g-d">The do-nothing benchmark:
just buy and sit. Beating it is the whole job.</div></div>
<div><div class="g-t">Conviction</div><div class="g-d">How strongly an advisor
believes its own suggestion, from 0 to 1. Used to size the trade.</div></div>
<div><div class="g-t">Breadth</div><div class="g-d">The share of tracked coins
currently trending up — a rough read on whether the whole market is rising.</div></div>
<div><div class="g-t">Veto</div><div class="g-d">A judge blocking a trade outright,
usually for being too risky or too similar to something already held.</div></div>
<div><div class="g-t">Market read</div><div class="g-d">The system's one-word summary
of conditions — <em>bull</em> (rising), <em>bear</em> (falling), or <em>chop</em>
(going sideways, the hardest to trade). It sizes trades differently in each.</div></div>
<div><div class="g-t">Fitness</div><div class="g-d">The single score used to judge a
proposed rule change, blending return, risk and consistency. A new version is only
adopted if it beats the current one by more than luck would explain.</div></div>
</div></div>

<div class="panel"><h2>Honest caveats</h2>
<div class="note">
This is <b>paper money</b>. Every price is real and every fee and slippage cost is
charged, but no capital is at risk.<br><br>
The "past data" numbers above are the current ruleset replayed over history it was
partly tuned on, which flatters it. The only numbers that carry real weight are the
<b>live account</b> at the top and the <b>holdout</b> results inside the
self-improvement log — those come from data the system never saw while tuning.<br><br>
<b>It is not currently profitable.</b> So far it has lost less than the market did
over the same stretch, which is a start, not a strategy. Beating its own earlier
versions is not the same as being good — that's why the buy-and-hold comparison is
printed next to every result and can't be quietly dropped.<br><br>
Nothing here is financial advice, and the system cannot promote itself to real
money — that takes six months of evidence and a human signing off.
</div></div>

<footer>Built automatically from live_state.json ·
<a href="https://github.com/Burakbab/necrozma" style="color:{C['dim']}">source on GitHub</a></footer>
</div></body></html>'''
 
    d = os.path.dirname(out_path)
    if d:                      # bare filename -> dirname is "" -> makedirs raises
        os.makedirs(d, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(doc)
    return out_path
 
 
if __name__ == "__main__":
    p = build()
    print(f"{p}  ({os.path.getsize(p) / 1024:.1f} KB)")
 