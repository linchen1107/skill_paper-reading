"""Open a paper-reading page at a local web address instead of a file path.

Usage (copied into each topic folder):  python serve.py [--port N] [--no-open]

Serves this folder on 127.0.0.1 at a free port (8000 or the next free one) and
opens index.html in the default browser. If the folder also has the backend of
paper-reading:presentation (studio/server.py), that backend is started instead,
since it serves the same folder together with its lab endpoints.
Python standard library only. Stop with Ctrl+C.
"""
import argparse
import functools
import http.server
import runpy
import socket
import sys
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent


def free_port(start):
    for port in range(start, start + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    sys.exit(f"no free port between {start} and {start + 49}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-open", action="store_true", help="do not open the browser")
    args = ap.parse_args()

    backend = HERE / "studio" / "server.py"
    if backend.exists():
        print(f"studio/server.py found: starting the presentation backend, which serves this folder too")
        sys.argv = [str(backend)] + (["--no-open"] if args.no_open else [])
        runpy.run_path(str(backend), run_name="__main__")
        return

    port = free_port(args.port)
    class Handler(http.server.SimpleHTTPRequestHandler):
        # notes open as text in the browser instead of downloading; fonts get their own type
        extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                          ".md": "text/plain; charset=utf-8", ".woff2": "font/woff2",
                          ".svg": "image/svg+xml", ".js": "text/javascript; charset=utf-8"}

        def log_message(self, *a):  # keep the console quiet
            pass

    handler = functools.partial(Handler, directory=str(HERE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{port}/index.html"
    print(f"Serving {HERE}\nOpen {url}\nStop with Ctrl+C", flush=True)
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
