"""HTTP server plumbing for the framework bucket."""

from __future__ import annotations

import json
import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from workspace.app import ROUTES, ApiError


REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_STATIC_DIR = REPO_ROOT / "workspace" / "static"
FRAMEWORK_STATIC_DIR = REPO_ROOT / "framework" / "static"
LOOPBACK_HOST = "127.0.0.1"
PORT = int(os.environ.get("AURELIAN_PORT", "8000"))


def network_bind_allowed() -> bool:
    return (
        os.environ.get("AURELIAN_ALLOW_NETWORK_BIND") == "1"
        or bool(os.environ.get("CODESPACES"))
        or bool(os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"))
    )


def resolve_host() -> str:
    requested_host = os.environ.get("AURELIAN_HOST", LOOPBACK_HOST).strip() or LOOPBACK_HOST
    if requested_host in {LOOPBACK_HOST, "localhost"}:
        return LOOPBACK_HOST

    if not network_bind_allowed():
        print(
            "Ignoring AURELIAN_HOST outside Codespaces to keep the starter local-only. "
            "Set AURELIAN_ALLOW_NETWORK_BIND=1 to expose it intentionally."
        )
        return LOOPBACK_HOST

    return requested_host


def display_host(host: str) -> str:
    if host == LOOPBACK_HOST:
        return "localhost"
    return host


HOST = resolve_host()


def match_pattern(pattern: str, path: str) -> dict[str, str] | None:
    pattern_parts = pattern.strip("/").split("/")
    path_parts = path.strip("/").split("/")
    if len(pattern_parts) != len(path_parts):
        return None
    params: dict[str, str] = {}
    for pat, actual in zip(pattern_parts, path_parts):
        if pat.startswith("{") and pat.endswith("}"):
            params[pat[1:-1]] = actual
        elif pat != actual:
            return None
    return params


def match_route(
    method: str,
    path: str,
) -> tuple[Any, dict[str, str], int] | tuple[None, None, None]:
    for route_method, route_pattern, handler, status_code in ROUTES:
        if route_method != method:
            continue
        params = match_pattern(route_pattern, path)
        if params is not None:
            return handler, params, status_code
    return None, None, None


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "AurelianStarter/1.0"

    def do_GET(self) -> None:  # noqa: N802
        self.handle_request("GET")

    def do_POST(self) -> None:  # noqa: N802
        self.handle_request("POST")

    def do_PATCH(self) -> None:  # noqa: N802
        self.handle_request("PATCH")

    def log_message(self, format: str, *args: object) -> None:
        return

    def handle_request(self, method: str) -> None:
        parsed = urlparse(self.path)
        try:
            if not parsed.path.startswith("/api/"):
                if method != "GET":
                    raise ApiError(HTTPStatus.METHOD_NOT_ALLOWED, "Method not allowed")
                self.serve_static(parsed.path)
                return

            payload = self.read_json_body() if method in {"POST", "PATCH"} else None
            response_body, status_code = self.route_api(method, parsed.path, payload)
            self.write_json(status_code, response_body)
        except ApiError as error:
            self.write_json(error.status_code, {"detail": error.detail})

    def route_api(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None,
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], int]:
        handler, params, status_code = match_route(method, path)
        if handler is None:
            raise ApiError(HTTPStatus.NOT_FOUND, "Not found")
        kwargs: dict[str, Any] = dict(params)
        if payload is not None:
            kwargs["payload"] = payload
        return handler(**kwargs), status_code

    def read_json_body(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        if not raw_body:
            return {}
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as error:
            raise ApiError(HTTPStatus.BAD_REQUEST, "Request body must be valid JSON") from error
        if not isinstance(payload, dict):
            raise ApiError(HTTPStatus.BAD_REQUEST, "Request body must be a JSON object")
        return payload

    def serve_static(self, path: str) -> None:
        if path in {"", "/"}:
            static_path = FRAMEWORK_STATIC_DIR / "index.html"
        elif path in {"/app.js", "/styles.css"}:
            static_path = WORKSPACE_STATIC_DIR / path.lstrip("/")
        elif path.startswith("/vendor/") and ".." not in path:
            static_path = FRAMEWORK_STATIC_DIR / path.lstrip("/")
        else:
            raise ApiError(HTTPStatus.NOT_FOUND, "Not found")

        if not static_path.exists():
            raise ApiError(HTTPStatus.NOT_FOUND, "Not found")

        content_type, _ = mimetypes.guess_type(static_path.name)
        if content_type is None:
            content_type = "application/octet-stream"
        body = static_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def write_json(self, status_code: int, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = HOST, port: int = PORT) -> None:
    server = ThreadingHTTPServer((host, port), RequestHandler)
    print(f"Aurelian starter workspace running at http://{display_host(host)}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()
