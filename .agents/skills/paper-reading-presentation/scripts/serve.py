"""Open a paper-reading page at a local web address instead of a file path.

Usage (copied into each topic folder):  python serve.py [--port N] [--host ADDRESS] [--no-open]

Serves this folder on 127.0.0.1 (or --host, for example this machine's Tailscale
address when the browser runs elsewhere) at a free port (8000 or the next free one) and
opens index.html in the default browser. If the folder also has the backend of
paper-reading:presentation (studio/server.py), that backend is started instead,
since it serves the same folder together with its lab endpoints.
Python standard library only. Stop with Ctrl+C.
"""
import argparse
import functools
import http.server
import os
import runpy
import socket
import subprocess
import sys
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent


def free_port(host, start):
    for port in range(start, start + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    sys.exit(f"{start} 到 {start + 49} 之間沒有可用的埠號")


def remote_hint(host, port):
    """Over SSH the browser runs on another machine, which cannot open 127.0.0.1 of this one."""
    if host != "127.0.0.1" or not (os.environ.get("SSH_CONNECTION") or os.environ.get("SSH_CLIENT")):
        return ""
    ts = ""
    try:
        out = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=5)
        ts = out.stdout.split()[0] if out.returncode == 0 and out.stdout.split() else ""
    except (OSError, subprocess.SubprocessError):
        pass
    lines = ["這是遠端連線：你的瀏覽器開不到這台機器的 127.0.0.1。"]
    if ts:
        lines.append(f"  只給自己的 Tailscale 裝置看：加上 --host {ts}，網址會是 http://{ts}:{port}/")
    lines.append(f"  或在自己的電腦轉接：ssh -L {port}:127.0.0.1:{port} <帳號>@<這台機器>")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="127.0.0.1", help="address to listen on (default: this machine only)")
    ap.add_argument("--no-open", action="store_true", help="do not open the browser")
    args = ap.parse_args()

    backend = HERE / "studio" / "server.py"
    if backend.exists():
        print(f"studio/server.py found: starting the presentation backend, which serves this folder too")
        sys.argv = [str(backend), "--port", str(args.port), "--host", args.host] + (["--no-open"] if args.no_open else [])
        runpy.run_path(str(backend), run_name="__main__")
        return

    port = free_port(args.host, args.port)
    class Handler(http.server.SimpleHTTPRequestHandler):
        # notes open as text in the browser instead of downloading; fonts get their own type
        extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                          ".md": "text/plain; charset=utf-8", ".woff2": "font/woff2",
                          ".svg": "image/svg+xml", ".js": "text/javascript; charset=utf-8"}

        def log_message(self, *a):  # keep the console quiet
            pass

    handler = functools.partial(Handler, directory=str(HERE))
    server = http.server.ThreadingHTTPServer((args.host, port), handler)
    url = f"http://{args.host}:{port}/index.html"
    print(f"Serving {HERE}\nOpen {url}\nStop with Ctrl+C", flush=True)
    hint = remote_hint(args.host, port)
    if hint:
        print(hint, flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("stopped")


if __name__ == "__main__":
    main()
