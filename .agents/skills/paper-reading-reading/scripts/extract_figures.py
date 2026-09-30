"""Extract a paper's text layer, its section headings and its real figures.

Usage: python extract_figures.py <paper.pdf> <out_dir>

Writes to <out_dir>:
  text.txt        the whole text layer, with "===== PAGE n =====" markers
  sections.tsv    line in text.txt, page, heading: read one section with an
                  offset instead of the whole text
  fig<N>.png      one image per captioned figure, caption included (150 DPI);
                  a reading copy for looking at the figure in context, not for pages
  fig<N>-real.*   the figure itself, without its caption, as the paper holds it:
                  the original embedded bitmap at its own resolution when the
                  figure is one raster image (.jpeg / .png), otherwise the vector
                  drawing cropped to the figure (.svg, text as outlines)
  figures.tsv     figure, page, status (ok / not found), bbox, caption start,
                  kind (raster / vector), real file

A figure is found from its caption ("Fig. 3:", "Figure 3.", "Fig. A.1:"):
vector drawings and raster images next to the caption are joined, with their
short text labels, stopping at body text. Tables are not extracted; read them
from text.txt. Needs PyMuPDF only.
"""
import re
import sys
from pathlib import Path

import pymupdf as fitz

CAPTION = re.compile(r"^(?:Fig\.|Figure|FIG\.)\s*([A-Z]?\.?\d+)\s*[:.|]")
# "3 Method", "3.2 Results", "IV. EXPERIMENTS", "A. Setting", or a bare common heading
HEADING = re.compile(
    r"^(?:(?:(?:1?\d)(?:\.1?\d){0,2}\.?|[IVX]{1,5}\.|[A-H]\.)\s+[A-Z][^.]{2,70}"
    r"|(?i:Abstract|Introduction|Related Work|Background|Methods?|Experiments|Results"
    r"|Discussion|Conclusions?|Limitations|References|Acknowledge?ments?|Appendix)\s*)$")


def is_body(block, col_width):
    # body text: several long lines; figure labels are short words
    x0, y0, x1, y1, text = block[:5]
    lines = [l for l in text.strip().split("\n") if l.strip()]
    avg = sum(len(l) for l in lines) / max(len(lines), 1)
    return len(lines) >= 2 and avg >= 35 and (x1 - x0) > 0.6 * col_width


def column_of(page, cap_rect):
    # the page column the caption sits in: left half, right half or full width
    mid = page.rect.width / 2
    if cap_rect.x1 <= mid + 10:
        return fitz.Rect(0, 0, mid, page.rect.height)
    if cap_rect.x0 >= mid - 10:
        return fitz.Rect(mid, 0, page.rect.width, page.rect.height)
    return fitz.Rect(page.rect)


def find_figure(page, cap_rect, blocks, graphics):
    col = column_of(page, cap_rect)
    margin = page.rect.height * 0.06  # running headers and footers
    barriers = [fitz.Rect(b[:4]) for b in blocks
                if fitz.Rect(b[:4]) != cap_rect
                and (is_body(b, col.width) or CAPTION.match(b[4].strip()))]

    def between_clear(r, above):
        # no body paragraph or another figure caption between graphic and caption
        lo, hi = (r.y1, cap_rect.y0) if above else (cap_rect.y1, r.y0)
        return not any(b.intersects(col) and b.y0 >= lo - 1 and b.y1 <= hi + 1
                       for b in barriers)

    for above in (True, False):
        if above:
            cand = [g for g in graphics if g.y1 <= cap_rect.y0 + 2 and g.intersects(col)]
        else:
            cand = [g for g in graphics if g.y0 >= cap_rect.y1 - 2 and g.intersects(col)]
        cand = [g for g in cand if between_clear(g, above)]
        if cand:
            break
    if not cand:
        return None

    region = fitz.Rect(cand[0])
    for g in cand[1:]:
        region.include_rect(g)
    # add short labels and titles touching the figure, but no body text
    grown = True
    while grown:
        grown = False
        near = fitz.Rect(region.x0 - 15, region.y0 - 15, region.x1 + 15, region.y1 + 15)
        for b in blocks:
            r = fitz.Rect(b[:4])
            if r == cap_rect or is_body(b, col.width) or CAPTION.match(b[4].strip()):
                continue
            if r.y1 < margin or r.y0 > page.rect.height - margin:
                continue
            if r.intersects(near) and not region.contains(r):
                region.include_rect(r)
                grown = True
    # a small margin so glyphs at the edge are not cut, never reaching into the caption
    art = fitz.Rect(region.x0 - 4, region.y0 - 4, region.x1 + 4, region.y1 + 4) & page.rect
    if cap_rect.y0 >= region.y1:
        art.y1 = min(art.y1, cap_rect.y0 - 0.5)
    elif cap_rect.y1 <= region.y0:
        art.y0 = max(art.y0, cap_rect.y1 + 0.5)
    region.include_rect(cap_rect)
    return region & page.rect, art


