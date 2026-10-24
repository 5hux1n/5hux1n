"""Render one app-store style tile per project into assets/tiles/<slug>.svg.

Run locally after changing PROJECTS:  python3 .github/scripts/tiles.py
Icons live in assets/icons/ (PNG or SVG). Projects without an icon get a
lettermark in the given colour.
"""
import base64
import os
from html import escape

from theme import style

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
ICONS = os.path.join(ROOT, "assets", "icons")
OUT = os.path.join(ROOT, "assets", "tiles")

# slug, name, one-line description, icon file or (letter, colour A, colour B)
PROJECTS = [
    ("fanqiefn", "番茄净化", "番茄小说去广告与净化", "fanqiefn.png"),
    ("hongguofn", "红果净化", "红果短剧界面与播放调整", "hongguofn.png"),
    ("XianYuHelper", "闲鱼助手", "去广告 · 自动擦亮", "xianyu.png"),
    ("wclocate", "WCLocate", "微信虚拟定位", "wclocate.png"),
    ("uuhelper", "uu 远控增强", "快捷键与虚拟滚轮", "uuhelper.png"),
    ("UUScreenSwitch", "UU 远控切屏", "一键切换显示器", "uuscreenswitch.png"),
    ("Alipay2NFC", "Alipay2NFC", "碰一碰唤起指定支付宝", "alipay2nfc.png"),
    ("spoofnotify", "SpoofNotify", "通知权限伪装", "spoofnotify.png"),
    ("CodexM", "CodexM", "菜单栏切换 Codex 账户", "codexm.png"),
    ("CherryMac", "CherryMac", "CHERRY 键盘 Mac 客户端", ("C", "#ff5f6d", "#c2185b")),
    ("m04s", "m04s", "印先森打印机 Mac 驱动", ("印", "#7f8cff", "#4b3fd6")),
    ("shuxin", "书信", "可自托管的个人微博客", "shuxin.svg"),
    ("pingme", "PingMe", "独立项目反馈中心", "pingme.svg"),
    ("Silex", "Silex", "越狱软件源生成器", "silex.png"),
    ("repolist", "RepoList", "越狱源合集，一键添加", ("R", "#34d399", "#0f9d74")),
    ("NSimg", "NSimg", "NodeSeek 图片上传助手", "nsimg.png"),
]

W, H = 252, 80
ICON = 52
PAD = 14


def data_uri(path):
    mime = "image/svg+xml" if path.endswith(".svg") else "image/png"
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


def icon_markup(icon):
    x = y = PAD
    clip = f'<clipPath id="ic"><rect x="{x}" y="{y}" width="{ICON}" height="{ICON}" rx="12"/></clipPath>'
    if isinstance(icon, tuple):
        letter, a, b = icon
        return (
            f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>{clip}</defs>'
            f'<rect x="{x}" y="{y}" width="{ICON}" height="{ICON}" rx="12" fill="url(#g)"/>'
            f'<text x="{x + ICON / 2}" y="{y + ICON / 2 + 9}" text-anchor="middle" class="lm">{escape(letter)}</text>'
        )
    path = os.path.join(ICONS, icon)
    # SVG icons get a light plate so dark strokes stay visible in dark mode
    plate = f'<rect x="{x}" y="{y}" width="{ICON}" height="{ICON}" rx="12" fill="#fafafa"/>' if icon.endswith(".svg") else ""
    inset = 6 if icon == "pingme.svg" else 0
    s = ICON - 2 * inset
    return (
        f"<defs>{clip}</defs>{plate}"
        f'<image clip-path="url(#ic)" x="{x + inset}" y="{y + inset}" width="{s}" height="{s}" href="{data_uri(path)}"/>'
        f'<rect x="{x + .5}" y="{y + .5}" width="{ICON - 1}" height="{ICON - 1}" rx="11.5" fill="none" stroke="#000" stroke-opacity=".08"/>'
    )


def tile(name, desc, icon):
    tx = PAD + ICON + 14
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(name)}：{escape(desc)}">
{style('.lm { font: 700 26px -apple-system, "PingFang SC", "Noto Sans SC", sans-serif; fill: #fff; } .card { fill: var(--tile); }')}
<rect class="card" x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16"/>
{icon_markup(icon)}
<text x="{tx}" y="36" class="n">{escape(name)}</text>
<text x="{tx}" y="57" class="m">{escape(desc)}</text>
</svg>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    for slug, name, desc, icon in PROJECTS:
        with open(os.path.join(OUT, f"{slug}.svg"), "w", encoding="utf-8") as f:
            f.write(tile(name, desc, icon))
    print(f"wrote {len(PROJECTS)} tiles to {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
