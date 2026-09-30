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
map, an empty symbol table, a KaTeX error or an untypeset formula), when no
section is marked data-traditional="1",
a map entry has no section, or the text contains unconfirmed wording
(尚未確認, 待驗證, 還沒確認), which belongs in the paper notes instead.
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
    print(f"公式：{f.get('sections', 0)} 節、關係圖 {f.get('mapNodes', 0)} 個方塊、符號 {f.get('symbols', 0)} 個")
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
