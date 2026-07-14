"""
server.py — entrypoint for Hermes Dashboard

A zero‑dependency HTTP server for monitoring an Android Hermes setup.
Routes:
  /                    → SPA HTML (templates/index.html)
  /api/status          → battery, disk, RAM, uptime
  /api/cron            → cron jobs with countdown
  /api/tree?dir=<rel>  → file‑tree listing
  /api/read/<rel>      → file content
  /api/download/<rel>  → file download
  /api/log/<job_id>    → latest cron log
  /api/settings        → GET/POST Tuya credentials
"""
import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Ensure the project root is on sys.path so local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import PORT
from handlers.status import status_handler
from handlers.cron import cron_list_handler, log_handler
from handlers.files import tree_handler, read_handler
from handlers.settings import settings_handler
from handlers.tuya import tuya_test_handler, tuya_cmd_handler


def _load_html() -> str:
    """Read the SPA template once at startup."""
    path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    try:
        return open(path).read()
    except FileNotFoundError:
        return '<h1>index.html not found</h1>'


HTML = _load_html()


class Handler(SimpleHTTPRequestHandler):
    """Single‑file HTTP handler that dispatches to route handlers."""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        routes = {
            '/api/status': lambda: self._json(status_handler()),
            '/api/cron': lambda: self._json(cron_list_handler()),
        }

        if path in routes:
            routes[path]()

        elif path == '/api/tree':
            rel = (qs.get('dir', [''])[0] or '').strip()
            data = tree_handler(rel)
            if data is None:
                self._send(404, b'')
            else:
                self._json(data)

        elif path.startswith('/api/read/'):
            rel = urllib.parse.unquote(path[10:])
            data, ct = read_handler(rel)
            if data is None:
                self._send(ct or 404, b'')
            else:
                self._send(200, data, ct)

        elif path.startswith('/api/download/'):
            rel = urllib.parse.unquote(path[14:])
            data, ct = read_handler(rel)
            if data is None:
                self._send(ct or 404, b'')
            else:
                self._send(
                    200, data,
                    'application/octet-stream',
                    f'attachment; filename="{os.path.basename(rel)}"',
                )

        elif path.startswith('/api/log/'):
            content = log_handler(path[9:])
            self._send(
                200 if content else 404,
                (content or '').encode(),
            )

        elif path == '/api/settings':
            self._json(settings_handler())

        elif path == '/api/tuya-test':
            self._json(tuya_test_handler())

        else:
            # Everything else → SPA
            self._send(200, HTML.encode(), 'text/html;charset=utf-8')

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        data = json.loads(body) if body else {}

        if self.path == '/api/settings':
            self._json(settings_handler(body))
        elif self.path == '/api/tuya-test':
            cmd = data.get('cmd', 'status')
            if cmd == 'status':
                self._json(tuya_test_handler())
            elif cmd in ('on', 'off'):
                self._json(tuya_cmd_handler(cmd))
            else:
                self._send(400, b'Bad request')
        else:
            self._send(404, b'')

    # ─── helpers ───────────────────────────────────────────────────

    def _json(self, obj, status=200):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode(), 'application/json')

    def _send(self, status, body, content_type='text/plain;charset=utf-8', disposition='inline'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Disposition', disposition)
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body if isinstance(body, bytes) else body.encode())


if __name__ == '__main__':
    from config import HOST, PORT
    print(f'📊 Hermes Dashboard → http://localhost:{PORT}')
    server = HTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.server_close()
    except PermissionError:
        print(f'❌ Port {PORT} requires permission. Try a port >1024.')
        sys.exit(1)
    except OSError as e:
        print(f'❌ {e}')
        sys.exit(1)
