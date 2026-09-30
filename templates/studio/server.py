"""Lab backend for paper-reading:presentation.

Start:   python studio/server.py            (or: python serve.py in the topic folder)
Options: --port N (first port to try, default 8000), --no-open

Serves the whole topic folder on 127.0.0.1 (the reading page, the figures and
studio/lab.html share one address) and one JSON endpoint per lab:

  GET  /api/labs           the labs and their parameters (lab.html builds its controls from this)
  POST /api/labs/<name>    run one lab with the posted parameters, return its result
  GET  /api/checks         run every registered reference check

A run edits only the part below "LABS": one function per lab, registered with
@lab(...), plus @check(...) for the hand calculations it must reproduce.
Standard library only unless a lab needs more.
"""
import argparse
import datetime
import functools
import hashlib
import http.server
import json
import pickle
import socket
import sys
import time
import traceback
import urllib.request
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

STUDIO = Path(__file__).resolve().parent
TOPIC = STUDIO.parent
DATA = STUDIO / "data"
CACHE = STUDIO / "_work" / "cache"

LABS, CHECKS = {}, []


def lab(name, title, question, source, params, knowledge=()):
    """Register a lab.

    name       short id used in the address, for example "ood"
    title      what the user sees, in Traditional Chinese, for example "真實 SST-2 句子上的 OOD 偵測"
    question   the claim or failure of the paper this lab tests, one sentence
    source     where in the paper, for example "Table V, Fig. 5"
    params     list of controls:
               {"key", "label", "type": "range", "min", "max", "step", "value", "help"}
               {"key", "label", "type": "select", "options": [...], "value"}
               {"key", "label", "type": "check", "value": False}
               {"key", "label", "type": "sample", "options": [{"value", "label"}], "value"}
    knowledge  the reading page's knowledge points it exercises, for example ("A4", "B2")

    The function takes the parameters as a dict and returns a dict (see RESULT below).
    """
    def deco(fn):
        LABS[name] = {"name": name, "title": title, "question": question, "source": source,
                      "params": params, "knowledge": list(knowledge), "fn": fn}
        return fn
    return deco


def check(name):
    """Register a reference check: the function returns (expected, actual, tolerance)."""
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


# RESULT returned by a lab function; every key is optional except "summary":
# {
#   "summary":  "one sentence: what happened on this input",
#   "input":    {"title": "...", "plot": PLOT | "image": "path under the topic folder" | "text": "..."},
#   "methods":  [{"name": "Moving average", "kind": "traditional" | "paper",
#                 "metric": {"label": "RMSE", "value": 0.12, "better": "lower" | "higher"},
#                 "plot": PLOT, "text": "..."}],
#   "table":    [["header", ...], [row], ...],
#   "failures": [{"title": "...", "detail": "why it fails here", "sample": value to load it}],
#   "note":     "limits of this lab",
# }
# PLOT is the reading page's plot spec: {"title", "xlabel", "ylabel", "type": "line" | "bar" | "heatmap",
#   "series": [{"name", "x", "y", "dashed"}]} or {"type": "heatmap", "z": [[...]]}.
# The server adds "provenance" (live, cached, remote) and "elapsed_ms".


_USED_CACHE, _USED_REMOTE = [], []


def remote(url, payload=None, about="", timeout=600):
    """Call a backend the project already has and return its JSON, instead of copying its code.

    url      for example "http://127.0.0.1:5160/api/estimate"; GET without payload, POST with one
    about    one sentence for the page, for example "既有套件：每件 3 票時的錯誤率估計"
    The page states that these numbers were computed by that backend, with its address and time.
    If it is not running, the lab fails with a message that names the address.
    """
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            value = json.loads(r.read())
    except OSError as e:
        raise RuntimeError(f"專案既有的後端 {url} 沒有回應（{e}）；請先啟動它") from None
    _USED_REMOTE.append({"url": url, "about": about or url, "ms": round((time.perf_counter() - start) * 1000)})
    return value


