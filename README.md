# loop_test

Created for testing the /loop skill functionality.

## Web Scraping Task

`main.py` is an automated web scraping tool that fetches and parses web pages.

### Usage

```bash
# Scrape a web page (results saved to output/ directory)
python main.py https://example.com

# Specify a custom output directory
python main.py https://example.com -o ./data

# Increase request timeout
python main.py https://example.com -t 60
```

### Features

- HTTP page fetching with configurable timeout
- HTML parsing — extracts title, text, links, and images
- JSON output saved to local files
- Error handling and logging

### Dependencies

- `requests` — HTTP client
- `beautifulsoup4` — HTML parser
