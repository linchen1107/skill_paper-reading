"""Give a finished paper-reading page the default warm light theme (cream paper, espresso "screens" for demos).

Usage:  python <plugin>/scripts/warm_theme.py <topic> [page.html ...]
Pages default to index.html, plus talk.html when it exists. Run after the page is filled in and before check_page.py.
Safe to run again: a themed page only gets its generated blocks refreshed.

The page CSS and the widgets' CSS are recoloured by a fixed map (dark slate -> warm light); canvases keep a dark
warm background so the demos' light labels and data colours stay readable, and a small canvas patch turns slate
greys drawn by the demos into warm greys. Data colours (cyan, amber, violet, green) are not changed inside demos.
Standard library only.
"""
import re
import sys
from pathlib import Path

CSS_MAP = {
    # page / panels
    "#0f1419": "#faf8f4", "#0c1116": "#f3ede3", "#080e16": "#f6f1e8", "#0b1118": "#f6f1e8",
    "#151c24": "#fffdf9", "#111820": "#fffdf9", "#0b1220": "#fffdf9", "#0b1420": "#fffdf9", "#0e151e": "#fffdf9",
    "#0d151f": "#fffdf9", "#101a29": "#fffdf9", "#111827": "#fffdf9", "#0b141f": "#fffdf9", "#0f172a": "#fffdf9",
    "#0e1620": "#fffdf9", "#131b24": "#fffdf9",
    # tints / hover / pressed
    "#1e293b": "#f1e8da", "#182331": "#f6efe3", "#14212b": "#f6efe3", "#12232e": "#f6efe3", "#122934": "#f8ece2",
    "#13232d": "#f8ece2", "#102735": "#f8ece2", "#142832": "#f8ece2", "#123546": "#f3dccb", "#0e2530": "#f8ece2",
    "#083344": "#f3dccb", "#082f3a": "#f8ece2", "#151f28": "#efe6d8", "#20313b": "#e9dccb", "#155e75": "#b4532a",
    "#164e63": "#f3dccb", "#1b2a33": "#e8dcc9",
    "#052e16": "#e7f3ea", "#2a0b0b": "#fbe9e6", "#2a1d05": "#fbf0dc", "#2a2410": "#fbf0dc", "#3b2f1a": "#fbf0dc",
    "#166534": "#9cc8a8", "#7f1d1d": "#e3a59b", "#854d0e": "#e2c08a",
    # borders
    "#2b3643": "#e2d6c3", "#334155": "#e2d6c3", "#45546b": "#d6c7b0", "#475569": "#d6c7b0", "#315163": "#d6c7b0",
    "#26313e": "#e2d6c3", "#778699": "#cdbca3",
    # text
    "#94a3b8": "#7d6b58", "#a3afbf": "#7d6b58", "#91a2b7": "#7d6b58", "#64748b": "#8a7866", "#b6c2d3": "#7d6b58",
    "#e2e8f0": "#2b2622", "#cbd5e1": "#4a4038", "#d2dce8": "#3d342c", "#d9e8ef": "#3d342c", "#f1f5f9": "#2b2622",
    # accents
    "#67e8f9": "#b4532a", "#22d3ee": "#b4532a", "#fbbf24": "#b7791f", "#facc15": "#b7791f", "#60a5fa": "#2f6fb3",
    "#c4b5fd": "#7c5cbf", "#c084fc": "#7c5cbf", "#f87171": "#c0392b", "#fb7185": "#c0392b", "#4ade80": "#2f855a",
    "#86efac": "#2f855a", "#fb923c": "#c05621",
}
RGBA_MAP = {
    "rgba(148,163,184,": "rgba(125,107,88,", "rgba(15,23,42,": "rgba(43,36,30,", "rgba(21,94,117,": "rgba(180,83,42,",
    "rgba(103,232,249,": "rgba(180,83,42,", "rgba(3,7,12,": "rgba(43,36,30,",
}
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400'
         '&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">')
