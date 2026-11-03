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

    def test_filter_by_status(self):
        for value, expected_count in [("active", 4), ("draft", 2), ("archived", 2)]:
            with self.subTest(status=value):
                status, body = self.get("/products?status=" + value)
                self.assertEqual(status, 200)
                self.assertEqual(body["total"], expected_count)
                self.assertEqual(len(body["data"]), expected_count)
                self.assertTrue(all(item["status"] == value for item in body["data"]))
        # A filtered request must not alter the fixture used by later requests.
        self.assertEqual(self.get("/products")[1]["total"], 8)

    def test_invalid_status(self):
        for query in ["status=invalid", "status=", "status=ACTIVE", "status=active&status=draft"]:
            with self.subTest(query=query):
                status, body = self.get("/products?" + query)
                self.assertEqual(status, 400)
                self.assertEqual(body["error"], "invalid_query")
                self.assertIn("active, draft, archived", body["message"])

    def test_unknown_path(self):
        status, body = self.get("/missing")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "not_found")


if __name__ == "__main__":
    unittest.main()
