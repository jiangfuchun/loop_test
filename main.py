"""
Web scraping task: Automatically fetch and parse web pages.

Supported features:
  - Fetch page content via HTTP GET
  - Parse HTML and extract text/images/links
  - Save results to local output files
  - Configurable via command-line arguments
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def fetch_page(url: str, timeout: int = 30) -> str:
    """Fetch HTML content from a URL."""
    log.info("Fetching %s (timeout=%ds)", url, timeout)
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    log.info("Fetched %d bytes", len(resp.content))
    return resp.text


def parse_html(html: str, base_url: str) -> dict:
    """Parse HTML and extract structured data."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove script/style elements for cleaner text extraction
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    text = soup.get_text(separator="\n", strip=True)

    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith("/"):
            from urllib.parse import urljoin
            href = urljoin(base_url, href)
        links.append({"text": a_tag.get_text(strip=True), "href": href})

    images = []
    for img_tag in soup.find_all("img", src=True):
        src = img_tag["src"]
        if src.startswith("/"):
            from urllib.parse import urljoin
            src = urljoin(base_url, src)
        images.append({"alt": img_tag.get("alt", ""), "src": src})

    return {
        "title": title,
        "text_length": len(text),
        "text_preview": text[:500],
        "links_count": len(links),
        "links": links[:50],  # limit to first 50
        "images_count": len(images),
        "images": images[:20],  # limit to first 20
    }


def save_output(data: dict, output_dir: Path, name: str) -> Path:
    """Save scraped data as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{name}.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    log.info("Saved to %s", out_path)
    return out_path


def scrape(url: str, output_dir: Optional[Path] = None) -> dict:
    """Scrape a URL and save results."""
    output_dir = output_dir or Path("output")
    html = fetch_page(url)
    data = parse_html(html, url)

    from urllib.parse import urlparse
    name = urlparse(url).netloc.replace(".", "_")
    save_output(data, output_dir, name)

    return data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Web page auto-scraping tool"
    )
    parser.add_argument("url", help="Target URL to scrape")
    parser.add_argument(
        "--output-dir", "-o",
        default="output",
        help="Output directory (default: output)",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )
    args = parser.parse_args()

    try:
        data = scrape(args.url, Path(args.output_dir))
        print(json.dumps({"status": "ok", "title": data["title"]}))
    except Exception as e:
        log.error("Failed to scrape %s: %s", args.url, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
