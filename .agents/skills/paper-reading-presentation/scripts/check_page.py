"""Check a topic's index.html in a headless browser, without screenshots.

Usage: python check_page.py <topic_dir>

Uses Chrome, Edge or Chromium already on the machine (nothing is installed).
Copies selftest.js to <topic_dir>/_work/, opens index.html?selftest, and for
every knowledge-point section moves each control and confirms the output
changes; steps through each formula animation; then runs every PR.check (hand
calculations). Writes <topic_dir>/_work/verify/check.json and prints one line
per knowledge point:
  Pass     every control changes the output, every check agrees, and a
           section marked data-formula="1" has a formula animation that steps
  Fail     a control changes nothing, a check disagrees or is missing, a formula
           has no working animation, or the page errors
  No demo  the section has no demo (it must say why on the page)
The page as a whole also fails when the formula layer is incomplete (no formula
sections or map, a map node pointing nowhere, a formula section missing from the
map, an empty symbol table, a KaTeX error or an untypeset formula), when a figure
of the paper is a screenshot instead of its fig<N>-real file, when the key
formulas break their rules (none, outside a knowledge point, before its demo,
without a plain sentence whose coloured words match the formula, or not live:
every key formula card has PR.live controls and moving each one changes the
line with the numbers substituted),
when a display formula appears outside the knowledge points and the appendix,
when the formula map is not in the appendix, when a registered term is used before it is
explained or capitalised jargon in the storyline is not registered, when the cold read
(_work/verify/cold_read.md) is missing, has an item marked [blocking] (blocks the main line)
without "-> fixed:" in its line, or has no "Understanding check" that starts with "Correct", when no
section is marked data-traditional="1",
a map entry has no section, or the text contains unconfirmed wording
("not yet confirmed", "to be verified", "unverified", "TBD"), which belongs in the paper notes instead.
The structure must be: six cards at the top (#story .ov-card, kickers Problem,
Before, This paper, Result, Weak spots, Next steps, in that order), each linking
to its chapter (section.chapter #ch-1 to #ch-6, each with a .chapter-lead), and
every knowledge point inside a chapter.
It also reads index.html as text and fails the page when the six cards are
longer than the card limit, a paragraph of the cards or chapters has more than 5
sentences, a sentence is longer than the sentence limit, a knowledge-point field
has more than 2 sentences, a source sits in brackets inside a sentence (it belongs in the
step's <p class="src"> line or a <span class="cite">), or the page names
something itself ("this page calls ...", "we call ...") instead of using the paper's or the
standard term.
The browser profile lives in _work/tmp/ and is deleted afterwards.
"""
import html
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Reading load. Web readers mostly scan (NN/g: 79% scan, 16% read word by word) and plain-language
# guidance splits sentences over 25 English words and keeps paragraphs to 5 sentences (GOV.UK).
# The six cards are the summary of the whole paper: about 75 words per card.
LIMITS = {"story": 450, "sentence": 25}
CARDS = ["Problem", "Before", "This paper", "Result", "Weak spots", "Next steps"]
STORY_LIMIT = LIMITS["story"]
SENTENCE_LIMIT = LIMITS["sentence"]
PARAGRAPH_SENTENCES = 5
FIELD_SENTENCES = 2
INLINE_SOURCE = re.compile(r"[(][^()]*(Section|Table|Fig\.|p\.\s?\d|§)[^()]*[)]")
COINED = re.compile(r"\b(?:we|we'll|we will|let's|this page)\s+(?:call|name|refer to)\b|\bhereafter (?:called|referred to)\b", re.I)


def _plain(fragment):
    fragment = re.sub(r'<span class="cite">.*?</span>', "", fragment, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def _units(sentence):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9.%+\-]*", sentence))


def _sentences(text):
    # a sentence ends at . ! ? followed by a space and a capital or a quote
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", text)
    return [x.strip() for x in parts if x and _units(x) > 0]