def cached(key, compute, about):
    """Compute an expensive intermediate result once on this machine and reuse it.

    key      a string naming the inputs, for example "hidden-states/qwen0.5b/layer23"
    compute  a function with no arguments
    about    one sentence for the page, for example "hidden states of Qwen2.5-0.5B, layer 23"
    The page then says which parts of a result came from this cache and when it was computed.
    """
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha1(key.encode()).hexdigest()[:16] + ".pkl")
    if path.exists():
        with path.open("rb") as f:
            stored = pickle.load(f)
    else:
        start = time.time()
        value = compute()
        stored = {"value": value, "meta": {"about": about, "key": key,
                  "computed": datetime.datetime.now().isoformat(timespec="minutes"),
                  "seconds": round(time.time() - start, 1)}}
        with path.open("wb") as f:
            pickle.dump(stored, f)
    _USED_CACHE.append(stored["meta"])
    return stored["value"]


def clean_params(spec, posted):
    """Keep only known parameters, clamp numbers to their range, fall back to defaults."""
    out = {}
    for p in spec:
        v = posted.get(p["key"], p.get("value"))
        if p["type"] == "range":
            try:
                v = float(v)
            except (TypeError, ValueError):
                v = float(p["value"])
            v = min(max(v, p["min"]), p["max"])
            if float(p.get("step", 1)).is_integer() and float(p["min"]).is_integer():
                v = int(round(v))
        elif p["type"] == "check":
            v = bool(v)
        elif p["type"] in ("select", "sample"):
            allowed = [o["value"] if isinstance(o, dict) else o for o in p["options"]]
            v = v if v in allowed else p["value"]
        out[p["key"]] = v
    return out


def run_lab(name, posted):
    item = LABS[name]
    params = clean_params(item["params"], posted)
    _USED_CACHE.clear()
    _USED_REMOTE.clear()
    start = time.perf_counter()
    result = item["fn"](params)
    result["elapsed_ms"] = round((time.perf_counter() - start) * 1000)
    result["params"] = params
    result["provenance"] = {
        "live": f"這次操作在這台電腦即時計算，耗時 {result['elapsed_ms']} ms。",
        "cached": [dict(m) for m in _USED_CACHE],
        "remote": [dict(m) for m in _USED_REMOTE],
    }
    return result


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".md": "text/plain; charset=utf-8", ".woff2": "font/woff2",
                      ".svg": "image/svg+xml", ".js": "text/javascript; charset=utf-8"}

    def log_message(self, *a):
        pass

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False, default=float).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/studio/lab.html")
            self.end_headers()
        elif path == "/api/labs":
            self.send_json([{k: v for k, v in item.items() if k != "fn"} for item in LABS.values()])
        elif path == "/api/checks":
            rows = []
            for name, fn in CHECKS:
                try:
                    expected, actual, tol = fn()
                    ok = abs(actual - expected) <= tol * max(1, abs(expected))
                    rows.append({"name": name, "expected": expected, "actual": actual, "ok": ok})
                except Exception as e:  # a failing check is reported, not hidden
                    rows.append({"name": name, "ok": False, "error": str(e)})
            self.send_json(rows)
        else:
            super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        name = path.removeprefix("/api/labs/")
        if not path.startswith("/api/labs/") or name not in LABS:
            return self.send_json({"error": f"沒有名為 {name!r} 的實驗"}, 404)
        try:
            length = int(self.headers.get("Content-Length") or 0)
            posted = json.loads(self.rfile.read(length) or b"{}")
            self.send_json(run_lab(name, posted))
        except Exception as e:
            self.send_json({"error": f"{type(e).__name__}: {e}",
                            "trace": traceback.format_exc().splitlines()[-6:]}, 500)


