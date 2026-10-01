"""Check a topic's index.html in a headless browser, without screenshots.

Usage: python check_page.py <topic_dir>

Uses Chrome, Edge or Chromium already on the machine (nothing is installed).
Copies selftest.js to <topic_dir>/_work/, opens index.html?selftest, and for
every knowledge-point section moves each control and confirms the output
changes; steps through each formula animation; then runs every PR.check (hand
calculations). Writes <topic_dir>/_work/verify/check.json and prints one line
per knowledge point:
  通過     every control changes the output, every check agrees, and a
           section marked data-formula="1" has a formula animation that steps
  未通過   a control changes nothing, a check disagrees or is missing, a formula
           has no working animation, or the page errors
  無示範   the section has no demo (it must say why on the page)
The page as a whole also fails when the formula layer is incomplete (no formula
sections or map, a map node pointing nowhere, a formula section missing from the
map, an empty symbol table, a KaTeX error or an untypeset formula), when a figure
of the paper is a screenshot instead of its fig<N>-real file, when the key
formulas break their rules (none, more than 5, outside a knowledge point, before
its demo, without a plain sentence whose coloured words match the formula),
when a display formula appears outside the knowledge points and the appendix,
when the formula map is not in the appendix, when a registered term is used before it is
explained or capitalised jargon in the storyline is not registered, when the latest cold
read (_work/verify/cold_read.md) is missing, older than index.html or lists anything, when no
section is marked data-traditional="1",
a map entry has no section, or the text contains unconfirmed wording
(尚未確認, 待驗證, 還沒確認), which belongs in the paper notes instead.
It also reads index.html as text and fails the page when the storyline (from
#story to the knowledge-point map) is longer than STORY_LIMIT characters, a
storyline paragraph has more than 5 sentences, a sentence of the storyline or of
a knowledge point is longer than SENTENCE_LIMIT, a knowledge-point field has more
than 2 sentences, a source sits in brackets inside a sentence (it belongs in the
step's <p class="src"> line or a <span class="cite">), or the page names
something itself (本頁稱為, 我們稱 ...) instead of using the paper's or the
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
# guidance splits sentences over 25 English words and keeps paragraphs to 5 sentences (GOV.UK);
# 40 is the Chinese equivalent used here (CJK characters, plus one per English word or number).
STORY_LIMIT = 3000
SENTENCE_LIMIT = 40
PARAGRAPH_SENTENCES = 5
FIELD_SENTENCES = 2
INLINE_SOURCE = re.compile(r"[（(][^（）()]*(原論文報告|本次實際重現|Section|Table|Fig\.|p\.\s?\d|§)[^（）()]*[）)]")
COINED = re.compile(r"本頁(?:稱|把它叫|把這[^，。]{0,6}叫|叫它)|我們(?:稱|把它叫)|以下(?:簡)?稱為|姑且稱|暫且稱")


def _plain(fragment):
    fragment = re.sub(r'<span class="cite">.*?</span>', "", fragment, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def _units(sentence):
    return len(re.findall(r"[\u3400-\u9fff]|[A-Za-z0-9][A-Za-z0-9.%+\-]*", sentence))


def _sentences(text):
    return [x.strip() for x in re.split(r"(?<=[。！？!?])", text) if _units(x) > 0]


def text_problems(page_html):
    """Reading-load checks on the page source; returns (problems, story_length)."""
    src = re.sub(r"<!--.*?-->|<script.*?</script>|<style.*?</style>", "", page_html, flags=re.S)
    problems = []
    start = src.find('<section id="story"')
    if start < 0:  # a page made before the storyline had its own id starts at its first section
        start = src.find("<section", max(src.find("<main"), 0))
    end = min([i for i in (src.find('<section id="map"'), src.find('<section id="kps"'),
                           src.find('<section id="cluster"')) if i > start] or [len(src)])
    story = src[start:end] if start >= 0 else ""
    blocks = [(m.group(1), m.group(2) or "", m.group(3)) for m in
              re.finditer(r"<(p|li)(\s[^>]*)?>(.*?)</\1>", story, re.S)]
    prose = [(tag, _plain(body)) for tag, attrs, body in blocks
             if not re.search(r'class="[^"]*\b(src|meta|note|sub)\b', attrs)]
    story_len = sum(_units(t) for _, t in prose)
    if story_len > STORY_LIMIT:
        problems.append(f"導讀有 {story_len} 字，上限 {STORY_LIMIT}：同一件事只講一次，細節移到知識點")
    long_s, long_p, inline = [], [], []
    for tag, text in prose:
        ss = _sentences(text)
        if tag == "p" and len(ss) > PARAGRAPH_SENTENCES:
            long_p.append(f"{len(ss)} 句：{text[:30]}…")
        long_s += [x for x in ss if _units(x) > SENTENCE_LIMIT]
        inline += INLINE_SOURCE.findall(text) and [text[:30]] or []
    fields = [_plain(m.group(1)) for m in re.finditer(r"<dd>(.*?)</dd>", src[end:].split('<div id="appendix"')[0], re.S)]
    long_f = [f"{len(_sentences(t))} 句：{t[:30]}…" for t in fields if len(_sentences(t)) > FIELD_SENTENCES]
    for t in fields:
        long_s += [x for x in _sentences(t) if _units(x) > SENTENCE_LIMIT]
        if INLINE_SOURCE.search(t):
            inline.append(t[:30])
    if long_p:
        problems.append(f"{len(long_p)} 段導讀超過 {PARAGRAPH_SENTENCES} 句：" + "；".join(long_p[:5]))
    if long_s:
        problems.append(f"{len(long_s)} 句超過 {SENTENCE_LIMIT} 字，拆成短句：" + "；".join(x[:24] + "…" for x in long_s[:8]))
    if long_f:
        problems.append(f"{len(long_f)} 個知識點欄位超過 {FIELD_SENTENCES} 句：" + "；".join(long_f[:5]))
    if inline:
        problems.append(f"{len(inline)} 處把出處寫在句子裡的括號中，改放到該段最後的 <p class=\"src\"> 或 <span class=\"cite\">：" + "；".join(x + "…" for x in inline[:5]))
    coined = sorted(set(COINED.findall(_plain(src))))
    if coined:
        problems.append("頁面自己取了名字（" + "、".join(coined) + "）：改用論文的名詞或標準名詞，第一次出現時用一句白話解釋")
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
            verdict = "無示範"
            if s["formula"]:
                verdict = "未通過"
                bad += 1
        elif s["controls"] and s["changed"] == s["controls"] and cs and ok_checks == len(cs) and anim_ok and not res["errors"]:
            verdict = "通過"
        else:
            verdict = "未通過"
            bad += 1
        extra = f" 沒反應: {', '.join(s['unchanged'])}" if s["unchanged"] else ""
        extra += "".join(f" 對照失敗: {c['name']}" for c in cs if not c["ok"])
        if s["demo"] and not cs:
            extra += " 沒有手算對照"
        if not anim_ok:
            extra += " 有公式但沒有可逐步播放的公式動畫"
        anim = f"動畫 {s['animSteps']} 步" if s["anim"] else ("動畫 缺" if s["formula"] else "動畫 —")
        tag = "［傳統作法］" if s["traditional"] else ""
        print(f"{s['kp']}\t{verdict}\t控制項 {s['changed']}/{s['controls']}\t手算 {ok_checks}/{len(cs)}\t{anim}\t{tag}{s['title']}{extra}")
    if not any(s["traditional"] for s in res["sections"]):
        bad += 1
        print("未通過：沒有任何知識點示範傳統作法（data-traditional=\"1\"）")
    if res["mapMissing"]:
        bad += 1
        print("未通過：地圖上有、頁面沒有的知識點:", ", ".join(res["mapMissing"]))
    f = res.get("formulas", {})
    problems = []
    if not f.get("sections"):
        problems.append("沒有任何公式節（section.eq-sec）")
    if not f.get("mapNodes"):
        problems.append("沒有公式關係圖（PR.formulaMap）")
    if f.get("brokenLinks"):
        problems.append("關係圖方塊連到不存在的位置: " + ", ".join(f["brokenLinks"]))
    if f.get("notOnMap"):
        problems.append("公式節不在關係圖上: " + ", ".join(f["notOnMap"]))
    if f.get("symbols", 0) < 1:
        problems.append("符號速查表是空的")
    if f.get("texErrors"):
        problems.append(f"{f['texErrors']} 個公式排版錯誤（.katex-error）")
    if f.get("texFallback"):
        problems.append(f"{f['texFallback']} 個公式沒有排版（katex/ 沒有載入）")
    keys = res.get("keyFormulas", [])
    if f.get("sections") and not keys:
        problems.append("沒有核心公式卡（.keyeq）：從公式清單選 1 到 5 個，放進對應知識點的示範之後")
    if len(keys) > 5:
        problems.append(f"核心公式 {len(keys)} 個，上限 5 個；其餘公式只放附錄")
    for k in keys:
        where = f"核心公式卡（{k['kp'] or '不在知識點裡'}）"
        if not k["kp"]:
            problems.append(where + "應放在知識點區塊內")
            continue
        if not k["formulaKp"]:
            problems.append(where + "所在的知識點沒有公式動畫（data-formula=\"1\"），讀者看不到代入數字的過程")
        if not k["afterDemo"]:
            problems.append(where + "應放在示範之後：先操作、看數字，再看一般式")
        if not k["plain"]:
            problems.append(where + "缺少一句白話（.plain）")
        if not k["words"]:
            problems.append(where + "的白話沒有著色關鍵詞（w-a 到 w-d）")
        if k["unmatched"]:
            problems.append(where + "的關鍵詞在公式裡沒有同色的項: " + "、".join(k["unmatched"]))
        elif k["words"] and not k["hover"]:
            problems.append(where + "指向關鍵詞時，公式沒有標出對應的項")
        if not k["typeset"]:
            problems.append(where + "的公式沒有排版")
    if res.get("storyFormulas"):
        problems.append(f"重點整理、故事線或論文群比較裡有 {res['storyFormulas']} 個獨立公式；公式只放在知識點或附錄")
    if not res.get("overviewInAppendix", True):
        problems.append("公式關係圖應放在附錄（#appendix），不要放在頁首")
    print(f"公式：核心 {len(keys)} 個（上限 5）；附錄 {f.get('sections', 0)} 節、關係圖 {f.get('mapNodes', 0)} 個方塊、符號 {f.get('symbols', 0)} 個")
    t = res.get("terms", {})
    if not t.get("count"):
        problems.append("沒有名詞表：在 demos.js 用 PR.terms({...}) 列出本頁的專有名詞，每個附一句白話")
    for x in t.get("late", []):
        problems.append(f"「{x['term']}」在解釋之前就出現了：…{x['context']}…")
    for k in t.get("notExplained", []):
        problems.append(f"「{k}」在頁面上用到，但沒有在第一次出現時用 <dfn data-term> 解釋")
    for k in t.get("dfnNotListed", []):
        problems.append(f"<dfn data-term=\"{k}\"> 不在名詞表裡")
    if t.get("unlisted"):
        problems.append("開頭與故事線用了沒列入名詞表的術語：" + "、".join(t["unlisted"][:30]))
    (work / "verify" / "reading_text.txt").write_text(res.get("readingText", ""), encoding="utf-8")
    cold = work / "verify" / "cold_read.md"
    if not cold.exists():
        problems.append("冷讀測試沒有執行：依 references/cold-read.md 派一個不看論文的讀者讀 _work/verify/reading_text.txt")
    elif cold.stat().st_mtime < page.stat().st_mtime:
        problems.append("index.html 在最後一次冷讀測試之後又改過；請再做一輪冷讀測試")
    else:
        text = cold.read_text(encoding="utf-8")
        for head, what in (("## 看不懂的地方", "看不懂"), ("## 可以刪掉的地方", "可以刪掉")):
            if head not in text:
                continue
            part = text.split(head, 1)[-1].split("\n## ", 1)[0]
            items = [ln for ln in part.splitlines() if ln.strip().startswith("- ")]
            if items:
                problems.append(f"冷讀測試還有 {len(items)} 處{what}（{cold}）")
    print(f"名詞：{t.get('count', 0)} 個；冷讀文字 -> {work / 'verify' / 'reading_text.txt'}")
    figs = res.get("figures", [])
    for fg in figs:
        if not fg["ok"]:
            problems.append("論文圖用了截圖，應改用 fig<N>-real.*: " + fg["src"])
        elif not fg["loaded"]:
            problems.append("論文圖載入失敗: " + fg["src"])
        elif not fg.get("popup"):
            problems.append("點論文圖沒有開出彈窗: " + fg["src"])
    print(f"論文圖：{len(figs)} 張，真實圖檔 {sum(f['ok'] for f in figs)} 張")
    tp, story_len = text_problems(page.read_text(encoding="utf-8"))
    problems += tp
    print(f"閱讀量：導讀 {story_len} 字（上限 {STORY_LIMIT}），句長上限 {SENTENCE_LIMIT} 字")
    for p in problems:
        bad += 1
        print("未通過：" + p)
    if res.get("unconfirmed"):
        bad += 1
        print(f"未通過：頁面上有 {len(res['unconfirmed'])} 處未確認的內容，應查證後改寫，或移到論文筆記：")
        for u in res["unconfirmed"][:20]:
            print("  …" + u + "…")
    if res["errors"]:
        bad += 1
        print("頁面錯誤:", "; ".join(res["errors"][:5]))
    print(f"{len(res['sections'])} 個知識點，{bad} 項未通過 -> {work / 'verify' / 'check.json'}")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
