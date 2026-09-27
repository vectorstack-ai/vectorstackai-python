import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from vectorstackai.api_resources import Embedding, Index


class MockAPI:
    """Local HTTP server that replays scripted responses and records requests."""

    def __init__(self):
        self.responses = []
        self.requests = []
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.base_url = f"http://127.0.0.1:{self._server.server_address[1]}/"
        threading.Thread(target=self._server.serve_forever, daemon=True).start()

    def respond(self, status=200, body=None, headers=None, delay=0.0):
        """Queue a response. The last queued response repeats once the queue drains."""
        if not isinstance(body, (bytes, str)):
            body = json.dumps({} if body is None else body)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.responses.append((status, body, headers or {}, delay))

    @property
    def hits(self):
        return len(self.requests)

    def close(self):
        self._server.shutdown()
        self._server.server_close()

    def _handler(self):
        mock = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _handle(self):
                length = int(self.headers.get("Content-Length") or 0)
                mock.requests.append((self.command, self.path, self.rfile.read(length)))
                status, body, headers, delay = (
                    mock.responses.pop(0) if len(mock.responses) > 1 else mock.responses[0]
                )
                if delay:
                    time.sleep(delay)
                try:
                    self.send_response(status)
                    self.send_header("Content-Length", str(len(body)))
                    for name, value in headers.items():
                        self.send_header(name, value)
                    self.end_headers()
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass  # client gave up (e.g. timed out)

            do_GET = do_POST = do_DELETE = _handle

        return Handler


@pytest.fixture
def api(monkeypatch):
    """Point every API resource at a local mock server."""
    mock = MockAPI()
    monkeypatch.setattr(Embedding, "CLASS_URL", mock.base_url + "embeddings")
    monkeypatch.setattr(Index, "CLASS_URL", mock.base_url + "precise_search/")
    yield mock
    mock.close()
