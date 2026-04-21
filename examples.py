"""
Example use cases for the web scraper with auto-decryption.
"""

from scraper import WebScraper, DecryptionEngine
import json


def example_basic_scraping():
    """Basic web scraping example."""
    print("\n=== Example 1: Basic Scraping ===")

    scraper = WebScraper(max_workers=3, rate_limit=1.0)

    urls = [
        'https://httpbin.org/html',
        'https://httpbin.org/json',
        'https://httpbin.org/user-agent'
    ]

    results = scraper.scrape_urls(urls)

    for result in results:
        print(f"\nURL: {result['url']}")
        print(f"Status: {result.get('status_code', 'Error')}")
        if 'title' in result:
            print(f"Title: {result['title']}")

    print(f"\nStats: {scraper.get_stats()}")


def example_link_extraction():
    """Extract all links from a webpage."""
    print("\n=== Example 2: Link Extraction ===")

    scraper = WebScraper(rate_limit=1.0)

    result = scraper.scrape_url('https://example.com', extract_links=True)

    if 'links' in result:
        print(f"Found {len(result['links'])} links:")
        for link in result['links'][:5]:  # Show first 5
            print(f"  - {link['text']}: {link['url']}")


def example_base64_decryption():
    """Decrypt base64 encoded data."""
    print("\n=== Example 3: Base64 Decryption ===")

    engine = DecryptionEngine()

    # Example base64 encoded messages
    encoded_messages = [
        'SGVsbG8sIFdvcmxkIQ==',
        'VGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl',
        'QXV0by1kZWNyeXB0aW5nIHNjcmFwZXI='
    ]

    for encoded in encoded_messages:
        decoded = engine.decode_base64(encoded)
        print(f"Encoded: {encoded}")
        print(f"Decoded: {decoded}\n")


def example_json_api_scraping():
    """Scrape JSON API endpoints."""
    print("\n=== Example 4: JSON API Scraping ===")

    scraper = WebScraper(rate_limit=0.5)

    # JSON endpoints
    urls = [
        'https://httpbin.org/json',
        'https://httpbin.org/get',
    ]

    results = scraper.scrape_urls(urls)

    for result in results:
        print(f"\nURL: {result['url']}")
        if 'json' in result:
            print("JSON Data:")
            print(json.dumps(result['json'], indent=2))


def example_custom_parser():
    """Use custom parser for specific data extraction."""
    print("\n=== Example 5: Custom Parser ===")

    def extract_metadata(response, result):
        """Extract specific metadata from page."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        metadata = {
            'paragraphs': len(soup.find_all('p')),
            'headings': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'links': len(soup.find_all('a')),
            'images': len(soup.find_all('img'))
        }

        return metadata

    scraper = WebScraper()
    result = scraper.scrape_url(
        'https://example.com',
        custom_parser=extract_metadata
    )

    if 'custom_parsed' in result:
        print("Page Metadata:")
        print(json.dumps(result['custom_parsed'], indent=2))


def example_concurrent_heavy_scraping():
    """Heavy concurrent scraping with multiple workers."""
    print("\n=== Example 6: Heavy Concurrent Scraping ===")

    # Generate multiple URLs
    urls = [
        f'https://httpbin.org/delay/{i % 3}'
        for i in range(10)
    ]

    scraper = WebScraper(
        max_workers=10,
        rate_limit=0.2,
        timeout=15
    )

    import time
    start_time = time.time()

    results = scraper.scrape_urls(urls)

    elapsed = time.time() - start_time

    print(f"Scraped {len(results)} URLs in {elapsed:.2f} seconds")
    print(f"Stats: {scraper.get_stats()}")


def example_with_custom_headers():
    """Scraping with custom headers."""
    print("\n=== Example 7: Custom Headers ===")

    scraper = WebScraper(
        custom_headers={
            'Accept': 'application/json',
            'X-Custom-Header': 'MyValue'
        }
    )

    result = scraper.scrape_url('https://httpbin.org/headers')

    if 'json' in result:
        print("Request headers seen by server:")
        print(json.dumps(result['json'].get('headers', {}), indent=2))


def example_aes_decryption():
    """Example of AES decryption (requires encrypted data)."""
    print("\n=== Example 8: AES Decryption ===")

    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    import base64

    # Create some encrypted data for demonstration
    key = b'This-is-a-32-byte-secret-key'
    iv = b'This-is-a-16-byt'
    plaintext = b'Secret message to decrypt!'

    # Encrypt
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(plaintext, AES.block_size))
    encrypted_with_iv = iv + encrypted
    encrypted_b64 = base64.b64encode(encrypted_with_iv).decode()

    print(f"Encrypted (base64): {encrypted_b64}")

    # Decrypt using DecryptionEngine
    engine = DecryptionEngine()
    encrypted_bytes = base64.b64decode(encrypted_b64)
    decrypted = engine.decrypt_aes(encrypted_bytes, key)

    print(f"Decrypted: {decrypted}")


def example_save_results():
    """Save scraping results to file."""
    print("\n=== Example 9: Save Results ===")

    scraper = WebScraper(rate_limit=0.5)

    urls = [
        'https://httpbin.org/json',
        'https://example.com'
    ]

    results = scraper.scrape_urls(urls, extract_links=True)

    # Save to JSON file
    filename = 'example_results.json'
    scraper.save_results(results, filename)
    print(f"Results saved to {filename}")


if __name__ == '__main__':
    # Run all examples
    examples = [
        example_basic_scraping,
        example_link_extraction,
        example_base64_decryption,
        example_json_api_scraping,
        example_custom_parser,
        example_concurrent_heavy_scraping,
        example_with_custom_headers,
        example_aes_decryption,
        example_save_results
    ]

    print("=" * 60)
    print("Web Scraper with Auto-Decryption - Examples")
    print("=" * 60)

    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"\nExample {i} error: {e}")

        if i < len(examples):
            input("\nPress Enter to continue to next example...")

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
