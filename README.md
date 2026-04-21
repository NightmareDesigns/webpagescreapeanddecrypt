# webpagescreapeanddecrypt

Heavy-hitting auto-decrypting website scraper.

## Run

### Command Line

```bash
python scraper.py https://example.com --max-pages 30 --max-depth 2 --workers 8
```

### GUI Application

A Qt-based C++ GUI is available for a user-friendly experience. See [gui/README.md](gui/README.md) for build instructions.

```bash
cd gui
mkdir build && cd build
cmake .. && make
cd ../..
./WebScraperGUI
```

## What it does

- Concurrently scrapes pages on the same host.
- Extracts candidate encoded strings from HTML/script content.
- Automatically attempts layered decryption/decoding (Base64, URL encoding, hex, ROT13).
- Returns structured JSON with decrypted findings per page.

## Test

```bash
python -m unittest discover -s tests -v
```