def free_port(start):
    for port in range(start, start + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    sys.exit(f"{start} 到 {start + 49} 之間沒有可用的埠號")


def main():
    ap = argparse.ArgumentParser(description="paper-reading lab backend")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    port = free_port(args.port)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port),
                                             functools.partial(Handler, directory=str(TOPIC)))
    url = f"http://127.0.0.1:{port}/studio/lab.html"
    print(f"實驗頁：{url}\n閱讀頁：http://127.0.0.1:{port}/index.html\n按 Ctrl+C 停止", flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("已停止")


# ============================== LABS ==============================
# Replace the example below with the labs confirmed in Step 0. Page text (titles, labels, summaries,
# notes) is written in Traditional Chinese as used in Taiwan. When the project already has a backend,
# a lab calls it with remote(...) instead of copying its code.

import math
import random


def _signal(seed, noise, n=200):
    r = random.Random(seed)
    clean = [1.0 if 60 <= i < 140 else 0.0 for i in range(n)]
    return clean, [c + r.gauss(0, noise) for c in clean]


def _moving_average(x, w):
    h = w // 2
    return [sum(x[max(0, i - h):i + h + 1]) / len(x[max(0, i - h):i + h + 1]) for i in range(len(x))]


def _median(x, w):
    h = w // 2
    return [sorted(x[max(0, i - h):i + h + 1])[len(x[max(0, i - h):i + h + 1]) // 2] for i in range(len(x))]


def _rmse(a, b):
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(a, b)) / len(a))


@lab("example", title="範例：去除雜訊時保留邊緣",
     question="中位數濾波能保留階梯邊緣，移動平均則會把它抹平（範本範例，正式執行時換掉）。",
     source="範本範例",
     params=[{"key": "sample", "label": "樣本", "type": "sample", "value": 1,
              "options": [{"value": s, "label": f"訊號 {s}"} for s in range(1, 6)]},
             {"key": "noise", "label": "雜訊強度", "type": "range", "min": 0.05, "max": 0.8, "step": 0.05,
              "value": 0.2, "help": "加入的雜訊的標準差"},
             {"key": "window", "label": "視窗長度", "type": "range", "min": 3, "max": 31, "step": 2, "value": 9}],
     knowledge=())
def example(p):
    clean, noisy = _signal(p["sample"], p["noise"])
    ma, md = _moving_average(noisy, p["window"]), _median(noisy, p["window"])
    e_ma, e_md = _rmse(ma, clean), _rmse(md, clean)
    x = list(range(len(clean)))
    better = "中位數濾波" if e_md < e_ma else "移動平均"
    failures = [{"title": f"訊號 {s}", "detail": "這裡移動平均比較好", "sample": s}
                for s in range(1, 6)
                if _rmse(_moving_average(_signal(s, p["noise"])[1], p["window"]), _signal(s, p["noise"])[0])
                < _rmse(_median(_signal(s, p["noise"])[1], p["window"]), _signal(s, p["noise"])[0])]
    return {
        "summary": f"在訊號 {p['sample']} 上，{better}比較接近乾淨訊號"
                   f"（RMSE {min(e_ma, e_md):.3f} 對 {max(e_ma, e_md):.3f}）。",
        "input": {"title": "含雜訊的輸入與乾淨訊號",
                  "plot": {"title": "輸入", "xlabel": "樣本索引", "ylabel": "數值",
                           "series": [{"name": "含雜訊", "x": x, "y": noisy}, {"name": "乾淨", "x": x, "y": clean, "dashed": True}]}},
        "methods": [
            {"name": "移動平均", "kind": "traditional",
             "metric": {"label": "RMSE", "value": round(e_ma, 4), "better": "lower"},
             "plot": {"title": "移動平均", "series": [{"name": "輸出", "x": x, "y": ma}, {"name": "乾淨", "x": x, "y": clean, "dashed": True}]}},
            {"name": "中位數濾波", "kind": "paper",
             "metric": {"label": "RMSE", "value": round(e_md, 4), "better": "lower"},
             "plot": {"title": "中位數濾波", "series": [{"name": "輸出", "x": x, "y": md}, {"name": "乾淨", "x": x, "y": clean, "dashed": True}]}},
        ],
        "failures": failures,
        "note": "程式產生的訊號；這個範例只示範實驗的回傳格式。",
    }


@check("[1, 2, 3] 以視窗 3 做移動平均，中間值 = 2")
def _check_ma():
    return 2.0, _moving_average([1.0, 2.0, 3.0], 3)[1], 1e-9


if __name__ == "__main__":
    main()
