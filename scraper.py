import argparse
import base64
import codecs
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen


def _is_mostly_printable(text: str, threshold: float = 0.85) -> bool:
    if not text:
        return False
    printable = sum(1 for c in text if c.isprintable() and c not in "\x0b\x0c")
    return printable / len(text) >= threshold


def _decode_base64(value: str):
    if len(value) < 8:
        return None
    if not re.fullmatch(r"[A-Za-z0-9+/=_-]+", value):
        return None
    padded = value + "=" * (-len(value) % 4)
    try:
        decoded = base64.b64decode(padded, validate=True).decode("utf-8")
    except Exception:
        return None
    return decoded if _is_mostly_printable(decoded) else None


def _decode_hex(value: str):
    compact = value.strip().replace(" ", "")
    if len(compact) < 8 or len(compact) % 2 != 0:
        return None
    if not re.fullmatch(r"[0-9a-fA-F]+", compact):
        return None
    try:
        decoded = bytes.fromhex(compact).decode("utf-8")
    except Exception:
        return None
    return decoded if _is_mostly_printable(decoded) else None


def _decode_url(value: str):
    decoded = unquote(value)
    return decoded if decoded != value else None


def _decode_rot13(value: str):
    decoded = codecs.decode(value, "rot_13")
    if decoded != value and _is_mostly_printable(decoded):
        return decoded
    return None


def auto_decrypt(value: str, max_rounds: int = 3):
    decoders = (_decode_base64, _decode_hex, _decode_url, _decode_rot13)
    results = set()
    seen = {value}
    queue = [value]

    for _ in range(max_rounds):
        next_queue = []
        for item in queue:
            for decoder in decoders:
                decoded = decoder(item)
                if decoded and decoded not in seen:
                    seen.add(decoded)
                    results.add(decoded)
                    next_queue.append(decoded)
        if not next_queue:
            break
        queue = next_queue

    return sorted(results, key=len)


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        attr_map = dict(attrs)
        href = attr_map.get("href")
        if href:
            self.links.append(href)


def _extract_title(html: str):
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def _extract_candidates(html: str):
    tokens = set(re.findall(r"[A-Za-z0-9%+/=_-]{8,}", html))
    return tokens


def _fetch_url(url: str, timeout: int, user_agent: str):
    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.status, body


def scrape(
    start_url: str,
    max_pages: int = 30,
    max_depth: int = 2,
    workers: int = 8,
    timeout: int = 10,
    user_agent: str = "HeavyAutoDecryptScraper/1.0",
):
    if workers < 1:
        raise ValueError("workers must be >= 1")

    parsed = urlparse(start_url)
    root_netloc = parsed.netloc

    visited = set()
    visited_lock = threading.Lock()
    pages = []
    current_level = {start_url}

    def reserve_url(candidate_url: str):
        with visited_lock:
            if candidate_url in visited or len(visited) >= max_pages:
                return False
            visited.add(candidate_url)
            return True

    for _depth in range(max_depth + 1):
        if not current_level or len(visited) >= max_pages:
            break

        batch = []
        for candidate in current_level:
            if reserve_url(candidate):
                batch.append(candidate)

        if not batch:
            break

        next_level = set()

        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_map = {
                pool.submit(_fetch_url, url, timeout, user_agent): url for url in batch
            }

            for future in as_completed(future_map):
                url = future_map[future]
                try:
                    status, html = future.result()
                except Exception as exc:
                    pages.append(
                        {
                            "url": url,
                            "status": "error",
                            "error": str(exc),
                            "title": "",
                            "decrypted_messages": [],
                        }
                    )
                    continue

                parser = LinkParser()
                parser.feed(html)

                for raw_link in parser.links:
                    absolute = urljoin(url, raw_link)
                    parsed_link = urlparse(absolute)
                    if parsed_link.scheme not in {"http", "https"}:
                        continue
                    if parsed_link.netloc != root_netloc:
                        continue
                    if len(visited) + len(next_level) < max_pages:
                        next_level.add(absolute)

                decrypted_messages = set()
                for candidate in _extract_candidates(html):
                    for decoded in auto_decrypt(candidate):
                        if 4 <= len(decoded) <= 500:
                            decrypted_messages.add(decoded)

                pages.append(
                    {
                        "url": url,
                        "status": status,
                        "title": _extract_title(html),
                        "decrypted_messages": sorted(decrypted_messages),
                    }
                )

        current_level = next_level

    return {
        "start_url": start_url,
        "max_pages": max_pages,
        "visited_pages": len(visited),
        "pages": pages,
    }


def main():
    parser = argparse.ArgumentParser(description="Heavy-hitting auto-decrypting website scraper")
    parser.add_argument("url", help="Starting URL to scrape")
    parser.add_argument("--max-pages", type=int, default=30)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--output", help="Optional output JSON file")

    args = parser.parse_args()

    result = scrape(
        start_url=args.url,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        workers=args.workers,
        timeout=args.timeout,
    )

    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload)
    else:
        print(payload)


if __name__ == "__main__":
    main()
