# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Generate slides/metr.html directly from assets/crete-capabilities/benchmark_results_1_1.yaml."""
import math
from datetime import datetime
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "assets" / "crete-capabilities" / "benchmark_results_1_1.yaml"
OUT_SLIDE = Path(__file__).resolve().parent / "slides" / "metr.html"

raw = yaml.safe_load(YAML_PATH.read_text())
results = raw["results"]

# Plot coordinates in a 1080 x 720 SVG (sits inside 60% column = ~1000 px wide, so viewBox ~= px!)
W, H = 1080, 720
L, R, T, B = 195, 920, 120, 625

t_start = datetime(2024, 1, 1).timestamp()
t_end = datetime(2026, 10, 1).timestamp()
y_min, y_max = 1.0, 2880.0  # minutes (1 min to 2 days)


def sx(date_str: str) -> float:
    ts = datetime.strptime(str(date_str), "%Y-%m-%d").timestamp()
    return L + (ts - t_start) / (t_end - t_start) * (R - L)


def sy(minutes: float) -> float:
    m = max(minutes, y_min)
    return B - (math.log(m) - math.log(y_min)) / (math.log(y_max) - math.log(y_min)) * (B - T)


def wall_y(minutes: float) -> float:
    return 100.0 - math.log(minutes / 2880.0) / math.log(6.0) * 65.0


parts = []
# Grid and y-axis ticks
for val, lbl in [(1, "1 min"), (15, "15 min"), (60, "1 h"), (480, "8 h"), (2880, "2 d")]:
    yy = sy(val)
    parts.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{R}" y2="{yy:.1f}" class="stroke-rule" stroke-width="1.2"></line>')
    parts.append(f'<text x="{L - 16}" y="{yy + 12:.1f}" text-anchor="end" font-size="38" class="fill-muted">{lbl}</text>')

# Axes
parts.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{B}" class="stroke-ink" stroke-width="2"></line>')
parts.append(f'<line x1="{L}" y1="{B}" x2="{R}" y2="{B}" class="stroke-ink" stroke-width="2"></line>')
parts.append(f'<text transform="translate(46 {(T + B) / 2:.1f}) rotate(-90)" text-anchor="middle" font-size="38" class="fill-ink">Human duration (50% success)</text>')

# X-axis year ticks
for yr in (2024, 2025, 2026):
    xx = sx(f"{yr}-01-01")
    parts.append(f'<line x1="{xx:.1f}" y1="{B}" x2="{xx:.1f}" y2="{B + 10}" class="stroke-ink" stroke-width="1.8"></line>')
    parts.append(f'<text x="{xx:.1f}" y="{B + 46}" text-anchor="middle" font-size="38" class="fill-muted">{yr}</text>')
parts.append(f'<text x="{(L + R) / 2:.1f}" y="{B + 88}" text-anchor="middle" font-size="38" class="fill-muted">Model release date</text>')

# Example tasks (METR reference durations)
for mins, label in [(240.0, "Train robust model"), (877.2, "Fix ML bug")]:
    yy = sy(mins)
    parts.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{L + 16}" y2="{yy:.1f}" class="stroke-muted" stroke-width="1.5"></line>')
    parts.append(f'<text x="{L + 24}" y="{yy + 12:.1f}" font-size="37" font-style="italic" class="fill-muted">{label}</text>')

# Plot METR TH 1.1 points
named = {
    "claude_3_7_sonnet_inspect": ("Sonnet 3.7", -16, -26, "end"),
    "claude_mythos_preview_early_inspect": ("Mythos (saturates)", -24, -18, "end"),
}
for mid, entry in results.items():
    dstr = str(entry["release_date"])
    p50 = entry["metrics"]["p50_horizon_length"]
    est = float(p50["estimate"])
    lo = float(p50["ci_low"])
    hi = float(p50["ci_high"])
    ts = datetime.strptime(dstr, "%Y-%m-%d").timestamp()
    if est < y_min or ts < t_start or ts > t_end:
        continue
    xx = sx(dstr)
    yy = sy(est)
    ylo = sy(max(lo, y_min))
    yhi = sy(min(hi, y_max))
    cls_s = "stroke-ochre" if "mythos" in mid else "stroke-accent"
    cls_f = "fill-ochre" if "mythos" in mid else "fill-accent"
    parts.append(f'<line x1="{xx:.1f}" y1="{ylo:.1f}" x2="{xx:.1f}" y2="{yhi:.1f}" class="{cls_s}" stroke-width="2.4" opacity="0.55"></line>')
    if hi > y_max:
        parts.append(f'<path d="M {xx - 6:.1f} {T + 10} L {xx:.1f} {T} L {xx + 6:.1f} {T + 10}" class="fill-none {cls_s}" stroke-width="2"></path>')
    parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="8" class="{cls_f}"></circle>')
    if mid in named:
        lbl, dx, dy, anc = named[mid]
        tcls = "fill-ink" if "mythos" in mid else cls_f
        parts.append(f'<text x="{xx + dx:.1f}" y="{yy + dy:.1f}" text-anchor="{anc}" font-size="37" class="{tcls}">{lbl}</text>')

