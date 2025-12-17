from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import re
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

def _is_pdf_url(url: str) -> bool:
    if not url:
        return False
    return bool(re.search(r"\.pdf($|\?)", url, re.IGNORECASE))


def fetch_pdf_text(url: str, timeout: int = 20, max_pages: int = 20, max_chars: int = 20000) -> str:
    """
    Download a PDF and extract text. Returns empty string on failure.
    """
    if not PdfReader:
        return ""  # library not available
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        bio = BytesIO(resp.content)
        reader = PdfReader(bio)
        texts = []
        for i, page in enumerate(reader.pages[:max_pages]):
            try:
                t = page.extract_text() or ""
            except Exception:
                t = ""
            if t:
                texts.append(t)
        return ("\n\n".join(texts))[:max_chars]
    except Exception:
        return ""


def fetch_page_text(url: str, timeout: int = 15, max_chars: int = 20000) -> str:
    """
    Fetch and extract readable text from a web page URL.
    Returns an empty string on failure.
    """
    if not url:
        return ""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            )
        }
        # If it looks like a PDF URL, try PDF parsing directly
        if _is_pdf_url(url):
            pdf_text = fetch_pdf_text(url, timeout=timeout, max_chars=max_chars)
            if pdf_text:
                return pdf_text

        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        # If server reports PDF content-type, switch to PDF parser
        ctype = resp.headers.get("Content-Type", "")
        if "pdf" in ctype.lower():
            pdf_text = fetch_pdf_text(url, timeout=timeout, max_chars=max_chars)
            if pdf_text:
                return pdf_text
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "iframe"]):
            tag.decompose()
        text = " ".join(s.strip() for s in soup.stripped_strings)
        return text[:max_chars]
    except Exception:
        return ""

def web_search(query: str, max_results: int = 4):
    """
    Perform a DuckDuckGo text search and return structured results.
    """
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            })

    return results
