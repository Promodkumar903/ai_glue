"""
OIE Browser — Playwright fetcher for JS-heavy government sites
"""
import re
from playwright.sync_api import sync_playwright


def fetch_rendered(url, wait_ms=3000, timeout_ms=30000):
    """
    Fetch a JS-heavy page using headless Chromium.
    Returns rendered HTML.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
        )
        page = context.new_page()
        try:
            page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            page.wait_for_timeout(wait_ms)
            html = page.content()
        finally:
            browser.close()
    return html


def strip_html(html):
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&#39;", "'").replace("&quot;", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    test_urls = [
        ("Make it in Germany Jobs",
         "https://www.make-it-in-germany.com/en/looking-for-foreign-professionals/jobs"),
        ("EURES",
         "https://eures.europa.eu/index_en"),
    ]

    for label, url in test_urls:
        print("\n" + "=" * 70)
        print(f"[{label}] {url}")
        print("=" * 70)
        try:
            html = fetch_rendered(url)
            text = strip_html(html)
            print(f"HTML: {len(html):,} bytes")
            print(f"Text: {len(text):,} chars")
            print(f"\nPreview (first 800 chars):")
            print(text[:800])
        except Exception as e:
            print(f"FAIL: {e}")