"""Generate the pixel-art night city layers used by the site.

Usage: python3 tools/gen_scene.py [out_dir] [palette]
Defaults: assets/img/scene, blade (the palette the site uses).
Writes sky.svg, far.svg, mid.svg and near.svg (same viewBox, stacked for
parallax), plus sky-plain.svg (no moon) for the contact section and car.svg
for the flying cars. The other palettes are kept here to try alternatives:
the CSS colors in assets/css/nightcity.css have to be updated to match.
"""
import os
import random
import sys

W, H = 640, 360
STYLE = (
    "<style>"
    ".tw{animation:tw 3.2s steps(2) infinite}"
    ".tw2{animation:tw 4.7s steps(2) infinite 1.3s}"
    "@keyframes tw{50%{opacity:.15}}"
    ".fl{animation:fl 6s steps(1) infinite}"
    ".fl2{animation:fl 8.5s steps(1) infinite 2s}"
    "@keyframes fl{90%{opacity:.2}92%{opacity:1}95%{opacity:.35}97%{opacity:1}}"
    ".bc{animation:bc 1.8s steps(1) infinite}"
    "@keyframes bc{50%{opacity:0}}"
    ".wn{animation:wn 11s steps(1) infinite}"
    "@keyframes wn{61%,100%{opacity:0}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    "</style>"
)

# Choice lists keep the same length across palettes, so every palette draws
# the exact same city with different colors.
PALETTES = {
    "synthwave": {
        "sky": ["#05041a", "#080622", "#0c0929", "#110b31", "#170d3a", "#1f1043",
                "#29134c", "#351653", "#441958", "#561c5b", "#6a1f5c", "#80245b"],
        "stars": ["#ffffff", "#c9ceff", "#ffe9b8", "#ffffff"],
        "moon": ["#f3ead0", "#e6dcbd", "#d2c7a5"],
        "far": "#251744", "far_win": "#4a3076",
        "mid": "#150c29", "mid_edge": "#24153f", "billboard": "#1b0f33",
        "mid_win": ["#f7c66b", "#f7c66b", "#8fd3ff", "#ff7ac8"],
        "signs": ["#ff3d8b", "#29e3ff", "#ffb84d", "#b46bff"],
        "near": "#07050f", "near_edge": "#1a1230", "beacon": "#ff4b4b",
        "near_win": ["#ffcf6e", "#ffcf6e", "#9fe6ff"],
        "ground": "#05040b",
        "car": {"body": "#2b1f4d", "roof": "#3a2b63", "shine": "#4a3a80", "glass": "#9fe6ff",
                "stripe": "#ff3d8b", "glow": "#29e3ff", "wheel": "#120c22"},
    },
    "terminal": {
        "sky": ["#010604", "#020a06", "#030f08", "#04140b", "#051a0e", "#062011",
                "#072614", "#082d17", "#09341a", "#0b3c1d", "#0d4520", "#104f24"],
        "stars": ["#ffffff", "#bfffd2", "#e6ffb8", "#ffffff"],
        "moon": ["#dcffe6", "#c2ebcd", "#a6d4b3"],
        "far": "#0b2716", "far_win": "#1a5230",
        "mid": "#06160c", "mid_edge": "#0f2c19", "billboard": "#081d10",
        "mid_win": ["#7dff9e", "#7dff9e", "#c8ff3d", "#3dffd2"],
        "signs": ["#39ff88", "#c8ff3d", "#3dffd2", "#9dff6e"],
        "near": "#020804", "near_edge": "#0b2013", "beacon": "#ffd23d",
        "near_win": ["#9dff6e", "#9dff6e", "#3dffd2"],
        "ground": "#010402",
        "car": {"body": "#0d2a18", "roof": "#143b22", "shine": "#1f5733", "glass": "#c8ff3d",
                "stripe": "#39ff88", "glow": "#3dffd2", "wheel": "#020804"},
    },
    "blade": {
        "sky": ["#050b12", "#07111a", "#0a1822", "#0e1f29", "#14262e", "#1e2d31",
                "#2c3332", "#3f3830", "#573c2b", "#723f25", "#8f431f", "#ad4a1a"],
        "stars": ["#ffffff", "#ffe0b0", "#bff5ec", "#ffffff"],
        "moon": ["#ffdcae", "#f0c591", "#d9a872"],
        "far": "#2b201d", "far_win": "#553828",
        "mid": "#170f0f", "mid_edge": "#2c1d1a", "billboard": "#1e1311",
        "mid_win": ["#ffb35c", "#ffb35c", "#5ff2e0", "#ff6a3d"],
        "signs": ["#ff7a2e", "#2de0c8", "#ffd23d", "#ff3d5a"],
        "near": "#080505", "near_edge": "#201513", "beacon": "#ff3d3d",
        "near_win": ["#ffc06e", "#ffc06e", "#7ff5e6"],
        "ground": "#040202",
        "car": {"body": "#2a1c18", "roof": "#3b2620", "shine": "#5a3a2c", "glass": "#7ff5e6",
                "stripe": "#ff7a2e", "glow": "#2de0c8", "wheel": "#0c0807"},
    },
    "arctic": {
        "sky": ["#020617", "#030a20", "#050f29", "#071532", "#0a1b3c", "#0e2246",
                "#132a51", "#19335c", "#213d67", "#2b4873", "#37547f", "#45618b"],
        "stars": ["#ffffff", "#cfe8ff", "#e9dcff", "#ffffff"],
        "moon": ["#eef6ff", "#d7e6f7", "#bcd1ea"],
        "far": "#14223f", "far_win": "#284470",
        "mid": "#0a1430", "mid_edge": "#17284d", "billboard": "#0e1b3b",
        "mid_win": ["#bfe9ff", "#bfe9ff", "#6ad7ff", "#c7a6ff"],
        "signs": ["#6ad7ff", "#ffffff", "#c7a6ff", "#3d8bff"],
        "near": "#030713", "near_edge": "#101c38", "beacon": "#ff4b6e",
        "near_win": ["#d9f3ff", "#d9f3ff", "#8fd0ff"],
        "ground": "#02040b",
        "car": {"body": "#15244a", "roof": "#1d3160", "shine": "#2c4580", "glass": "#d9f3ff",
                "stripe": "#c7a6ff", "glow": "#6ad7ff", "wheel": "#030713"},
    },
}


