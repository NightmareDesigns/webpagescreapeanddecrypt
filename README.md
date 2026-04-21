# webpagescreapeanddecrypt

Heavy-hitting auto-decrypting website scraper.

## Run

```bash
python /home/runner/work/webpagescreapeanddecrypt/webpagescreapeanddecrypt/scraper.py https://example.com --max-pages 30 --max-depth 2 --workers 8
```

## What it does

- Concurrently scrapes pages on the same host.
- Extracts candidate encoded strings from HTML/script content.
- Automatically attempts layered decryption/decoding (Base64, URL encoding, hex, ROT13).
- Returns structured JSON with decrypted findings per page.

## Test

```bash
cd /home/runner/work/webpagescreapeanddecrypt/webpagescreapeanddecrypt
python -m unittest discover -s tests -v
```
