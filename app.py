"""Local-only product API for a Mintlify Autopilot demonstration."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


PRODUCTS = json.loads(
    (Path(__file__).parent / "fixtures" / "products.json").read_text(encoding="utf-8")
)


def list_products(query):
    if query:
        raise ValueError("Query parameters are not supported")
    return {"data": PRODUCTS, "total": len(PRODUCTS)}


class ProductHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urlsplit(self.path)
        if request.path != "/products":
            self.send_json(404, {"error": "not_found"})
            return
        try:
            result = list_products(parse_qs(request.query, keep_blank_values=True))
        except ValueError as error:
            self.send_json(400, {"error": "invalid_query", "message": str(error)})
            return
        self.send_json(200, result)

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ProductHandler)
    print("Demo API: http://127.0.0.1:8000/products", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