class Layer:
    def __init__(self):
        self.parts = []

    def rect(self, x, y, w, h, fill, opacity=None, cls=None):
        extra = ""
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        if cls:
            extra += f' class="{cls}"'
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{extra}/>')

    def open_group(self, cls):
        self.parts.append(f'<g class="{cls}">' if cls else "<g>")

    def close_group(self):
        self.parts.append("</g>")

    def disc(self, cx, cy, r, fill, opacity=None):
        for y in range(cy - r, cy + r):
            dy = y - cy + 0.5
            half = int((r * r - dy * dy) ** 0.5) if dy * dy <= r * r else 0
            if half:
                self.rect(cx - half, y, 2 * half, 1, fill, opacity)

    def save(self, path):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
               f'width="{W}" height="{H}" shape-rendering="crispEdges" '
               f'preserveAspectRatio="xMidYMax slice">{STYLE}{"".join(self.parts)}</svg>\n')
        with open(path, "w") as f:
            f.write(svg)


def sky(P, moon=True):
    L = Layer()
    bands = P["sky"]
    y = 0
    for i, c in enumerate(bands):
        h = 22 + i * 3
        L.rect(0, y, W, h if i < len(bands) - 1 else H - y, c)
        y += h
    for _ in range(170):
        x, y = random.randrange(W), random.randrange(0, 210)
        c = random.choice(P["stars"])
        L.rect(x, y, 1, 1, c, cls=random.choice([None, None, "tw", "tw2"]))
    for _ in range(9):
        x, y = random.randrange(6, W - 6), random.randrange(4, 150)
        cls = random.choice(["tw", "tw2"])
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            L.rect(x + dx, y + dy, 1, 1, "#ffffff", cls=cls)
    if not moon:
        return L
    # moon with stepped halo and craters
    light, shade, crater = P["moon"]
    mx, my = 488, 74
    L.disc(mx, my, 46, light, 0.04)
    L.disc(mx, my, 36, light, 0.06)
    L.disc(mx, my, 27, light)
    L.disc(mx + 7, my - 3, 24, shade)
    for cx, cy, r in [(mx - 9, my - 8, 5), (mx + 8, my + 9, 4), (mx - 3, my + 12, 3), (mx + 12, my - 10, 2)]:
        L.disc(cx, cy, r, crater)
    return L


