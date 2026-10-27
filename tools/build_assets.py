#!/usr/bin/env python3
"""Generates assets/info-card.svg and assets/nkala-ascii.svg.

Usage:
    python tools/build_assets.py                    # monogram placeholder portrait
    python tools/build_assets.py tools/portrait.jpg # ASCII portrait from your photo / pencil drawing

For a graphite pencil drawing on light paper (dark strokes), add --paper.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# ---- palette: black / emerald / gold ----
BG1, BG2 = "#0b110f", "#050807"
BORDER = "#1f2d28"
MUTED = "#6b7f77"
TEXT = "#d7e4de"
EMERALD = "#10b981"
EMERALD_L = "#34d399"
GOLD = "#d4af37"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
W, H = 460, 553

COLS, ROWS = 76, 37
RAMP = " .:-=+*#%@"  # light -> dense


def chrome(title, gid):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">'
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient></defs>'
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#{gid})"/>'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{BORDER}"/>'
        f'<line x1="0" y1="30" x2="{W}" y2="30" stroke="{BORDER}"/>'
        '<circle cx="20" cy="15" r="5" fill="#ff5f56"/><circle cx="36" cy="15" r="5" fill="#ffbd2e"/>'
        '<circle cx="52" cy="15" r="5" fill="#27c93f"/>'
        f'<text x="{W/2}" y="19" fill="{MUTED}" font-size="12" text-anchor="middle">{title}</text>'
    )


def fade_in(inner, t):
    return (
        f'<g opacity="0" transform="translate(0,5)">{inner}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.4s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
        f'begin="{t:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>'
    )


# ---------------- info card ----------------
def build_info_card():
    out = [chrome("nkala@github: ~$ neofetch", "ibg")]
    t = 0.15
    out.append(fade_in(
        f'<text x="20" y="66" font-size="15" font-weight="700"><tspan fill="{EMERALD_L}">nkala</tspan>'
        f'<tspan fill="{MUTED}">@</tspan><tspan fill="{GOLD}">github</tspan></text>'
        f'<line x1="140" y1="62" x2="440" y2="62" stroke="{BORDER}"/>', t))

    def row(y, key, val, t):
        return fade_in(
            f'<text x="20" y="{y}" fill="{GOLD}" font-size="13" font-weight="700">{key}</text>'
            f'<text x="118" y="{y}" fill="{TEXT}" font-size="13">{val}</text>', t)

    def section(y, label, t):
        return fade_in(
            f'<text x="20" y="{y}" fill="{EMERALD}" font-size="13" font-weight="700">&#8212; {label}</text>'
            f'<line x1="{20 + 13 * 0.62 * (len(label) + 3) + 8:.0f}" y1="{y-4}" x2="440" y2="{y-4}" stroke="{BORDER}"/>', t)

    rows = [
        (96, "Name", "Tafadzwa Nkala"),
        (122, "Role", "Software Developer"),
        (148, "Focus", "AI apps &amp; full-stack products"),
        (174, "Edu", "B.Tech CSE (AI), LPU, Punjab"),
        (200, "Origin", "Zimbabwe"),
    ]
    for y, k, v in rows:
        t += 0.08
        out.append(row(y, k, v, t))

    t += 0.16
    out.append(section(238, "Stack", t))
    stack = [
        (264, "Web", "React, Next.js, TypeScript, Tailwind"),
        (290, "Backend", "Node.js, Supabase, PostgreSQL"),
        (316, "AI", "Python, Gemini API, Ollama, Streamlit"),
        (342, "3D", "Three.js, R3F, GSAP"),
        (368, "Tools", "Git, Vercel, Vite, WordPress"),
    ]
    for y, k, v in stack:
        t += 0.08
        out.append(row(y, k, v, t))

    t += 0.16
    out.append(section(406, "Highlights", t))
    hl = [
        (434, "ExplainAI &#8212; AI-powered learning platform"),
        (460, "KaziLink &#8212; local services marketplace"),
        (486, "The 8&#176; House &#8212; 3D architectural web"),
    ]
    for y, txt in hl:
        t += 0.08
        out.append(fade_in(
            f'<circle cx="23" cy="{y-4}" r="2.5" fill="{EMERALD}"/>'
            f'<text x="36" y="{y}" fill="{TEXT}" font-size="13">{txt}</text>', t))

    out.append("</svg>")
    (ASSETS / "info-card.svg").write_text("".join(out), encoding="utf-8")


# ---------------- ascii portrait ----------------
def monogram_image():
    img = Image.new("L", (600, 600), 0)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=380)
    except TypeError:
        font = ImageFont.load_default()
    d.text((300, 300), "TN", fill=255, font=font, anchor="mm")
    return img


def image_to_rows(img, paper):
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img, cutoff=2)
    if paper:  # dark strokes on light paper -> invert so strokes are dense
        img = ImageOps.invert(img)
    # crop to target aspect (char cell is ~ 5.5w x 12h px)
    target = (COLS * 5.5) / (ROWS * 12)
    w, h = img.size
    if w / h > target:
        nw = int(h * target)
        img = img.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w / target)
        img = img.crop((0, 0, w, nh))
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    px = img.load()
    rows = []
    for y in range(ROWS):
        line = "".join(RAMP[min(len(RAMP) - 1, px[x, y] * len(RAMP) // 256)] for x in range(COLS))
        rows.append(line.replace("&", "&amp;").replace("<", "&lt;"))
    return rows


def build_portrait(src, paper):
    img = Image.open(src) if src else monogram_image()
    rows = image_to_rows(img, paper)
    out = [chrome("nkala@github: ~$ ./portrait.sh", "abg")]
    step = 0.06
    for i, line in enumerate(rows):
        y0 = 37 + i * 12
        t = i * step
        out.append(
            f'<clipPath id="a{i}"><rect x="20" y="{y0}" height="12" width="0">'
            f'<animate attributeName="width" from="0" to="420" begin="{t:.2f}s" dur="{step}s" fill="freeze"/></rect></clipPath>'
            f'<g clip-path="url(#a{i})"><text xml:space="preserve" x="20" y="{y0+9.2}" fill="{EMERALD_L}" '
            f'font-size="9.6" textLength="420" lengthAdjust="spacing">{line}</text></g>'
        )
    end = len(rows) * step
    out.append(
        f'<line x1="0" y1="505" x2="{W}" y2="505" stroke="{BORDER}"/>'
        f'<text x="20" y="524" fill="{MUTED}" font-size="12.5">nkala@github:~$ whoami '
        f'<tspan fill="{TEXT}">Tafadzwa Nkala</tspan></text>'
        f'<rect x="322" y="513" width="7" height="13" fill="{GOLD}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" '
        f'repeatCount="indefinite" begin="{end:.2f}s"/></rect></svg>'
    )
    (ASSETS / "nkala-ascii.svg").write_text("".join(out), encoding="utf-8")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    paper = "--paper" in sys.argv
    build_info_card()
    build_portrait(args[0] if args else None, paper)
    print("Wrote", ASSETS / "info-card.svg", "and", ASSETS / "nkala-ascii.svg")