def save_real(doc, pno, page, art, out, num):
    """Save the figure as the paper holds it: the embedded bitmap, or the vector drawing as SVG."""
    area = max(art.width * art.height, 1)
    for info in page.get_image_info(xrefs=True):
        r = fitz.Rect(info["bbox"]) & art
        if info.get("xref") and r.width * r.height >= 0.85 * area:
            x = doc.extract_image(info["xref"])
            if x and x["ext"] in ("png", "jpeg", "jpg") and not x.get("smask"):
                path = out / f"fig{num}-real.{x['ext']}"
                path.write_bytes(x["image"])
            else:  # other codecs or a transparency mask: the same pixels, stored as PNG
                pix = fitz.Pixmap(doc, info["xref"])
                if x and x.get("smask"):
                    pix = fitz.Pixmap(pix, fitz.Pixmap(doc, x["smask"]))
                if pix.n - pix.alpha > 3:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                path = out / f"fig{num}-real.png"
                pix.save(path)
            return "raster", path.name
    # vector: copy the page, remove what lies outside the figure, crop, and write SVG
    tmp = fitz.open()
    tmp.insert_pdf(doc, from_page=pno, to_page=pno)
    q, R = tmp[0], tmp[0].rect
    for r in (fitz.Rect(R.x0, R.y0, R.x1, art.y0), fitz.Rect(R.x0, art.y1, R.x1, R.y1),
              fitz.Rect(R.x0, art.y0, art.x0, art.y1), fitz.Rect(art.x1, art.y0, R.x1, art.y1)):
        if not r.is_empty:
            q.add_redact_annot(r)
    q.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS,
                       graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                       text=fitz.PDF_REDACT_TEXT_REMOVE)
    q.set_cropbox(art & q.mediabox)
    path = out / f"fig{num}-real.svg"
    path.write_text(q.get_svg_image(text_as_path=True), encoding="utf-8")
    return "vector", path.name


NUMBER_ONLY = re.compile(r"^\d+(?:\.\d+){0,2}$")


def sections(lines):
    rows, page, skip = [], 0, False
    for n, line in enumerate(lines, start=1):
        if line.startswith("===== PAGE "):
            page = int(line.split()[2])
            continue
        if skip:  # title line already joined to its number
            skip = False
            continue
        t = line.strip()
        nxt = lines[n].strip() if n < len(lines) else ""
        # ICLR/NeurIPS style: the number on its own line, the title on the next
        if NUMBER_ONLY.match(t) and 2 < len(nxt) < 70 and nxt[0].isupper() and not nxt.endswith("."):
            t, skip = f"{t} {nxt}", True
        if "“" in t or '"' in t:  # reference entries, quotations
            continue
        if HEADING.match(t) and not CAPTION.match(t):
            rows.append(f"{n}\t{page}\t{t}")
    return rows


def main(pdf, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf)
    seen, rows, text = set(), [], []
    for pno, page in enumerate(doc, start=1):
        text.append(f"===== PAGE {pno} =====\n{page.get_text()}")
        blocks = [b for b in page.get_text("blocks") if b[6] == 0]
        caps = [b for b in blocks if CAPTION.match(b[4].strip())]
        if not caps:
            continue
        graphics = [fitz.Rect(r) for r in page.cluster_drawings()]
        graphics += [fitz.Rect(i["bbox"]) for i in page.get_image_info()]
        graphics = [g for g in graphics if g.width > 20 or g.height > 20]
        for c in caps:
            num = CAPTION.match(c[4].strip()).group(1)
            if num in seen:
                continue
            seen.add(num)
            cap_rect = fitz.Rect(c[:4])
            start = " ".join(c[4].split())[:80]
            found = find_figure(page, cap_rect, blocks, graphics)
            if found is None:
                rows.append(f"{num}\t{pno}\tnot found\t\t{start}\t\t")
                continue
            region, art = found
            page.get_pixmap(clip=region, dpi=150).save(out / f"fig{num}.png")
            kind, real = save_real(doc, pno - 1, page, art, out, num)
            box = ",".join(str(round(v)) for v in region)
            rows.append(f"{num}\t{pno}\tok\t{box}\t{start}\t{kind}\t{real}")
    full = "\n".join(text)
    (out / "text.txt").write_text(full, encoding="utf-8")
    heads = sections(full.split("\n"))
    (out / "sections.tsv").write_text(
        "line\tpage\theading\n" + "\n".join(heads) + "\n", encoding="utf-8")
    (out / "figures.tsv").write_text(
        "figure\tpage\tstatus\tbbox\tcaption\tkind\treal\n" + "\n".join(rows) + "\n", encoding="utf-8")
    found = sum("\tok\t" in r for r in rows)
    print(f"{len(doc)} pages, {len(heads)} headings, {len(rows)} captioned figures, "
          f"{found} extracted -> {out}")
    for r in rows:
        if "not found" in r:
            print("not found:", r)
    return {"pages": len(doc), "headings": len(heads), "figures": len(rows), "extracted": found}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
