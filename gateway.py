import base64
import http.server
import os
import urllib.error
import urllib.request

UPSTREAM = "http://127.0.0.1:8080"
PORT = int(os.environ.get("PORT", "10000"))
AUTH_USER = os.environ["SEARX_AUTH_USER"]
AUTH_PASSWORD = os.environ["SEARX_AUTH_PASSWORD"]


class ThreadedHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def authorized(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False

        try:
            decoded = base64.b64decode(header[6:]).decode("utf-8")
            user, password = decoded.split(":", 1)
            return user == AUTH_USER and password == AUTH_PASSWORD
        except Exception:
            return False

    def send_body(self, status, body=b"", content_type="text/plain; charset=utf-8",
                  headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")

        if headers:
            for key, value in headers.items():
                self.send_header(key, value)

        self.end_headers()

        if body:
            self.wfile.write(body)

    def do_GET(self):
        # Render health check intentionally does not require credentials.
        if self.path == "/healthz":
            self.send_body(
                200,
                b'{"ok":true,"service":"leadhunter-searxng","status":"healthy"}',
                "application/json",
            )
            return

        if not self.authorized():
            self.send_body(
                401,
                b"",
                headers={
                    "WWW-Authenticate": 'Basic realm="LeadHunter Search"'
                },
            )
            return

        target = UPSTREAM + self.path

        request = urllib.request.Request(
            target,
            headers={
                "User-Agent": "LeadHunter-Research-Worker/1.0",
                "Accept": self.headers.get("Accept", "*/*"),
                "Accept-Language": self.headers.get("Accept-Language", "en"),
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read()
                content_type = response.headers.get(
                    "Content-Type",
                    "text/html; charset=utf-8",
                )

                self.send_body(
                    response.status,
                    body,
                    content_type,
                )

        except urllib.error.HTTPError as error:
            body = error.read()
            self.send_body(
                error.code,
                body,
                error.headers.get(
                    "Content-Type",
                    "text/plain; charset=utf-8",
                ),
            )

        except Exception as error:
            print(f"Gateway upstream error: {error}", flush=True)
            self.send_body(
                502,
                b'{"ok":false,"error":"searxng_upstream_unavailable"}',
                "application/json",
            )

    def do_POST(self):
        self.send_body(
            405,
            b'{"ok":false,"error":"method_not_allowed"}',
            "application/json",
        )

    def log_message(self, format_string, *args):
        print("gateway:", format_string % args, flush=True)


if __name__ == "__main__":
    print(
        f"LeadHunter SearXNG gateway listening on 0.0.0.0:{PORT}",
        flush=True,
    )

    server = ThreadedHTTPServer(("0.0.0.0", PORT), Handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
