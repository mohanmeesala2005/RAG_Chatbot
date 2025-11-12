import re
import logging
from typing import Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from playwright.sync_api import sync_playwright


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _ensure_scheme(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        return "http://" + url
    return url


def _clean_text(text: str) -> str:
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_from_soup(soup: BeautifulSoup) -> str:
    # Remove scripts/styles/comments
    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav", "form", "svg"]):
        tag.decompose()

    # Prefer main/article content if present
    candidates = []
    for selector in ("article", "main", "div[id^=content]", "div[class*=content]", "section"):
        found = soup.select(selector)
        if found:
            candidates.extend(found)

    # If no structural candidates, fall back to body
    if not candidates:
        body = soup.body or soup
        candidates = [body]

    texts = []
    for node in candidates:
        # Collect meaningful text from paragraphs, headings and list items
        for elt in node.find_all(["p", "h1", "h2", "h3", "h4", "li"]):
            if isinstance(elt, Tag):
                txt = elt.get_text(separator=" ", strip=True)
                if txt:
                    texts.append(txt)

    # If nothing was collected above, take visible text of the node
    if not texts:
        visible = "".join(node.get_text(separator=" ", strip=True) for node in candidates)
        texts = [visible] if visible else []

    content = " ".join(texts)
    return _clean_text(content)


def _scrape_with_requests(url: str, timeout: int = 10) -> Optional[str]:
    headers = {
        "User-Agent": "RAG-Chatbot-Scraper/1.0 (+https://github.com/)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        return _extract_from_soup(soup)
    except Exception as e:
        logger.warning("Requests scraping failed for %s: %s", url, e)
        return None


def _scrape_with_playwright(url: str, timeout: int = 30) -> Optional[str]:
    try:
        # Import inside function to make playwright optional

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
            html = page.content()
            browser.close()
            soup = BeautifulSoup(html, "html.parser")
            return _extract_from_soup(soup)
    except Exception as e:
        logger.warning("Playwright scraping failed for %s: %s", url, e)
        return None


def scrape_website(url: str, use_playwright: bool = False, timeout: int = 10) -> str:
    """
    Scrape a website and return the main textual content.

    - Tries a fast requests + BeautifulSoup approach first.
    - If that fails or yields very little content, and use_playwright=True (or requests fails),
      it will attempt a headless browser scrape using Playwright (if installed).
    - Returns an empty string on failure.

    Args:
        url: URL to scrape.
        use_playwright: If True, allow falling back to Playwright for JS-heavy sites.
        timeout: Request/page timeout in seconds.

    Returns:
        Extracted plain text (possibly empty).
    """
    url = _ensure_scheme(url)
    text = _scrape_with_requests(url, timeout=timeout)

    if text:
        # If the result looks reasonable, return it
        if len(text.split()) >= 20:
            return text
        logger.info("Requests returned small content (word count=%d), considering Playwright if allowed", len(text.split()))

    if use_playwright:
        pw_text = _scrape_with_playwright(url, timeout=max(timeout, 20))
        if pw_text and len(pw_text.split()) >= 10:
            return pw_text

    # If requests returned something even if small, return it; else empty string
    return text or ""
