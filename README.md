# Heavy-Hitting Auto-Decrypting Website Scraper

A powerful, production-ready web scraper with built-in decryption capabilities, concurrent processing, and advanced features designed for heavy-duty scraping tasks.

## Features

- **Multi-threaded Concurrent Scraping**: Process multiple URLs simultaneously with configurable thread pool
- **Auto-Decryption Engine**: Support for multiple encryption algorithms:
  - Base64 encoding/decoding
  - AES (CBC mode) decryption
  - RSA decryption
  - Automatic detection and decryption
- **Rate Limiting**: Built-in rate limiting to avoid overwhelming servers
- **Proxy Support**: Rotate through proxy servers for distributed scraping
- **Retry Logic**: Automatic retry with exponential backoff for failed requests
- **User-Agent Rotation**: Random user-agent rotation to avoid detection
- **Session Management**: Persistent session with cookie support
- **Multiple Content Types**: Handle HTML, JSON, and other content types
- **Link Extraction**: Automatically extract and normalize all links from pages
- **Custom Parsers**: Support for custom parsing logic
- **Comprehensive Logging**: Detailed logging and statistics tracking
- **Error Handling**: Robust error handling with graceful degradation

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from scraper import WebScraper

# Create scraper instance
scraper = WebScraper(
    max_workers=10,      # Number of concurrent threads
    rate_limit=0.5,      # Seconds between requests
    timeout=30           # Request timeout
)

# Scrape a single URL
result = scraper.scrape_url('https://example.com', extract_links=True)
print(result)

# Scrape multiple URLs concurrently
urls = [
    'https://example.com',
    'https://httpbin.org/json',
    'https://httpbin.org/html'
]
results = scraper.scrape_urls(urls, extract_links=True)

# Save results to file
scraper.save_results(results, 'output.json')

# View statistics
print(scraper.get_stats())
```

### With Decryption Keys

```python
from scraper import WebScraper

# Configure with decryption keys
scraper = WebScraper(
    max_workers=5,
    decryption_keys={
        'aes_key': b'your-32-byte-aes-key-here!!!',
        'aes_iv': b'your-16-byte-iv!',
        'rsa_private_key': '''-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----'''
    }
)

# Scrape with auto-decryption enabled
result = scraper.scrape_url('https://example.com', auto_decrypt=True)
```

### With Proxy Rotation

```python
from scraper import WebScraper

# Configure with proxies
scraper = WebScraper(
    max_workers=10,
    use_proxy=True,
    proxy_list=[
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080',
        'http://proxy3.example.com:8080'
    ]
)

results = scraper.scrape_urls(urls)
```

### Custom Parser

```python
from scraper import WebScraper

def custom_parser(response, result):
    """Extract specific data from response."""
    soup = BeautifulSoup(response.text, 'lxml')
    return {
        'meta_description': soup.find('meta', {'name': 'description'}),
        'h1_tags': [h1.text for h1 in soup.find_all('h1')],
        'images': [img.get('src') for img in soup.find_all('img')]
    }

scraper = WebScraper()
result = scraper.scrape_url('https://example.com', custom_parser=custom_parser)
print(result['custom_parsed'])
```

## Decryption Engine

The scraper includes a powerful decryption engine that can handle various encryption schemes:

### Manual Decryption

```python
from scraper import DecryptionEngine

engine = DecryptionEngine()

# Base64 decoding
decoded = engine.decode_base64('SGVsbG8gV29ybGQh')

# AES decryption
decrypted = engine.decrypt_aes(
    encrypted_data=encrypted_bytes,
    key=b'your-32-byte-key-here!!!!!!!',
    iv=b'your-16-byte-iv!'
)

# RSA decryption
decrypted = engine.decrypt_rsa(
    encrypted_data=encrypted_bytes,
    private_key=rsa_private_key_pem
)

# Auto-detect and decrypt
result = engine.auto_detect_and_decrypt(
    data=encrypted_string,
    keys={
        'aes_key': b'your-key',
        'rsa_private_key': 'your-private-key-pem'
    }
)
```

## Configuration Options

### WebScraper Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_workers` | int | 10 | Maximum concurrent threads |
| `rate_limit` | float | 0.5 | Minimum seconds between requests |
| `timeout` | int | 30 | Request timeout in seconds |
| `use_proxy` | bool | False | Enable proxy rotation |
| `proxy_list` | List[str] | None | List of proxy URLs |
| `custom_headers` | Dict | None | Custom HTTP headers |
| `decryption_keys` | Dict | None | Decryption keys dictionary |

### scrape_url Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | str | Required | URL to scrape |
| `extract_links` | bool | False | Extract all links from page |
| `auto_decrypt` | bool | True | Attempt auto-decryption |
| `custom_parser` | Callable | None | Custom parsing function |

## Output Format

The scraper returns structured data for each URL:

```json
{
  "url": "https://example.com",
  "status_code": 200,
  "headers": {},
  "content_type": "text/html",
  "title": "Page Title",
  "text": "Extracted text content",
  "raw_content": "Full HTML content",
  "links": [
    {
      "url": "https://example.com/page",
      "text": "Link Text",
      "title": "Link Title"
    }
  ],
  "decrypted_data": ["decrypted content"],
  "timestamp": 1234567890.123
}
```

## Statistics

Track scraping performance:

```python
stats = scraper.get_stats()
# Returns:
# {
#   'requests': 100,
#   'successful': 95,
#   'failed': 5,
#   'decrypted': 20
# }
```

## Advanced Features

### Automatic Retry with Exponential Backoff

The scraper automatically retries failed requests up to 3 times with exponential backoff (2-10 seconds).

### Session Persistence

HTTP sessions are maintained across requests, preserving cookies and connection pooling for better performance.

### User-Agent Rotation

User agents are automatically rotated for each request to avoid detection.

### Link Extraction and Normalization

All extracted links are automatically converted to absolute URLs for easy follow-up scraping.

## Security Considerations

⚠️ **Important**: Only use this scraper on websites you own or have permission to scrape. Respect robots.txt and rate limits. Use decryption capabilities only on data you have authorization to decrypt.

## Use Cases

- Web data extraction and aggregation
- Content monitoring and archival
- API testing and validation
- Encrypted content retrieval (with proper authorization)
- SEO analysis and link checking
- Research and data collection

## Requirements

- Python 3.7+
- See `requirements.txt` for dependencies

## License

MIT License - See repository for details

## Contributing

Contributions are welcome! Please ensure all security and ethical guidelines are followed.
