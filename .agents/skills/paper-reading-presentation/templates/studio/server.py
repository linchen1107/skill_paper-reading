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
    title      what the user sees, for example "OOD detection on real SST-2 sentences"
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
# The server adds "provenance" and "elapsed_ms".


_USED_CACHE = []


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
    start = time.perf_counter()
    result = item["fn"](params)
    result["elapsed_ms"] = round((time.perf_counter() - start) * 1000)
    result["params"] = params
    result["provenance"] = {
        "live": f"Computed for this request on this machine in {result['elapsed_ms']} ms.",
        "cached": [dict(m) for m in _USED_CACHE],
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
            return self.send_json({"error": f"no lab named {name!r}"}, 404)
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
    sys.exit(f"no free port between {start} and {start + 49}")


def main():
    ap = argparse.ArgumentParser(description="paper-reading lab backend")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()
    port = free_port(args.port)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port),
                                             functools.partial(Handler, directory=str(TOPIC)))
    url = f"http://127.0.0.1:{port}/studio/lab.html"
    print(f"Labs:    {url}\nReading: http://127.0.0.1:{port}/index.html\nStop with Ctrl+C", flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("stopped")


# ============================== LABS ==============================
# Replace the example below with the labs confirmed in Step 0.

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


@lab("example", title="Example: keeping an edge while removing noise",
     question="A median filter keeps a step edge that a moving average blurs (template example; replace it).",
     source="template example",
     params=[{"key": "sample", "label": "Sample", "type": "sample", "value": 1,
              "options": [{"value": s, "label": f"Signal {s}"} for s in range(1, 6)]},
             {"key": "noise", "label": "Noise level", "type": "range", "min": 0.05, "max": 0.8, "step": 0.05,
              "value": 0.2, "help": "Standard deviation of the added noise"},
             {"key": "window", "label": "Window", "type": "range", "min": 3, "max": 31, "step": 2, "value": 9}],
     knowledge=())
def example(p):
    clean, noisy = _signal(p["sample"], p["noise"])
    ma, md = _moving_average(noisy, p["window"]), _median(noisy, p["window"])
    e_ma, e_md = _rmse(ma, clean), _rmse(md, clean)
    x = list(range(len(clean)))
    better = "median filter" if e_md < e_ma else "moving average"
    failures = [{"title": f"Signal {s}", "detail": "moving average wins here", "sample": s}
                for s in range(1, 6)
                if _rmse(_moving_average(_signal(s, p["noise"])[1], p["window"]), _signal(s, p["noise"])[0])
                < _rmse(_median(_signal(s, p["noise"])[1], p["window"]), _signal(s, p["noise"])[0])]
    return {
        "summary": f"On signal {p['sample']}, the {better} is closer to the clean signal "
                   f"(RMSE {min(e_ma, e_md):.3f} vs {max(e_ma, e_md):.3f}).",
        "input": {"title": "Noisy input and the clean signal",
                  "plot": {"title": "Input", "xlabel": "sample index", "ylabel": "value",
                           "series": [{"name": "noisy", "x": x, "y": noisy}, {"name": "clean", "x": x, "y": clean, "dashed": True}]}},
        "methods": [
            {"name": "Moving average", "kind": "traditional",
             "metric": {"label": "RMSE", "value": round(e_ma, 4), "better": "lower"},
             "plot": {"title": "Moving average", "series": [{"name": "output", "x": x, "y": ma}, {"name": "clean", "x": x, "y": clean, "dashed": True}]}},
            {"name": "Median filter", "kind": "paper",
             "metric": {"label": "RMSE", "value": round(e_md, 4), "better": "lower"},
             "plot": {"title": "Median filter", "series": [{"name": "output", "x": x, "y": md}, {"name": "clean", "x": x, "y": clean, "dashed": True}]}},
        ],
        "failures": failures,
        "note": "Generated signals; this example only shows the lab contract.",
    }


@check("moving average of [1, 2, 3] with window 3 at the centre = 2")
def _check_ma():
    return 2.0, _moving_average([1.0, 2.0, 3.0], 3)[1], 1e-9


if __name__ == "__main__":
    main()