def far(P):
    L = Layer()
    x = -4
    while x < W:
        w = random.randint(14, 34)
        h = random.randint(70, 160)
        top = H - h
        L.rect(x, top, w, h, P["far"])
        if random.random() < 0.25:
            L.rect(x + w // 2 - 1, top - random.randint(8, 22), 2, 22, P["far"])
        for wy in range(top + 5, H, 7):
            for wx in range(x + 3, x + w - 3, 5):
                if random.random() < 0.12:
                    L.rect(wx, wy, 2, 2, P["far_win"])
        x += w
    return L


def mid(P):
    L = Layer()
    x = -6
    while x < W:
        w = random.randint(18, 44)
        h = random.randint(50, 200)
        top = H - h
        L.rect(x, top, w, h, P["mid"])
        L.rect(x, top, 1, h, P["mid_edge"])
        if random.random() < 0.35:
            step = random.randint(4, 8)
            L.rect(x + step, top - step, w - 2 * step, step, P["mid"])
        for wy in range(top + 6, H - 4, 6):
            for wx in range(x + 4, x + w - 3, 5):
                if random.random() < 0.2:
                    c = random.choice(P["mid_win"])
                    L.rect(wx, wy, 2, 3, c, random.choice([0.55, 0.75, 0.9]),
                           cls="wn" if random.random() < 0.05 else None)
        if w >= 22 and random.random() < 0.7:
            c = random.choice(P["signs"])
            sh = random.randint(18, 44)
            sx = x + random.choice([2, w - 6])
            sy = top + random.randint(4, max(5, min(26, h - sh - 4)))
            L.open_group(random.choice([None, "fl", "fl2"]))
            L.rect(sx - 4, sy - 4, 12, sh + 8, c, 0.12)
            L.rect(sx - 2, sy - 2, 8, sh + 4, c, 0.2)
            L.rect(sx, sy, 4, sh, c)
            for gy in range(sy + 4, sy + sh - 2, 6):
                L.rect(sx + 1, gy, 2, 1, P["mid"])
            L.close_group()
        elif w >= 30 and random.random() < 0.3 and h > 80:
            c = random.choice(P["signs"][:2])
            bx, by = x + 3, top - 16
            L.rect(bx + 4, by + 10, 2, 6, P["mid"])
            L.rect(bx + w - 12, by + 10, 2, 6, P["mid"])
            L.rect(bx, by, w - 6, 10, P["billboard"])
            L.open_group("fl2")
            L.rect(bx - 3, by - 3, w, 16, c, 0.14)
            L.rect(bx, by, w - 6, 1, c)
            L.rect(bx, by + 9, w - 6, 1, c)
            for gx in range(bx + 3, bx + w - 9, 4):
                L.rect(gx, by + 3, 2, 4, c, 0.85)
            L.close_group()
        x += w + random.randint(0, 2)
    return L


def near(P):
    L = Layer()
    x = -8
    while x < W:
        w = random.randint(22, 56)
        h = random.randint(22, 105)
        top = H - h
        L.rect(x, top, w, h, P["near"])
        L.rect(x, top, w, 1, P["near_edge"])
        if random.random() < 0.4:
            ax = x + random.randint(3, w - 4)
            ah = random.randint(8, 20)
            L.rect(ax, top - ah, 1, ah, P["near"])
            L.rect(ax, top - ah - 1, 1, 1, P["beacon"], cls="bc")
        if random.random() < 0.25 and w > 26:
            tx = x + random.randint(4, w - 14)
            L.rect(tx, top - 9, 9, 6, P["near"])
            L.rect(tx + 1, top - 3, 1, 3, P["near"])
            L.rect(tx + 7, top - 3, 1, 3, P["near"])
        for wy in range(top + 5, H - 6, 7):
            for wx in range(x + 4, x + w - 4, 6):
                if random.random() < 0.13:
                    L.rect(wx, wy, 3, 3, random.choice(P["near_win"]),
                           cls="wn" if random.random() < 0.06 else None)
        x += w + random.randint(0, 4)
    L.rect(0, H - 4, W, 4, P["ground"])
    return L


def car(P, path):
    c = P["car"]
    rects = [
        (4, 7, 16, 1, c["glow"], ".55"), (7, 8, 10, 1, c["glow"], ".25"),
        (7, 0, 9, 2, c["roof"], None), (8, 1, 3, 1, c["glass"], None), (12, 1, 3, 1, c["glass"], None),
        (2, 2, 20, 4, c["body"], None), (3, 2, 18, 1, c["shine"], None), (2, 4, 20, 1, c["stripe"], None),
        (21, 2, 2, 1, "#fff2a8", None), (23, 2, 1, 1, "#fff2a8", ".5"),
        (1, 2, 1, 2, "#ff4b4b", None), (0, 2, 1, 2, "#ff4b4b", ".4"),
        (5, 6, 3, 1, c["wheel"], None), (16, 6, 3, 1, c["wheel"], None),
    ]
    body = "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{f}"' + (f' opacity="{o}"' if o else "") + "/>"
        for x, y, w, h, f, o in rects)
    with open(path, "w") as fh:
        fh.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 9" width="24" height="9" '
                 f'shape-rendering="crispEdges">{body}</svg>\n')


def main(out_dir, palette):
    P = PALETTES[palette]
    os.makedirs(out_dir, exist_ok=True)
    random.seed(1984)
    for layer, fn in [("sky", sky), ("far", far), ("mid", mid), ("near", near)]:
        fn(P).save(os.path.join(out_dir, f"{layer}.svg"))
    random.seed(2077)
    sky(P, moon=False).save(os.path.join(out_dir, "sky-plain.svg"))
    car(P, os.path.join(out_dir, "car.svg"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "assets/img/scene",
         sys.argv[2] if len(sys.argv) > 2 else "blade")
