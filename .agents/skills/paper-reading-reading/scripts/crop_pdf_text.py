"""Crop the paper's own sentences behind each confirmed error, with the wrong phrase boxed in red.

Usage:  python <plugin>/scripts/crop_pdf_text.py <paper.pdf> <items.tsv> <topic>/figs [prefix]
items.tsv, one phrase per line:   <item number><TAB><page, 1-based><TAB><exact phrase as it appears in the text layer>
Several lines with the same item number go into one image (stacked, each tile labelled with its page).
Writes <figs>/<prefix>-<item>.png (prefix defaults to "crit"), for <figure class="pdf-crop"> in the Weak spots chapter.

The page is rendered without its annotations (a user's highlights stay out); the crop snaps to whole text lines
of the phrase's own column with one line of context above and below. A phrase that is not found stops the run,
so a wrong quotation cannot slip through. Needs PyMuPDF and Pillow.
"""
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

ZOOM, PAD = 2.5, 24
RED, LABEL = (200, 40, 30), (125, 107, 88)


def tile(page, rects):
    """One image of the text lines around rects, all in the same column of one page."""
    blocks = [b for b in page.get_text("dict")["blocks"] if b.get("lines")]
    hit = [fitz.Rect(b["bbox"]) for b in blocks if any(fitz.Rect(b["bbox"]).intersects(r) for r in rects)]
    x0 = min(b.x0 for b in hit) - 4
    x1 = max(b.x1 for b in hit) + 4
    lines = [fitz.Rect(l["bbox"]) for b in blocks for l in b["lines"] if l["bbox"][0] >= x0 - 2 and l["bbox"][2] <= x1 + 2]
    top, bot = min(r.y0 for r in rects), max(r.y1 for r in rects)
    near = [l for l in lines if l.y1 > top - PAD and l.y0 < bot + PAD] or [fitz.Rect(x0, top, x1, bot)]
    clip = fitz.Rect(x0, min(l.y0 for l in near) - 3, x1, max(l.y1 for l in near) + 3)
    pix = page.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), clip=clip, annots=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(im)
    for r in rects:
        d.rectangle([(r.x0 - clip.x0) * ZOOM - 3, (r.y0 - clip.y0) * ZOOM - 2,
                     (r.x1 - clip.x0) * ZOOM + 3, (r.y1 - clip.y0) * ZOOM + 2], outline=RED, width=3)
    return im


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    pdf, items, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    prefix = sys.argv[4] if len(sys.argv) > 4 else "crit"
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf)
    wanted = {}
    for ln in items.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        n, page, phrase = ln.split("\t", 2)
        wanted.setdefault(n.strip(), []).append((int(page), phrase.strip()))
    for n, marks in wanted.items():
        groups = {}  # (page, column left edge) -> rects
        for page, phrase in marks:
            rects = doc[page - 1].search_for(phrase, flags=fitz.TEXT_DEHYPHENATE)
            if not rects:
                sys.exit(f"item {n}: phrase not found on p.{page}: {phrase!r}")
            w = doc[page - 1].rect.width
            for r in rects:
                groups.setdefault((page, 0 if r.x0 < w / 2 else 1), []).append(r)
        tiles = []
        for (page, _), rects in sorted(groups.items()):
            im = tile(doc[page - 1], rects)
            lab = Image.new("RGB", (im.width, 30), (250, 248, 244))
            ImageDraw.Draw(lab).text((6, 8), f"p. {page}", fill=LABEL)
            tiles += [lab, im]
        img = Image.new("RGB", (max(t.width for t in tiles), sum(t.height for t in tiles)), "white")
        y = 0
        for t in tiles:
            img.paste(t, (0, y))
            y += t.height
        dest = out / f"{prefix}-{n}.png"
        img.save(dest)
        print(f"{dest}  {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