def text_problems(page_html):
    """Reading-load checks on the page source; returns (problems, story_length)."""
    src = re.sub(r"<!--.*?-->|<script.*?</script>|<style.*?</style>", "", page_html, flags=re.S)
    problems = []
    start = src.find('<section id="story"')
    if start < 0:  # a page made before the cards had their own id starts at its first section
        start = src.find("<section", max(src.find("<main"), 0))
    first_ch = src.find('<section id="ch-1"', start)
    end = min([i for i in (src.find('id="backup"'), src.find('<section id="map"'), src.find('<section id="cluster"'),
                           src.find('<div id="appendix"')) if i > start] or [len(src)])
    cards_end = first_ch if first_ch > start else end
    para = lambda part: [(m.group(1), _plain(m.group(3))) for m in re.finditer(r"<(p|li)(\s[^>]*)?>(.*?)</\1>", part, re.S)
                         if not re.search(r'class="[^"]*\b(src|meta|note|sub)\b', m.group(2) or "")]
    cards = para(src[start:cards_end])
    # chapter prose: everything between the cards and the backup material except the knowledge points' fields,
    # demos and formula cards, which have their own limits or are generated
    body = re.sub(r'<div class="(?:demo|keyeq)[^"]*"[^>]*>.*?</div>\s*(?=<|$)', "", src[cards_end:end], flags=re.S)
    body = re.sub(r"<dl>.*?</dl>", "", body, flags=re.S)
    prose = cards + para(body)
    story_len = sum(_units(t) for _, t in cards)
    if story_len > STORY_LIMIT:
        problems.append(f"The six cards are {story_len} words; the limit is {STORY_LIMIT}. Keep only conclusions in the cards and move details to the chapter")
    long_s, long_p, inline = [], [], []
    for tag, text in prose:
        ss = _sentences(text)
        if tag == "p" and len(ss) > PARAGRAPH_SENTENCES:
            long_p.append(f"{len(ss)} sentences: {text[:30]}...")
        long_s += [x for x in ss if _units(x) > SENTENCE_LIMIT]
        inline += INLINE_SOURCE.findall(text) and [text[:30]] or []
    fields = [_plain(m.group(1)) for m in re.finditer(r"<dd>(.*?)</dd>", src[cards_end:end], re.S)]
    long_f = [f"{len(_sentences(t))} sentences: {t[:30]}..." for t in fields if len(_sentences(t)) > FIELD_SENTENCES]
    for t in fields:
        long_s += [x for x in _sentences(t) if _units(x) > SENTENCE_LIMIT]
        if INLINE_SOURCE.search(t):
            inline.append(t[:30])
    if long_p:
        problems.append(f"{len(long_p)} paragraphs have more than {PARAGRAPH_SENTENCES} sentences: " + "; ".join(long_p[:5]))
    if long_s:
        problems.append(f"{len(long_s)} sentences are longer than {SENTENCE_LIMIT} words; split them: " + "; ".join(x[:40] + "..." for x in long_s[:8]))
    if long_f:
        problems.append(f"{len(long_f)} knowledge-point fields have more than {FIELD_SENTENCES} sentences: " + "; ".join(long_f[:5]))
    if inline:
        problems.append(f"{len(inline)} sources sit in brackets inside a sentence; move them to the paragraph's last <p class=\"src\"> or a <span class=\"cite\">: " + "; ".join(x + "..." for x in inline[:5]))
    coined = sorted(set(COINED.findall(_plain(src))))
    if coined:
        problems.append("The page names something itself (" + ", ".join(coined) + "). Use the paper's term or the standard term and explain it in one plain sentence at first use")
    return problems, story_len


