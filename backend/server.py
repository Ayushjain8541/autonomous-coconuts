#!/usr/bin/env python3
"""Local-only bootstrap server. Fixture connectivity is not product completion."""
import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ml import classify_encounter

ASSETS = {"/": ("index.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
          "/styles.css": ("styles.css", "text/css; charset=utf-8")}


def demo_analysis():
    data = json.loads((ROOT / "contracts/fixtures/analysis-demo.json").read_text())
    for event in data["encounters"]:
        event.update(classify_encounter(event["predicted_pc"], event["miss_distance_m"]))
    return data


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data, content_type="application/json; charset=utf-8"):
        body = json.dumps(data, allow_nan=False).encode() if isinstance(data, dict) else data
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def error(self, status, code, message):
        self.reply(status, {"error": {"code": code, "message": message, "details": []}})

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/health":
            return self.reply(200, {"status": "ok", "mode": "bootstrap_fixture",
                                   "model": "unavailable", "insights": "unconfigured"})
        if path == "/api/demo":
            return self.reply(200, demo_analysis())
        if path in ASSETS:
            name, mime = ASSETS[path]
            return self.reply(200, (ROOT / "web" / name).read_bytes(), mime)
        self.error(404, "NOT_FOUND", "Route not found")

    def do_POST(self):
        # Close rejected request connections so unread bodies cannot become a next request.
        self.close_connection = True
        path = urlsplit(self.path).path
        if path == "/api/analyses":
            return self.error(503, "MODEL_UNAVAILABLE", "Upload analysis is not implemented in this bootstrap. P2/P3 own the real CSV/model path.")
        if path.startswith("/api/analyses/") and path.endswith("/insights"):
            return self.error(503, "INSIGHTS_UNAVAILABLE", "No live LLM provider is configured. Deterministic demo data remains available.")
        self.error(404, "NOT_FOUND", "Route not found")

    def log_message(self, format_string, *args):
        pass


def make_server(host="127.0.0.1", port=8000):
    return ThreadingHTTPServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("COCONUTS_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("COCONUTS_PORT", "8000")))
    args = parser.parse_args()
    with make_server(args.host, args.port) as server:
        print("Bootstrap fixture: http://%s:%s" % (args.host, server.server_port), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
