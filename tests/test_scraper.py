import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from scraper import auto_decrypt, scrape


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""<html><head><title>Home</title></head>
                <body>
                    <a href='/next'>next</a>
                    <script>const msg='c2VjcmV0';</script>
                </body></html>"""
            )
            return

        if self.path == "/next":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><head><title>Next</title></head><body>frperg</body></html>"
            )
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, *_args, **_kwargs):
        return


class ScraperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_auto_decrypt_decodes_chained_formats(self):
        value = "%37%33%36%35%36%33%37%32%36%35%37%34"
        decoded = auto_decrypt(value)
        self.assertIn("736563726574", decoded)
        self.assertIn("secret", decoded)

    def test_scrape_collects_and_decrypts_messages(self):
        result = scrape(
            f"{self.base_url}/",
            max_pages=5,
            max_depth=2,
            workers=2,
            timeout=5,
        )

        self.assertEqual(result["visited_pages"], 2)
        all_messages = {
            message
            for page in result["pages"]
            for message in page["decrypted_messages"]
        }
        self.assertIn("secret", all_messages)


if __name__ == "__main__":
    unittest.main()
