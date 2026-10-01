"""Turn <topic>/papers/*.md into papers/*.html so a note opens as a readable page in the browser.

Usage: python build_notes.py <topic_dir>
The .md files stay the source; run this again after editing a note. index.html links to the .html.
Covers what the notes use: front matter, headings, nested lists, paragraphs, block quotes,
tables, **bold**, *italic*, `code` and links (links to another note's .md point to its .html).
"""
import html
import re
import sys
from pathlib import Path

CSS = """
:root{--bg:#0f1419;--panel:#151c24;--ink:#e2e8f0;--muted:#94a3b8;--line:#2b3643;--acc:#67e8f9}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 system-ui,"Noto Sans TC","Microsoft JhengHei",sans-serif}
main{max-width:920px;margin:0 auto;padding:24px 16px 80px}
a{color:var(--acc)} h1{font-size:26px;margin:8px 0 16px} h2{font-size:20px;margin:32px 0 10px;padding-bottom:4px;border-bottom:1px solid var(--line)}
h3{font-size:17px;margin:22px 0 6px} code{background:var(--panel);padding:1px 5px;border-radius:4px;font-size:.9em}
blockquote{margin:10px 0;padding:6px 14px;border-left:3px solid var(--acc);background:var(--panel);color:#cbd5e1}
table{border-collapse:collapse;margin:10px 0;display:block;overflow-x:auto} th,td{border:1px solid var(--line);padding:4px 10px;text-align:left} th{background:var(--panel)}
.meta{border:1px solid var(--line);border-radius:8px;background:var(--panel);padding:10px 14px;margin-bottom:18px}
.meta div{display:flex;gap:12px} .meta b{color:var(--muted);font-weight:400;min-width:4.5em;flex:none}
.top{font-size:14px;margin-bottom:12px} li{margin:2px 0} ul,ol{padding-left:1.5em}
"""


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)

    def link(m):
        text, href = m.group(1), m.group(2)
        if not re.match(r"[a-z]+:", href):
            href = re.sub(r"\.md(#|$)", r".html\1", href)
        return f'<a href="{href}">{text}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def front_matter(lines):
    if not lines or lines[0].strip() != "---":
        return [], lines
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    meta = []
    for ln in lines[1:end]:
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta.append((k.strip(), v.strip().strip('"')))
    return meta, lines[end + 1:]


def body(lines):
    out, para, stack = [], [], []  # stack of (indent, tag) for open lists

    def flush_para():
        if para:
            out.append("<p>" + "<br>".join(inline(x) for x in para) + "</p>")
            para.clear()

    def close_lists(to=-1):
        while stack and stack[-1][0] > to:
            out.append(f"</li></{stack.pop()[1]}>")

    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        m = re.match(r"^( *)([-*]|\d+\.) (.*)$", ln)
        if not ln.strip():
            flush_para(); close_lists(); i += 1; continue
        if m:
            flush_para()
            ind, tag = len(m.group(1)), ("ol" if m.group(2)[0].isdigit() else "ul")
            if stack and ind > stack[-1][0]:
                out.append(f"<{tag}><li>")
                stack.append((ind, tag))
            else:
                close_lists(ind)
                if stack and stack[-1][0] == ind:
                    out.append("</li><li>")
                else:
                    out.append(f"<{tag}><li>")
                    stack.append((ind, tag))
            out.append(inline(m.group(3)))
            i += 1; continue
        if stack and ln.startswith(" "):  # continuation of a list item
            out.append("<br>" + inline(ln.strip())); i += 1; continue
        close_lists()
        h = re.match(r"^(#{1,6}) (.*)$", ln)
        if h:
            flush_para(); n = len(h.group(1))
            out.append(f"<h{n}>{inline(h.group(2))}</h{n}>"); i += 1; continue
        if ln.startswith(">"):
            flush_para(); q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(inline(lines[i].lstrip(">").strip())); i += 1
            out.append("<blockquote>" + "<br>".join(q) + "</blockquote>"); continue
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            flush_para()
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            rows = ["<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells(ln)) + "</tr>"]
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(lines[i])) + "</tr>"); i += 1
            out.append("<table>" + "".join(rows) + "</table>"); continue
        if re.match(r"^-{3,}$", ln):
            flush_para(); out.append("<hr>"); i += 1; continue
        para.append(ln.strip()); i += 1
    flush_para(); close_lists()
    return "\n".join(out)


def convert(md):
    meta, lines = front_matter(md.read_text(encoding="utf-8").splitlines())
    title = dict(meta).get("簡稱") or dict(meta).get("title") or md.stem
    meta_html = "".join(f"<div><b>{html.escape(k)}</b><span>{inline(v)}</span></div>" for k, v in meta)
    page = f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head>
<body><main>
<div class="top"><a href="../index.html#cluster">← 回到論文群</a>　·　<a href="{md.name}">原始 Markdown</a></div>
{f'<div class="meta">{meta_html}</div>' if meta else ''}
{body(lines)}
</main></body></html>
"""
    md.with_suffix(".html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    notes = sorted((Path(sys.argv[1]).resolve() / "papers").glob("*.md"))
    for md in notes:
        convert(md)
    print(f"{len(notes)} notes -> html")