# Fragment: upper-right agent wall-time axis + Navier-Stokes & Hugging Face diamonds
cases = [
    f'<g class="fragment" data-fragment-index="0">',
    f'<line x1="{R}" y1="{wall_y(17280):.1f}" x2="{R}" y2="{wall_y(2880):.1f}" class="stroke-teal" stroke-width="2"></line>',
    f'<line x1="{R}" y1="{wall_y(2880):.1f}" x2="{R + 10}" y2="{wall_y(2880):.1f}" class="stroke-teal" stroke-width="2"></line>',
    f'<text x="{R + 16}" y="{wall_y(2880) + 12:.1f}" font-size="37" class="fill-teal">2 d</text>',
    f'<line x1="{R}" y1="{wall_y(17280):.1f}" x2="{R + 10}" y2="{wall_y(17280):.1f}" class="stroke-teal" stroke-width="2"></line>',
    f'<text x="{R + 16}" y="{wall_y(17280) + 12:.1f}" font-size="37" class="fill-teal">12 d</text>',
    f'<text x="{R + 14}" y="{wall_y(17280) - 24:.1f}" font-size="36" class="fill-teal">Wall time</text>',
]
for dstr, mins, lbl, dy in [
    ("2026-07-13", 107.77 * 60, "Hugging Face · 108 h", -20),
    ("2026-09-05", 88.0 * 60, "Navier–Stokes · 88 h", 38),
]:
    xx = sx(dstr)
    yy = wall_y(mins)
    cases.append(f'<path d="M {xx:.1f} {yy - 9:.1f} L {xx + 9:.1f} {yy:.1f} L {xx:.1f} {yy + 9:.1f} L {xx - 9:.1f} {yy:.1f} Z" class="fill-ground stroke-teal" stroke-width="3"></path>')
    cases.append(f'<text x="{xx - 16:.1f}" y="{yy + dy:.1f}" text-anchor="end" font-size="37" class="fill-teal">{lbl}</text>')
cases.append("</g>")

svg_body = "\n      ".join(parts + cases)

html = f"""<section data-layout="figure-text" data-split="60">
  <h2>Capabilities scale with task horizon and coordination</h2>
  <figure>
    <svg viewBox="0 0 {W} {H}" role="img" aria-label="METR 50%-success human-expert task durations by model release date from 2024 to 2026, with Navier-Stokes and Hugging Face multi-agent wall-time demonstrations at upper right">
      {svg_body}
    </svg>
    <span class="source">METR Time Horizons v1.1; OpenAI; Hugging Face.</span>
  </figure>
  <div class="text">
    <p class="kicker">Beyond single agents</p>
    <ul>
      <li><strong>Single-agent horizon</strong> grew from minutes to hours on software and ML tasks</li>
      <li class="fragment" data-fragment-index="0"><strong>Navier–Stokes:</strong> ~10,000 concurrent agents, 88 h wall time (≈ 880k agent-hours)</li>
      <li class="fragment" data-fragment-index="0"><strong>Hugging Face:</strong> ~700 attack participants across 108 h recovered campaign</li>
    </ul>
  </div>
  <aside class="notes">
    <ul class="skim">
      <li><strong>Left axis</strong> — METR Time Horizons v1.1: the human-expert duration of software, ML and cybersecurity tasks that a single agent completes at 50% reliability (not agent wall-clock runtime). Doubling time from 2023 onward is 128.7 days (CI 104–158 d), excluding points above 16 hours where the suite saturates.</li>
      <li><strong>Upper-right axis</strong> — agent wall-clock time for two coordinated multi-agent demonstrations, explicitly separate from METR's single-agent human-time metric: Navier–Stokes (88 h with ~10,000 concurrent agents; 88 × 10,000 = 880,000 is a constant-concurrency illustration) and the Hugging Face intrusion (107.77 h recovered campaign, ~700 participants).</li>
      <li><strong>Bridge</strong> — individual horizons are already hours long; the frontier now also includes coordinated swarms.</li>
    </ul>
    <details><summary>Sources</summary>
      <p>METR Time Horizons v1.1 YAML (downloaded 12 Sep 2026, doubling time from 2023 on: 128.744 d, CI 104.428–158.012 d), <a href="https://metr.org/time-horizons/">metr.org/time-horizons</a>. OpenAI, <a href="https://openai.com/index/navier-stokes-solution/">Navier–Stokes solution</a> (88 h, ~10,000 concurrent agents, 17 h Lean formalization). Hugging Face, <a href="https://huggingface.co/blog/agent-intrusion-technical-timeline">Agent intrusion technical timeline</a>; METR, <a href="https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/">investigation</a>.</p>
    </details>
  </aside>
</section>
"""

OUT_SLIDE.write_text(html)
print(f"Wrote {OUT_SLIDE} ({len(html)} bytes)")
