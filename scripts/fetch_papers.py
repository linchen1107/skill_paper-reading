"""Fetch a batch of papers and extract each one, in one command.

Usage: python fetch_papers.py <list.tsv> <topic_dir>

<list.tsv> has one paper per line: <short><TAB><source>, where <source> is
  an arXiv id            2101.08596
  a PDF URL              https://.../paper.pdf
  a local PDF path       C:/papers/foo.pdf   (read in place, not copied)
Lines starting with # are ignored.

For each paper: download to <topic_dir>/_work/pdf/<short>.pdf (skipped if it
exists), then extract to <topic_dir>/_work/extract/<short>/ with
extract_figures.py. Prints one line per paper and writes
<topic_dir>/_work/extract/status.tsv: short, status, pages, figures, source.
A paper that cannot be fetched is reported, not retried.
"""
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_figures  # noqa: E402

ARXIV = re.compile(r"^(?:arxiv:)?(\d{4}\.\d{4,5})(v\d+)?$", re.I)


def fetch(source, dest):
    m = ARXIV.match(source.strip())
    url = f"https://arxiv.org/pdf/{m.group(1)}{m.group(2) or ''}" if m else source
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 paper-reading"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if not data.startswith(b"%PDF"):
        raise ValueError("not a PDF (paywall or landing page)")
    dest.write_bytes(data)


def main(list_file, topic_dir):
    topic = Path(topic_dir)
    pdf_dir = topic / "_work" / "pdf"
    ext_dir = topic / "_work" / "extract"
    rows = []
    for line in Path(list_file).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        short, source = [x.strip() for x in line.split("\t", 1)]
        try:
            local = Path(source)
            if local.suffix.lower() == ".pdf" and local.exists():
                pdf = local
            else:
                pdf_dir.mkdir(parents=True, exist_ok=True)
                pdf = pdf_dir / f"{short}.pdf"
                if not pdf.exists():
                    fetch(source, pdf)
            info = extract_figures.main(str(pdf), str(ext_dir / short))
            rows.append(f"{short}\tok\t{info['pages']}\t{info['figures']}\t{source}")
        except Exception as e:  # report and go on with the rest of the batch
            reason = " ".join(str(e).split())[:80]
            rows.append(f"{short}\tfailed: {reason}\t\t\t{source}")
            print(f"{short}: failed: {reason}")
    ext_dir.mkdir(parents=True, exist_ok=True)
    with open(ext_dir / "status.tsv", "a", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    ok = sum("\tok\t" in r for r in rows)
    print(f"{ok}/{len(rows)} papers extracted -> {ext_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
