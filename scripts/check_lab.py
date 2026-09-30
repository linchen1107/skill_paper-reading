"""Check a topic's labs end to end: backend, endpoints and the lab page.

Usage: python check_lab.py <topic_dir>

Starts <topic>/studio/server.py on a free port, opens studio/lab.html?selftest in
the Chrome, Edge or Chromium already on the machine, and lets the page run every
lab with its defaults and with one changed setting through the real endpoints.
Then runs the backend's reference checks (@check), stops the backend and deletes
the browser profile. Prints one line per lab:
  通過     both settings computed without error, the results differ, the page rendered them
  未通過   an error, identical results for different settings, or nothing rendered
Writes <topic>/studio/_work/verify/check_lab.json. Exit status 1 when anything fails.
"""
import html
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_page import find_browser  # noqa: E402


def main(topic_dir):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    topic = Path(topic_dir).resolve()
    server = topic / "studio" / "server.py"
    if not server.exists():
        sys.exit(f"no studio/server.py in {topic}")
    browser = find_browser()
    if not browser:
        sys.exit("no Chrome, Edge or Chromium found; the labs cannot be checked here")
    work = topic / "studio" / "_work"
    (work / "verify").mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen([sys.executable, "-u", str(server), "--no-open", "--port", "8100"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            encoding="utf-8", errors="replace")
    profile = work / "tmp" / "check-profile"
    try:
        url = None
        deadline = time.time() + 120
        while time.time() < deadline and url is None:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    sys.exit("the backend stopped before it served anything")
                continue
            m = re.search(r"(http://127\.0\.0\.1:\d+)/studio/lab\.html", line)
            if m:
                url = m.group(1)
        if not url:
            sys.exit("the backend did not print its address within 120 s")
        checks = json.loads(urllib.request.urlopen(url + "/api/checks", timeout=600).read())
        run = subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={profile}",
             "--virtual-time-budget=600000", "--dump-dom", url + "/studio/lab.html?selftest"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)
    m = re.search(r'<pre id="lab-selftest">(.*?)</pre>', run.stdout, re.S)
    if not m:
        sys.exit("the lab page did not report; open it through the backend and look for an error")
    res = json.loads(html.unescape(m.group(1)))
    res["checks"] = checks
    (work / "verify" / "check_lab.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = 0
    for r in res["labs"]:
        verdict = "通過" if r.get("ok") else "未通過"
        bad += not r.get("ok")
        why = []
        if r.get("error"):
            why.append("錯誤: " + str(r["error"])[:120])
        if not r.get("changed", False):
            why.append("兩組設定結果相同")
        if not r.get("rendered", False):
            why.append("頁面沒有顯示結果")
        print(f"{r['lab']}\t{verdict}\t方法 {r.get('methods', 0)} 個\t{'；'.join(why)}")
    for c in checks:
        bad += not c.get("ok")
        print(f"對照\t{'通過' if c.get('ok') else '未通過'}\t{c['name']}\t{c.get('error', '')}")
    print(f"{len(res['labs'])} 個實驗、{len(checks)} 個對照，{bad} 項未通過 -> {work / 'verify' / 'check_lab.json'}")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
