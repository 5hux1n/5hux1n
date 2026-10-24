"""Signature business card: the name is written stroke by stroke, then a line
of live stats fades in. Follows the viewer's light/dark scheme.

Writes <OUT>/card.svg. Uses cards.fetch() for data (MOCK=1 for sample data).
"""
import json
import os
from html import escape

from cards import fetch, fmt
from theme import FONT

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
OUT = os.environ.get("OUT", "dist")

W, H = 840, 300
SIG_SCALE = 1.5
SIG_X, SIG_BASE = 64, 156        # left edge and baseline of the signature
WRITE_S = 2.6                     # seconds to write the whole name

TAGLINE = "iOS 插件 · Mac 小工具 · 网页"


def signature():
    sig = json.load(open(os.path.join(ROOT, "assets", "signature.json"), encoding="utf-8"))
    x0, _, x1, _ = sig["bbox"]
    span = x1 - x0
    parts = []
    for g in sig["glyphs"]:
        gx0, _, gx1, _ = g["bounds"]
        start = (gx0 - x0) / span * WRITE_S * 0.82
        dur = max(0.35, (gx1 - gx0) / span * WRITE_S * 1.6)
        parts.append(
            f'<path class="ink" pathLength="1" d="{g["d"]}" '
            f'style="animation-delay:{start:.2f}s,{WRITE_S * .8 + start * .3:.2f}s;'
            f'animation-duration:{dur:.2f}s,.9s"/>'
        )
    tx = SIG_X - x0 * SIG_SCALE
    width = span * SIG_SCALE
    return f'<g transform="translate({tx:.1f},{SIG_BASE}) scale({SIG_SCALE})">{"".join(parts)}</g>', width


def card(u):
    sig, sig_w = signature()
    c = u["contributionsCollection"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    stats = [
        (fmt(c["contributionCalendar"]["totalContributions"]), "次贡献"),
        (fmt(u["repositories"]["totalCount"]), "个仓库"),
        (fmt(stars), "颗星"),
    ]
    # stats as tspans so numbers can be bold
    tsp = []
    for i, (num, label) in enumerate(stats):
        if i:
            tsp.append('<tspan class="dot">  ·  </tspan>')
        tsp.append(f'<tspan class="num">{num}</tspan><tspan> {label}</tspan>')
    line_y = 202
    line_x2 = SIG_X + sig_w + 30
    after = WRITE_S + .2

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="5hux1n · {TAGLINE}">
<style>
  :root {{ --bg:#fbfaf7; --edge:#e7e3da; --ink:#1c1b19; --muted:#7a766d; --rule:#d9d4c8; --accent:#c2562e; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#111214; --edge:#26282c; --ink:#f2efe8; --muted:#8e8a82; --rule:#34363a; --accent:#ef8a5e; }}
  }}
  .bg   {{ fill: var(--bg); stroke: var(--edge); }}
  .ink  {{ fill: var(--ink); fill-opacity: 0; stroke: var(--ink); stroke-width: .9; stroke-linecap: butt; stroke-linejoin: round;
          stroke-dasharray: 1; stroke-dashoffset: 1;
          animation-name: write, fill; animation-timing-function: cubic-bezier(.45,.05,.35,1), ease-out; animation-fill-mode: forwards; }}
  @keyframes write {{ to {{ stroke-dashoffset: 0; }} }}
  @keyframes fill  {{ to {{ fill-opacity: 1; stroke-width: .2; }} }}
  .rule {{ stroke: var(--rule); stroke-width: 1; stroke-dasharray: 1; stroke-dashoffset: 1;
          animation: write .9s ease-out {after:.2f}s forwards; }}
  .tag  {{ font: 500 17px {FONT}; fill: var(--muted); letter-spacing: .5px; }}
  .st   {{ font: 400 15px {FONT}; fill: var(--muted); }}
  .num  {{ font-weight: 700; fill: var(--ink); }}
  .dot  {{ fill: var(--rule); }}
  .link {{ font: 500 14px {FONT}; fill: var(--muted); }}
  .fade {{ opacity: 0; animation: fade .8s ease-out forwards; }}
  @keyframes fade {{ to {{ opacity: 1; }} }}
{".ink,.rule,.fade{animation:none!important;stroke-dashoffset:0!important;opacity:1!important;fill-opacity:1!important;stroke-width:.2!important}.rule{stroke-width:1!important}" if os.environ.get("NOANIM") else ""}
</style>
<rect class="bg" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18"/>

{sig}

<line class="rule" pathLength="1" x1="{SIG_X}" y1="{line_y}" x2="{line_x2:.0f}" y2="{line_y}"/>

<g class="fade" style="animation-delay:{after + .3:.2f}s">
  <text x="{SIG_X}" y="{line_y + 32}" class="tag">{escape(TAGLINE)}</text>
</g>
<g class="fade" style="animation-delay:{after + .6:.2f}s">
  <text x="{SIG_X}" y="{line_y + 60}" class="st">{"".join(tsp)}</text>
</g>

<g class="fade" style="animation-delay:{after + .9:.2f}s" transform="translate({W - 64},{H - 44})">
  <text x="0" y="0" class="link" text-anchor="end">mjh.im</text>
</g>
</svg>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "card.svg"), "w", encoding="utf-8") as f:
        f.write(card(fetch()))
    print("wrote", os.path.join(OUT, "card.svg"))


if __name__ == "__main__":
    main()
