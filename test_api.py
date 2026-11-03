import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from app import ProductHandler


class ProductAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ProductHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def get(self, path):
        try:
            response = urlopen(self.base_url + path, timeout=3)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def test_list_all_products(self):
        status, body = self.get("/products")
        self.assertEqual(status, 200)
        self.assertEqual(body["total"], 8)
        self.assertEqual(len(body["data"]), 8)
        self.assertEqual(len({item["id"] for item in body["data"]}), 8)
        self.assertEqual({item["status"] for item in body["data"]}, {"active", "draft", "archived"})

    def test_unknown_parameter(self):
        status, body = self.get("/products?unknown=value")
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_query")

    def test_unknown_path(self):
        status, body = self.get("/missing")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "not_found")


if __name__ == "__main__":
    unittest.main()
