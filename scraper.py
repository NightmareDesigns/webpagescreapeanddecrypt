#!/usr/bin/env python3
"""
Heavy-Hitting Auto-Decrypting Website Scraper

A powerful web scraper with built-in decryption capabilities, concurrent processing,
and advanced features like proxy support, rate limiting, and automatic retry logic.
"""

import base64
import hashlib
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import unpad
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DecryptionEngine:
    """Handles various decryption algorithms."""

    @staticmethod
    def decode_base64(data: str) -> str:
        """Decode base64 encoded data."""
        try:
            return base64.b64decode(data).decode('utf-8')
        except Exception as e:
            logger.error(f"Base64 decoding failed: {e}")
            return data

    @staticmethod
    def decrypt_aes(encrypted_data: bytes, key: bytes, iv: Optional[bytes] = None) -> str:
        """Decrypt AES encrypted data."""
        try:
            if iv is None:
                iv = encrypted_data[:16]
                encrypted_data = encrypted_data[16:]

            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"AES decryption failed: {e}")
            raise

    @staticmethod
    def decrypt_rsa(encrypted_data: bytes, private_key: str) -> str:
        """Decrypt RSA encrypted data."""
        try:
            key = RSA.import_key(private_key)
            cipher = PKCS1_OAEP.new(key)
            decrypted = cipher.decrypt(encrypted_data)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"RSA decryption failed: {e}")
            raise

    @staticmethod
    def auto_detect_and_decrypt(data: str, keys: Optional[Dict[str, Any]] = None) -> str:
        """Attempt to auto-detect encoding/encryption and decrypt."""
        # Try base64 first
        try:
            decoded = DecryptionEngine.decode_base64(data)
            if decoded != data:
                return decoded
        except:
            pass

        # If keys provided, try decryption methods
        if keys:
            if 'aes_key' in keys:
                try:
                    encrypted_bytes = base64.b64decode(data)
                    return DecryptionEngine.decrypt_aes(
                        encrypted_bytes,
                        keys['aes_key'].encode() if isinstance(keys['aes_key'], str) else keys['aes_key'],
                        keys.get('aes_iv')
                    )
                except:
                    pass

            if 'rsa_private_key' in keys:
                try:
                    encrypted_bytes = base64.b64decode(data)
                    return DecryptionEngine.decrypt_rsa(encrypted_bytes, keys['rsa_private_key'])
                except:
                    pass

        return data


