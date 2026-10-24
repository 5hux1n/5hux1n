"""Generate GitHub stats and top-language SVG cards.

Runs in GitHub Actions with GITHUB_TOKEN. Writes:
  dist/stats.svg
  dist/langs.svg
Set MOCK=1 to render with sample data locally.
"""
import json
import os
import urllib.request
from html import escape

LOGIN = os.environ.get("LOGIN", "5hux1n")
OUT = os.environ.get("OUT", "dist")

QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar { totalContributions }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""

MOCK = {
    "name": "5hux1n",
    "followers": {"totalCount": 128},
    "contributionsCollection": {
        "totalCommitContributions": 1834,
        "restrictedContributionsCount": 210,
        "totalPullRequestContributions": 42,
        "totalIssueContributions": 17,
        "contributionCalendar": {"totalContributions": 2103},
    },
    "repositories": {
        "totalCount": 29,
        "nodes": [
            {"stargazerCount": 120, "languages": {"edges": [
                {"size": 900000, "node": {"name": "Swift", "color": "#F05138"}},
                {"size": 500000, "node": {"name": "JavaScript", "color": "#f1e05a"}}]}},
            {"stargazerCount": 80, "languages": {"edges": [
                {"size": 400000, "node": {"name": "Objective-C", "color": "#438eff"}},
                {"size": 300000, "node": {"name": "Python", "color": "#3572A5"}},
                {"size": 120000, "node": {"name": "Logos", "color": "#ff0000"}},
                {"size": 90000, "node": {"name": "TypeScript", "color": "#3178c6"}},
                {"size": 60000, "node": {"name": "Shell", "color": "#89e051"}}]}},
        ],
    },
}

# Palette (dark card, reads well on both light and dark GitHub themes)
BG = "#0d1117"
BORDER = "#30363d"
TITLE = "#7ee7c7"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', 'PingFang SC', sans-serif"

# Languages that are markup/data rather than code
SKIP_LANGS = {"HTML", "CSS", "SCSS", "Makefile", "Dockerfile", "Jupyter Notebook"}


def fetch():
    if os.environ.get("MOCK"):
        return MOCK
    token = os.environ["GITHUB_TOKEN"]
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(json.dumps(data["errors"], indent=2))
    return data["data"]["user"]


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


ICONS = {
    # 16x16 octicon paths
    "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z",
    "commit": "M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "pr": "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.573.677A.25.25 0 0 1 10 .854V2.5h1A2.5 2.5 0 0 1 13.5 5v5.628a2.251 2.251 0 1 1-1.5 0V5a1 1 0 0 0-1-1h-1v1.646a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354ZM3.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm0 9.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm8.25.75a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0Z",
    "repo": "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z",
    "people": "M2 5.5a3.5 3.5 0 1 1 5.898 2.549 5.508 5.508 0 0 1 3.034 4.084.75.75 0 1 1-1.482.235 4 4 0 0 0-7.9 0 .75.75 0 0 1-1.482-.236A5.507 5.507 0 0 1 3.102 8.05 3.493 3.493 0 0 1 2 5.5ZM11 4a3.001 3.001 0 0 1 2.22 5.018 5.01 5.01 0 0 1 2.56 3.012.749.749 0 0 1-.885.954.752.752 0 0 1-.549-.514 3.507 3.507 0 0 0-2.522-2.372.75.75 0 0 1-.574-.73v-.352a.75.75 0 0 1 .416-.672A1.5 1.5 0 0 0 11 5.5.75.75 0 0 1 11 4Zm-5.5-.5a2 2 0 1 0-.001 3.999A2 2 0 0 0 5.5 3.5Z",
    "fire": "M9.533.753V.752c.217 2.385 1.463 3.626 2.653 4.81C13.37 6.74 14.498 7.863 14.498 10c0 3.5-3 6-6.5 6S1.5 13.512 1.5 10c0-1.298.536-2.56 1.425-3.286.376-.308.862 0 1.035.454C4.46 8.487 5.312 9.328 6.5 9c-1-2.5.5-6 3.033-8.247Z",
}

STYLE = f"""<style>
  .t {{ font: 600 17px {FONT}; fill: {TITLE}; }}
  .l {{ font: 400 13.5px {FONT}; fill: {TEXT}; }}
  .v {{ font: 700 13.5px {FONT}; fill: {TEXT}; }}
  .m {{ font: 400 12px {FONT}; fill: {MUTED}; }}
  .row {{ opacity: 0; animation: in .5s ease-out forwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateX(-8px); }} to {{ opacity: 1; transform: none; }} }}
  .bar {{ animation: grow 1s ease-out forwards; transform-origin: left; transform: scaleX(0); }}
  @keyframes grow {{ to {{ transform: scaleX(1); }} }}
</style>"""


def frame(w, h, title, inner):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
{STYLE}
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<text x="25" y="36" class="t">{escape(title)}</text>
{inner}
</svg>
"""


def stats_card(u):
    c = u["contributionsCollection"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    rows = [
        ("star", "Stars", stars),
        ("commit", "近一年提交", c["totalCommitContributions"] + c["restrictedContributionsCount"]),
        ("fire", "近一年贡献", c["contributionCalendar"]["totalContributions"]),
        ("pr", "Pull Requests", c["totalPullRequestContributions"]),
        ("repo", "公开仓库", u["repositories"]["totalCount"]),
        ("people", "Followers", u["followers"]["totalCount"]),
    ]
    inner = []
    for i, (icon, label, val) in enumerate(rows):
        y = 62 + i * 25
        inner.append(
            f'<g class="row" style="animation-delay:{150 + i * 120}ms" transform="translate(25,{y})">'
            f'<path d="{ICONS[icon]}" fill="{ACCENT}" transform="translate(0,-1)"/>'
            f'<text x="26" y="12.5" class="l">{label}</text>'
            f'<text x="250" y="12.5" class="v" text-anchor="end">{fmt(val)}</text></g>'
        )
    return frame(300, 220, "GitHub 数据", "\n".join(inner))


def langs_card(u, top=6):
    totals, colors = {}, {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            if name in SKIP_LANGS:
                continue
            totals[name] = totals.get(name, 0) + e["size"]
            colors[name] = e["node"]["color"] or MUTED
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:top]
    total = sum(v for _, v in ranked) or 1
    w, bar_w = 360, 310
    inner, x = [], 25.0
    # stacked progress bar
    inner.append(f'<clipPath id="r"><rect x="25" y="56" width="{bar_w}" height="9" rx="4.5"/></clipPath>')
    inner.append('<g clip-path="url(#r)" class="bar">')
    for name, size in ranked:
        seg = bar_w * size / total
        inner.append(f'<rect x="{x:.2f}" y="56" width="{seg + 0.5:.2f}" height="9" fill="{colors[name]}"/>')
        x += seg
    inner.append("</g>")
    # two-column legend
    for i, (name, size) in enumerate(ranked):
        col, row = i % 2, i // 2
        gx, gy = 25 + col * 165, 90 + row * 30
        pct = 100 * size / total
        inner.append(
            f'<g class="row" style="animation-delay:{300 + i * 120}ms" transform="translate({gx},{gy})">'
            f'<circle cx="5" cy="5" r="5" fill="{colors[name]}"/>'
            f'<text x="16" y="9.5" class="l">{escape(name)}</text>'
            f'<text x="16" y="25" class="m">{pct:.1f}%</text></g>'
        )
    return frame(w, 220, "常用语言", "\n".join(inner))


def main():
    u = fetch()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_card(u))
    with open(os.path.join(OUT, "langs.svg"), "w", encoding="utf-8") as f:
        f.write(langs_card(u))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
