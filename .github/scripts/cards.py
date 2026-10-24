"""Generate the GitHub stats strip SVG.

Runs in GitHub Actions with GITHUB_TOKEN. Writes:
  dist/stats.svg
Set MOCK=1 to render with sample data locally.
"""
import json
import os
import urllib.request
from html import escape

from theme import FONT, style

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
        "contributionCalendar": {"totalContributions": 118},
    },
    "repositories": {
        "totalCount": 29,
        "nodes": [
            {"stargazerCount": 30, "languages": {"edges": [
                {"size": 900000, "node": {"name": "Swift", "color": "#F05138"}},
                {"size": 500000, "node": {"name": "JavaScript", "color": "#f1e05a"}}]}},
            {"stargazerCount": 18, "languages": {"edges": [
                {"size": 400000, "node": {"name": "Objective-C", "color": "#438eff"}},
                {"size": 300000, "node": {"name": "Python", "color": "#3572A5"}},
                {"size": 120000, "node": {"name": "Logos", "color": "#ff0000"}},
                {"size": 90000, "node": {"name": "TypeScript", "color": "#3178c6"}},
                {"size": 60000, "node": {"name": "Shell", "color": "#89e051"}}]}},
        ],
    },
}

MUTED = "#8b949e"

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

STYLE = style("""
  .bar { transform-box: fill-box; transform-origin: left center; transform: scaleX(0);
         animation: grow 1s ease-out .2s forwards; }
  @keyframes grow { to { transform: scaleX(1); } }
  .big { font: 700 24px """ + FONT + """; fill: var(--text); }
""")


def frame(w, h, title, inner):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
{STYLE}
<rect class="card" x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12"/>
<text x="25" y="36" class="t">{escape(title)}</text>
{inner}
</svg>
"""


def stats_card(u):
    c = u["contributionsCollection"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    items = [
        ("star", "Stars", stars),
        ("fire", "近一年贡献", c["contributionCalendar"]["totalContributions"]),
        ("commit", "近一年提交", c["totalCommitContributions"] + c["restrictedContributionsCount"]),
        ("pr", "Pull Requests", c["totalPullRequestContributions"]),
        ("repo", "公开仓库", u["repositories"]["totalCount"]),
        ("people", "Followers", u["followers"]["totalCount"]),
    ]
    w, h, col = 780, 96, 130
    out = []
    for i, (icon, label, val) in enumerate(items):
        cx = col * i + col / 2
        if i:
            out.append(f'<line x1="{col * i}" y1="24" x2="{col * i}" y2="{h - 24}" stroke="var(--border)"/>')
        out.append(
            f'<g class="fade" style="animation-delay:{80 + i * 90}ms">'
            f'<text x="{cx}" y="46" class="big" text-anchor="middle">{fmt(val)}</text>'
            f'<g transform="translate({cx},66)"><text x="9" y="0" class="m" text-anchor="middle">{label}</text></g>'
            f'</g>'
        )
    # icons sit left of each label; label width estimated so the pair stays centred
    icons = []
    for i, (icon, label, _) in enumerate(items):
        cx = col * i + col / 2
        lw = sum(12.5 if ord(ch) > 0x2E80 else 7 for ch in label)
        x = cx + 9 - lw / 2 - 18
        icons.append(
            f'<g class="fade" style="animation-delay:{80 + i * 90}ms">'
            f'<path class="ic" d="{ICONS[icon]}" transform="translate({x:.1f},55) scale(0.8)"/></g>'
        )
    body = "\n".join(out + icons)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="GitHub 数据">
{STYLE}
<rect class="card" x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14"/>
{body}
</svg>
"""


def main():
    u = fetch()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_card(u))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