class WebScraper:
    """Heavy-hitting web scraper with auto-decryption capabilities."""

    def __init__(
        self,
        max_workers: int = 10,
        rate_limit: float = 0.5,
        timeout: int = 30,
        use_proxy: bool = False,
        proxy_list: Optional[List[str]] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        decryption_keys: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the web scraper.

        Args:
            max_workers: Maximum number of concurrent threads
            rate_limit: Minimum seconds between requests
            timeout: Request timeout in seconds
            use_proxy: Whether to use proxy rotation
            proxy_list: List of proxy URLs
            custom_headers: Custom HTTP headers
            decryption_keys: Dictionary of decryption keys
        """
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.proxy_index = 0
        self.session = requests.Session()
        self.decryption_engine = DecryptionEngine()
        self.decryption_keys = decryption_keys or {}

        # Setup headers
        self.ua = UserAgent()
        self.headers = custom_headers or {}
        if 'User-Agent' not in self.headers:
            self.headers['User-Agent'] = self.ua.random

        self.session.headers.update(self.headers)

        # Statistics
        self.stats = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'decrypted': 0
        }

    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy from the rotation."""
        if not self.use_proxy or not self.proxy_list:
            return None

        proxy = self.proxy_list[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)

        return {
            'http': proxy,
            'https': proxy
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _fetch_url(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """
        Fetch URL with retry logic.

        Args:
            url: URL to fetch
            method: HTTP method
            **kwargs: Additional arguments for requests

        Returns:
            Response object
        """
        self.stats['requests'] += 1

        # Rate limiting
        time.sleep(self.rate_limit)

        # Get proxy if enabled
        proxies = self._get_proxy()

        # Rotate user agent
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = self.ua.random

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                proxies=proxies,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            self.stats['successful'] += 1
            return response
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"Failed to fetch {url}: {e}")
            raise

    def scrape_url(
        self,
        url: str,
        extract_links: bool = False,
        auto_decrypt: bool = True,
        custom_parser: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Scrape a single URL.

        Args:
            url: URL to scrape
            extract_links: Whether to extract all links
            auto_decrypt: Whether to attempt auto-decryption
            custom_parser: Custom parsing function

        Returns:
            Dictionary containing scraped data
        """
        try:
            response = self._fetch_url(url)

            result = {
                'url': url,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content_type': response.headers.get('Content-Type', ''),
                'raw_content': response.text,
                'timestamp': time.time()
            }

            # Parse HTML
            if 'text/html' in result['content_type']:
                soup = BeautifulSoup(response.text, 'lxml')
                result['title'] = soup.title.string if soup.title else None
                result['text'] = soup.get_text(strip=True)

                # Extract links if requested
                if extract_links:
                    links = []
                    for link in soup.find_all('a', href=True):
                        absolute_url = urljoin(url, link['href'])
                        links.append({
                            'url': absolute_url,
                            'text': link.get_text(strip=True),
                            'title': link.get('title', '')
                        })
                    result['links'] = links

                # Auto-decrypt if enabled
                if auto_decrypt:
                    # Look for encrypted data in script tags, data attributes, etc.
                    encrypted_scripts = soup.find_all('script', {'data-encrypted': True})
                    if encrypted_scripts:
                        decrypted_data = []
                        for script in encrypted_scripts:
                            try:
                                encrypted = script.get('data-encrypted') or script.string
                                if encrypted:
                                    decrypted = self.decryption_engine.auto_detect_and_decrypt(
                                        encrypted.strip(),
                                        self.decryption_keys
                                    )
                                    decrypted_data.append(decrypted)
                                    self.stats['decrypted'] += 1
                            except Exception as e:
                                logger.warning(f"Failed to decrypt script data: {e}")

                        if decrypted_data:
                            result['decrypted_data'] = decrypted_data

            # Handle JSON responses
            elif 'application/json' in result['content_type']:
                try:
                    result['json'] = response.json()

                    # Try to decrypt JSON values if auto_decrypt enabled
                    if auto_decrypt:
                        result['decrypted_json'] = self._decrypt_json_values(result['json'])
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON from {url}")

            # Custom parser
            if custom_parser:
                result['custom_parsed'] = custom_parser(response, result)

            return result

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'timestamp': time.time()
            }

    def _decrypt_json_values(self, data: Any) -> Any:
        """Recursively decrypt JSON values."""
        if isinstance(data, dict):
            return {k: self._decrypt_json_values(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._decrypt_json_values(item) for item in data]
        elif isinstance(data, str):
            return self.decryption_engine.auto_detect_and_decrypt(data, self.decryption_keys)
        return data

    def scrape_urls(
        self,
        urls: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            **kwargs: Arguments to pass to scrape_url

        Returns:
            List of scraping results
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.scrape_url, url, **kwargs): url
                for url in urls
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Successfully scraped: {url}")
                except Exception as e:
                    logger.error(f"Exception scraping {url}: {e}")
                    results.append({
                        'url': url,
                        'error': str(e),
                        'timestamp': time.time()
                    })

        return results

    def get_stats(self) -> Dict[str, int]:
        """Get scraping statistics."""
        return self.stats.copy()

    def save_results(self, results: List[Dict[str, Any]], filename: str):
        """Save scraping results to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {filename}")


def main():
    """Example usage."""
    # Example configuration
    scraper = WebScraper(
        max_workers=5,
        rate_limit=1.0,
        timeout=30,
        decryption_keys={
            # Add your decryption keys here
            # 'aes_key': 'your-aes-key',
            # 'rsa_private_key': 'your-rsa-private-key'
        }
    )

    # Example URLs
    urls = [
        'https://example.com',
        'https://httpbin.org/json',
    ]

    # Scrape URLs
    results = scraper.scrape_urls(urls, extract_links=True, auto_decrypt=True)

    # Print statistics
    print("\nScraping Statistics:")
    print(json.dumps(scraper.get_stats(), indent=2))

    # Save results
    scraper.save_results(results, 'scraping_results.json')


if __name__ == '__main__':
    main()