WARM_EXTRA = """
  :root { --sans: "IBM Plex Sans", "Noto Sans TC", "Segoe UI", system-ui, sans-serif;
    --serif: "Lora", "Noto Serif TC", "Source Han Serif TC", Georgia, serif; --navy: #1a2744; --espresso: #2a211c; }
  body { background: #faf8f4; color: #2b2622; font-family: var(--sans); }
  h1, h2 { font-family: var(--serif); color: var(--navy); } h2 { border-bottom-color: #d8ccb8; } h3 { color: var(--navy); }
  #toc { background: #f3ede3; border-right-color: #e2d6c3; }
  #toc a.on { background: #e8dcc9; color: #2b2622; }
  /* every animation, chart and photo canvas is a warm dark "screen" so its light labels stay readable */
  main canvas { background: var(--espresso) !important; border-radius: 6px; }
  .fmap { background: var(--espresso) !important; }
  .fmap foreignObject, .fmap foreignObject * { color: #f1e8dc; }
  /* formula-map node colours (SVG attributes set by widgets.js) */
  .fmap [fill="#0f172a"] { fill: #3a2e26; } .fmap [stroke="#cbd5e1"] { stroke: #dfd2c1; }
  .fmap [fill="#083344"] { fill: #5a2f1e; } .fmap [stroke="#22d3ee"] { stroke: #e8956a; }
  .fmap [fill="#1e293b"] { fill: #3b3029; } .fmap [stroke="#475569"] { stroke: #6e5d4c; }
  .fmap [fill="#111827"] { fill: #231c17; } .fmap [stroke="#64748b"] { stroke: #8f7d69; }
  .fmap [stroke="#94a3b8"] { stroke: #bba98f; } .fmap [fill="#94a3b8"] { fill: #bba98f; }
  /* key formula cards: a dark "screen" so the coloured formula terms keep their contrast */
  .keyeq { background: var(--espresso) !important; border-color: #4a3d33 !important; border-left: 4px solid #e8956a !important; }
  .keyeq .plain, .keyeq .tex-block, .keyeq .katex { color: #f1e8dc !important; }
  .keyeq .w-a { color: #67e8f9 !important; } .keyeq .w-b { color: #fbbf24 !important; }
  .keyeq .w-c { color: #c4b5fd !important; } .keyeq .w-d { color: #86efac !important; }
"""
CANVAS_PATCH = """<script>
/* warm neutrals inside canvases: slate greys become warm greys; data colours are unchanged */
(function () {
  const M = { '#94a3b8': '#bba98f', '#a3afbf': '#bfae96', '#64748b': '#8f7d69', '#475569': '#6e5d4c', '#334155': '#4d4036',
    '#2b3643': '#4a3d33', '#1e293b': '#3b3029', '#0f172a': '#231c17', '#0b1220': '#231c17', '#111827': '#231c17',
    '#e2e8f0': '#f1e8dc', '#cbd5e1': '#dfd2c1', '#f8fafc': '#fbf6ee', '#f1f5f9': '#fbf6ee' };
  const R = [['rgba(148,163,184,', 'rgba(187,169,143,'], ['rgba(15,20,25,', 'rgba(35,28,23,'], ['rgba(5,10,18,', 'rgba(35,28,23,']];
  const map = v => { if (typeof v !== 'string') return v; const k = v.toLowerCase(); if (M[k]) return M[k];
    for (const [a, b] of R) if (k.startsWith(a)) return b + v.slice(a.length); return v; };
  const P = CanvasRenderingContext2D.prototype;
  ['fillStyle', 'strokeStyle'].forEach(p => { const d = Object.getOwnPropertyDescriptor(P, p);
    Object.defineProperty(P, p, { get: d.get, set(v) { d.set.call(this, map(v)); }, configurable: true }); });
})();
</script>
"""


def warm_css(css):
    css = re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: CSS_MAP.get(m.group(0).lower(), m.group(0)), css)
    for a, b in RGBA_MAP.items():
        css = css.replace(a, b)
    return css


def warmify(html, widget_css):
    if 'id="warm-theme"' in html:  # already themed: refresh the generated blocks only
        html = re.sub(r'<style id="warm-theme">.*?</style>', lambda m: '<style id="warm-theme">' + WARM_EXTRA + "</style>", html, 1, re.S)
        html = re.sub(r'<style id="pr-widget-css">.*?</style>', lambda m: '<style id="pr-widget-css">' + warm_css(widget_css) + "</style>", html, 1, re.S)
        return re.sub(r"<script>\n/\* warm neutrals inside canvases.*?</script>\n", lambda m: CANVAS_PATCH, html, 1, re.S)
    css = html[html.index("<style>") + 7: html.index("</style>")]
    h = html.replace('<link rel="stylesheet" href="katex/katex.min.css">', FONTS + '\n<link rel="stylesheet" href="katex/katex.min.css">', 1)
    # the widgets skip injecting their own CSS when #pr-widget-css exists, so the recoloured copy replaces it
    h = h.replace("<style>" + css + "</style>", "<style>" + warm_css(css) + "</style>\n<style id=\"warm-theme\">" + WARM_EXTRA + "</style>\n"
                  + '<style id="pr-widget-css">' + warm_css(widget_css) + "</style>", 1)
    return h.replace('<script src="katex/katex.min.js"></script>', CANVAS_PATCH + '<script src="katex/katex.min.js"></script>', 1)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    topic = Path(sys.argv[1])
    m = re.search(r"const WIDGET_CSS = `(.*?)`;", (topic / "widgets.js").read_text(encoding="utf-8"), re.S)
    if not m:
        sys.exit("widgets.js has no WIDGET_CSS block; copy the plugin's templates/widgets.js first")
    pages = sys.argv[2:] or ["index.html"] + (["talk.html"] if (topic / "talk.html").exists() else [])
    for name in pages:
        p = topic / name
        p.write_text(warmify(p.read_text(encoding="utf-8"), m.group(1)), encoding="utf-8")
        print(f"warm theme: {p}")


if __name__ == "__main__":
    main()
