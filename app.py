"""Local-only product API for a Mintlify Autopilot demonstration."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


PRODUCTS = json.loads(
    (Path(__file__).parent / "fixtures" / "products.json").read_text(encoding="utf-8")
)


def list_products(query):
    if set(query) - {"status", "limit", "sort"}:
        raise ValueError("Only status, limit and sort query parameters are supported")
    statuses = query.get("status")
    products = PRODUCTS
    if statuses is not None:
        if len(statuses) != 1 or statuses[0] not in {"active", "draft", "archived"}:
            raise ValueError("status must be exactly one of: active, draft, archived")
        products = [product for product in PRODUCTS if product["status"] == statuses[0]]
    sorts = query.get("sort")
    if sorts is not None:
        if len(sorts) != 1 or sorts[0] not in {"price_asc", "price_desc", "name_asc", "name_desc"}:
            raise ValueError("sort must be exactly one of: price_asc, price_desc, name_asc, name_desc")
        products = sorted(
            products,
            key=lambda product: product["name"] if sorts[0] in {"name_asc", "name_desc"} else product["price_cents"],
            reverse=sorts[0] in {"price_desc", "name_desc"},
        )
    limits = query.get("limit")
    if limits is not None:
        if len(limits) != 1 or not limits[0].isascii() or not limits[0].isdigit():
            raise ValueError("limit must be one integer from 1 to 200")
        limit = int(limits[0])
        if not 1 <= limit <= 200:
            raise ValueError("limit must be one integer from 1 to 200")
        products = products[:limit]
    return {"data": products, "total": len(products)}


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