def find_browser():
    names = ["chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
             "msedge", "microsoft-edge"]
    cands = []
    if platform.system() == "Windows":
        for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"),
                     os.environ.get("LOCALAPPDATA")):
            if base:
                cands += [Path(base) / "Google/Chrome/Application/chrome.exe",
                          Path(base) / "Microsoft/Edge/Application/msedge.exe"]
    elif platform.system() == "Darwin":
        cands += [Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                  Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
                  Path("/Applications/Chromium.app/Contents/MacOS/Chromium")]
    for c in cands:
        if c.exists():
            return str(c)
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def main(topic_dir):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    topic = Path(topic_dir).resolve()
    page = topic / "index.html"
    if not page.exists():
        sys.exit(f"no index.html in {topic}")
    browser = find_browser()
    if not browser:
        sys.exit("no Chrome, Edge or Chromium found; the page cannot be checked here")
    work = topic / "_work"
    (work / "verify").mkdir(parents=True, exist_ok=True)
    shutil.copy(HERE / "selftest.js", work / "selftest.js")
    profile = work / "tmp" / "check-profile"
    try:
        run = subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--allow-file-access-from-files",
             f"--user-data-dir={profile}", "--virtual-time-budget=20000", "--dump-dom",
             page.as_uri() + "?selftest"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
        (work / "selftest.js").unlink(missing_ok=True)
    m = re.search(r'<pre id="selftest-result">(.*?)</pre>', run.stdout, re.S)
    if not m:
        sys.exit("the self-test did not report; the page may not load widgets.js or demos.js")
    res = json.loads(html.unescape(m.group(1)))
    (work / "verify" / "check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    checks = {}
    for c in res["checks"]:
        checks.setdefault(str(c["kp"]), []).append(c)
    bad = 0
    for s in res["sections"]:
        cs = checks.get(str(s["kp"]), [])
        ok_checks = sum(c["ok"] for c in cs)
        anim_ok = s["anim"] or not s["formula"]
        if not s["demo"]:
            verdict = "No demo"
            if s["formula"]:
                verdict = "Fail"
                bad += 1
        elif s["controls"] and s["changed"] == s["controls"] and cs and ok_checks == len(cs) and anim_ok and not res["errors"]:
            verdict = "Pass"
        else:
            verdict = "Fail"
            bad += 1
        extra = f" no response: {', '.join(s['unchanged'])}" if s["unchanged"] else ""
        extra += "".join(f" check failed: {c['name']}" for c in cs if not c["ok"])
        if s["demo"] and not cs:
            extra += " no hand-calculation check"
        if not anim_ok:
            extra += " has a formula but no step-by-step formula animation"
        anim = f"animation {s['animSteps']} steps" if s["anim"] else ("animation missing" if s["formula"] else "animation -")
        tag = "[traditional] " if s["traditional"] else ""
        print(f"{s['kp']}\t{verdict}\tcontrols {s['changed']}/{s['controls']}\tchecks {ok_checks}/{len(cs)}\t{anim}\t{tag}{s['title']}{extra}")
    if not any(s["traditional"] for s in res["sections"]):
        bad += 1
        print("Fail: no knowledge point demonstrates the traditional approach (data-traditional=\"1\")")
    if res["mapMissing"]:
        bad += 1
        print("Fail: knowledge points on the map but not on the page:", ", ".join(res["mapMissing"]))
    f = res.get("formulas", {})
    problems = []
    if not f.get("sections"):
        problems.append("no formula section (section.eq-sec)")
    if not f.get("mapNodes"):
        problems.append("no formula map (PR.formulaMap)")
    if f.get("brokenLinks"):
        problems.append("map nodes link to places that do not exist: " + ", ".join(f["brokenLinks"]))
    if f.get("notOnMap"):
        problems.append("formula sections missing from the map: " + ", ".join(f["notOnMap"]))
    if f.get("symbols", 0) < 1:
        problems.append("the symbol table is empty")
    if f.get("texErrors"):
        problems.append(f"{f['texErrors']} formula typesetting errors (.katex-error)")
    if f.get("texFallback"):
        problems.append(f"{f['texFallback']} formulas are not typeset (katex/ did not load)")
    keys = res.get("keyFormulas", [])
    if f.get("sections") and not keys:
        problems.append("no formula card (.keyeq): put one card for every formula a knowledge point uses, after its demo")
    for k in keys:
        where = f"Formula card (knowledge point {k['kp'] or '?'}{' ' + k['name'] if k.get('name') else ''}) "
        if not k["kp"]:
            problems.append(where + "must sit inside a knowledge point")
            continue
        if not k["formulaKp"] and not k.get("live"):
            problems.append(where + "does not show the numbers being substituted: add a PR.live control row, or give its knowledge point a formula animation (data-formula=\"1\")")
        if not k["afterDemo"]:
            problems.append(where + "must come after the demo: first move the controls and see the numbers, then the general form")
        if not k["plain"]:
            problems.append(where + "has no plain sentence (.plain)")
        if not k["words"]:
            problems.append(where + "has a plain sentence without coloured key words (w-a to w-d)")
        if k["unmatched"]:
            problems.append(where + "has key words with no same-coloured term in the formula: " + ", ".join(k["unmatched"]))
        elif k["words"] and not k["hover"]:
            problems.append(where + "does not highlight the matching term when a key word is hovered")
        if not k["typeset"]:
            problems.append(where + "has a formula that is not typeset")
        if not k.get("live"):
            problems.append(where + "is not interactive: add data-live=\"name\" and, in demos.js, PR.live('name', {controls, tex}) with sliders and the line with the numbers substituted")
        elif k.get("liveControls", 0) == 0 or k.get("liveChanged", 0) < k.get("liveControls", 0):
            problems.append(where + f"has live controls of which only {k.get('liveChanged', 0)}/{k.get('liveControls', 0)} change the substituted line; every one must change it")
    if res.get("storyFormulas"):
        problems.append(f"{res['storyFormulas']} display formulas sit outside the knowledge points and the appendix (cards, chapter openings or the paper table); formulas belong only in knowledge points or the appendix")
    if not res.get("overviewInAppendix", True):
        problems.append("the formula map belongs in the appendix (#appendix), not at the top of the page")
    st = res.get("structure", {})
    if st.get("cards") != CARDS:
        problems.append("The page must open with 6 cards in this order: " + ", ".join(CARDS) + " (.ov-kicker); it has: " + ", ".join(st.get("cards") or ["none"]))
    want = [f"#ch-{i}" for i in range(1, 7)]
    if st.get("cardLinks") and st["cardLinks"] != want[:len(st["cardLinks"])]:
        problems.append("each card must link to its chapter (#ch-1 to #ch-6): " + ", ".join(x or "(no link)" for x in st["cardLinks"]))
    chs = st.get("chapters", [])
    if [c["id"] for c in chs] != [w[1:] for w in want]:
        problems.append("the page must have 6 section.chapter elements in order (ch-1 to ch-6), one per card; it has: " + ", ".join(c["id"] for c in chs))
    for c in chs:
        if not c["lead"]:
            problems.append(f"{c['id']} has no opening conclusion sentence (.chapter-lead)")
    for c in chs[:4]:
        if not c["kps"]:
            problems.append(f"{c['id']} ({c['name']}) has no knowledge points; the chapter's content must be developed through knowledge points")
    if st.get("kpOutside"):
        problems.append("these knowledge points are not inside any chapter; move each to the chapter of the card it supports: " + ", ".join(st["kpOutside"]))
    print(f"Structure: {len(st.get('cards', []))} cards, {len(chs)} chapters, knowledge points per chapter: " + " / ".join(str(c["kps"]) for c in chs))
    print(f"Formula cards: {len(keys)}, {sum(1 for k in keys if k.get('live'))} live; appendix {f.get('sections', 0)} sections, {f.get('mapNodes', 0)} map nodes, {f.get('symbols', 0)} symbols")
    t = res.get("terms", {})
    if not t.get("count"):
        problems.append("no term list: in demos.js, list the page's technical terms with PR.terms({...}), each with one plain sentence")
    for x in t.get("late", []):
        problems.append(f"\"{x['term']}\" appears before it is explained: ...{x['context']}...")
    for k in t.get("notExplained", []):
        problems.append(f"\"{k}\" is used on the page but not explained with <dfn data-term> at first use")
    for k in t.get("dfnNotListed", []):
        problems.append(f"<dfn data-term=\"{k}\"> is not in the term list")
    if t.get("unlisted"):
        problems.append("the cards and chapter openings use terms that are not in the term list: " + ", ".join(t["unlisted"][:30]))
    (work / "verify" / "reading_text.txt").write_text(res.get("readingText", ""), encoding="utf-8")
    cold = work / "verify" / "cold_read.md"
    if not cold.exists():
        problems.append("the cold read was not run: following references/cold-read.md, have a reader who has not seen the paper read _work/verify/reading_text.txt")
    else:
        text = cold.read_text(encoding="utf-8")
        def items(head):
            part = text.split(head, 1)[-1].split("\n## ", 1)[0] if head in text else ""
            return [ln.strip() for ln in part.splitlines() if ln.strip().startswith("- ")]
        unclear, cut = items("## Unclear"), items("## Can be cut")
        blocking = [x for x in unclear if x.startswith("- [blocking]")]
        open_blocking = [x for x in blocking if "\u2192 fixed:" not in x]
        check = text.split("## Understanding check", 1)[-1].split("\n## ", 1)[0].strip() if "## Understanding check" in text else ""
        if open_blocking:
            problems.append(f"{len(open_blocking)} blocking items in the cold read are not fixed (after fixing, end the line with \"\u2192 fixed: how it was changed\"): {cold}")
        if not check:
            problems.append("the cold read has no understanding check: compare the reader's 3-sentence summary with the paper, then write \"Correct\" under \"## Understanding check\" in cold_read.md, or list what was misread")
        elif not check.startswith("Correct"):
            problems.append("the cold reader misunderstood the page, so it would mislead readers: fix it and redo the cold read")
        print(f"Cold read: {len(blocking)} blocking ({len(open_blocking)} not fixed), {len(unclear) - len(blocking)} minor, {len(cut)} can be cut (the last two do not block acceptance; list them in the delivery message)")
    print(f"Terms: {t.get('count', 0)}; cold-read text -> {work / 'verify' / 'reading_text.txt'}")
    figs = res.get("figures", [])
    for fg in figs:
        if not fg["ok"]:
            problems.append("a paper figure uses a screenshot; use fig<N>-real.* instead: " + fg["src"])
        elif not fg["loaded"]:
            problems.append("a paper figure failed to load: " + fg["src"])
        elif not fg.get("popup"):
            problems.append("clicking a paper figure does not open a popup: " + fg["src"])
    print(f"Paper figures: {len(figs)}, {sum(f['ok'] and not f.get('crop') for f in figs)} real image files, {sum(bool(f.get('crop')) for f in figs)} screenshots of the original (evidence for weak spots)")
    tp, story_len = text_problems(page.read_text(encoding="utf-8"))
    problems += tp
    print(f"Reading load: the six cards are {story_len} words (limit {STORY_LIMIT}); sentence limit {SENTENCE_LIMIT} words")
    for p in problems:
        bad += 1
        print("Fail: " + p)
    if res.get("unconfirmed"):
        bad += 1
        print(f"Fail: the page has {len(res['unconfirmed'])} unconfirmed statements; verify and rewrite them, or move them to the paper notes:")
        for u in res["unconfirmed"][:20]:
            print("  …" + u + "…")
    if res["errors"]:
        bad += 1
        print("Page errors:", "; ".join(res["errors"][:5]))
    print(f"{len(res['sections'])} knowledge points, {bad} failures -> {work / 'verify' / 'check.json'}")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
