#!/usr/bin/env python3
"""
Unit tests for the web scraper and decryption engine.
"""

import unittest
import base64
from unittest.mock import Mock, patch, MagicMock
from scraper import WebScraper, DecryptionEngine
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class TestDecryptionEngine(unittest.TestCase):
    """Test cases for DecryptionEngine."""

    def setUp(self):
        self.engine = DecryptionEngine()

    def test_decode_base64_valid(self):
        """Test base64 decoding with valid input."""
        encoded = base64.b64encode(b"Hello, World!").decode()
        decoded = self.engine.decode_base64(encoded)
        self.assertEqual(decoded, "Hello, World!")

    def test_decode_base64_invalid(self):
        """Test base64 decoding with invalid input."""
        invalid = "not-valid-base64!!!"
        result = self.engine.decode_base64(invalid)
        self.assertEqual(result, invalid)  # Should return original on error

    def test_decrypt_aes(self):
        """Test AES decryption."""
        key = b'0123456789abcdef0123456789abcdef'  # Exactly 32 bytes
        iv = b'0123456789abcdef'  # Exactly 16 bytes
        plaintext = b'Secret message!'

        # Encrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(plaintext, AES.block_size))
        encrypted_with_iv = iv + encrypted

        # Decrypt
        decrypted = self.engine.decrypt_aes(encrypted_with_iv, key)
        self.assertEqual(decrypted, plaintext.decode())

    def test_auto_detect_base64(self):
        """Test auto-detection of base64 encoded data."""
        original = "Test message"
        encoded = base64.b64encode(original.encode()).decode()

        result = self.engine.auto_detect_and_decrypt(encoded)
        self.assertEqual(result, original)


class TestWebScraper(unittest.TestCase):
    """Test cases for WebScraper."""

    def setUp(self):
        self.scraper = WebScraper(max_workers=2, rate_limit=0)

    @patch('scraper.requests.Session.request')
    def test_fetch_url_success(self, mock_request):
        """Test successful URL fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_request.return_value = mock_response

        response = self.scraper._fetch_url('https://example.com')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.scraper.stats['successful'], 1)

    @patch('scraper.requests.Session.request')
    def test_scrape_url_html(self, mock_request):
        """Test scraping HTML content."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><head><title>Test Page</title></head><body><p>Content</p></body></html>"
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_request.return_value = mock_response

        result = self.scraper.scrape_url('https://example.com')

        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['title'], 'Test Page')
        self.assertIn('Content', result['text'])

    @patch('scraper.requests.Session.request')
    def test_scrape_url_json(self, mock_request):
        """Test scraping JSON content."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "value"}'
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"key": "value"}
        mock_request.return_value = mock_response

        result = self.scraper.scrape_url('https://api.example.com/data')

        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['json'], {"key": "value"})

    @patch('scraper.requests.Session.request')
    def test_extract_links(self, mock_request):
        """Test link extraction."""
        html = '''
        <html>
            <body>
                <a href="/page1">Link 1</a>
                <a href="https://example.com/page2" title="Page 2">Link 2</a>
            </body>
        </html>
        '''
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_request.return_value = mock_response

        result = self.scraper.scrape_url('https://example.com', extract_links=True)

        self.assertIn('links', result)
        self.assertEqual(len(result['links']), 2)
        self.assertEqual(result['links'][0]['url'], 'https://example.com/page1')
        self.assertEqual(result['links'][1]['title'], 'Page 2')

    def test_get_proxy_rotation(self):
        """Test proxy rotation."""
        scraper = WebScraper(
            use_proxy=True,
            proxy_list=['http://proxy1:8080', 'http://proxy2:8080']
        )

        proxy1 = scraper._get_proxy()
        proxy2 = scraper._get_proxy()
        proxy3 = scraper._get_proxy()

        self.assertEqual(proxy1['http'], 'http://proxy1:8080')
        self.assertEqual(proxy2['http'], 'http://proxy2:8080')
        self.assertEqual(proxy3['http'], 'http://proxy1:8080')  # Should rotate back

    def test_get_stats(self):
        """Test statistics tracking."""
        stats = self.scraper.get_stats()
        self.assertIn('requests', stats)
        self.assertIn('successful', stats)
        self.assertIn('failed', stats)
        self.assertIn('decrypted', stats)

    def test_custom_headers(self):
        """Test custom headers are set."""
        custom_headers = {'X-Custom': 'Value'}
        scraper = WebScraper(custom_headers=custom_headers)

        self.assertIn('X-Custom', scraper.headers)
        self.assertEqual(scraper.headers['X-Custom'], 'Value')


if __name__ == '__main__':
    unittest.main()
