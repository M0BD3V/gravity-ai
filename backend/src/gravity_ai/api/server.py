from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from gravity_ai.api.app import ApplicationContext


def run_server(host: str = "127.0.0.1", port: int = 8765, root_dir: str | None = None) -> None:
    context = ApplicationContext.create(root_dir=root_dir, persist=True)
    handler = _make_handler(context)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Gravity AI API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    finally:
        context.close()
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Gravity AI local API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--root-dir", default=None)
    args = parser.parse_args(argv)
    run_server(host=args.host, port=args.port, root_dir=args.root_dir)
    return 0


def _make_handler(context: ApplicationContext):
    class GravityRequestHandler(BaseHTTPRequestHandler):
        server_version = "GravityAI/0.1"

        def do_OPTIONS(self) -> None:  # noqa: N802
            self._send_json(HTTPStatus.NO_CONTENT, {})

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/health":
                self._send_json(HTTPStatus.OK, context.health())
                return
            if path == "/tools":
                self._send_json(HTTPStatus.OK, context.list_tools())
                return
            if path == "/plugins":
                self._send_json(HTTPStatus.OK, context.list_plugins())
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": f"Unknown route: {path}"})

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            payload = self._read_json()
            if path == "/chat":
                self._send_json(HTTPStatus.OK, context.chat(payload))
                return
            if path == "/tools/execute":
                self._send_json(HTTPStatus.OK, context.execute_tool(payload))
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": f"Unknown route: {path}"})

        def log_message(self, format: str, *args: Any) -> None:
            print(f"[api] {self.address_string()} - {format % args}")

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            if length == 0:
                return {}
            raw = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                return {}
            return payload if isinstance(payload, dict) else {}

        def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "content-type")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if status != HTTPStatus.NO_CONTENT:
                self.wfile.write(body)

    return GravityRequestHandler

