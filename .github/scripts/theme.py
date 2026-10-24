"""Shared look for every generated SVG: follows the viewer's light/dark scheme."""
import os

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Noto Sans SC', sans-serif"

CSS = f"""
  :root {{
    --bg: #ffffff; --border: #d0d7de; --text: #1f2328; --muted: #59636e;
    --title: #0969da; --accent: #0969da; --track: #eaeef2; --tile: #f6f8fa;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #0d1117; --border: #30363d; --text: #e6edf3; --muted: #8b949e;
      --title: #58a6ff; --accent: #58a6ff; --track: #21262d; --tile: #161b22;
    }}
  }}
  .card {{ fill: var(--bg); stroke: var(--border); }}
  .t {{ font: 600 16px {FONT}; fill: var(--title); }}
  .n {{ font: 600 15px {FONT}; fill: var(--text); }}
  .l {{ font: 400 13.5px {FONT}; fill: var(--text); }}
  .v {{ font: 700 13.5px {FONT}; fill: var(--text); }}
  .m {{ font: 400 12.5px {FONT}; fill: var(--muted); }}
  .ic {{ fill: var(--accent); }}
  .track {{ fill: var(--track); }}
  .fade {{ opacity: 0; animation: fade .6s ease-out forwards; }}
  @keyframes fade {{ to {{ opacity: 1; }} }}
"""


# NOANIM=1 renders the final frame (for local previews)
STILL = ".fade, .bar { animation: none !important; opacity: 1 !important; transform: none !important; }"


def style(extra=""):
    still = STILL if os.environ.get("NOANIM") else ""
    return f"<style>{CSS}{extra}{still}</style>"
