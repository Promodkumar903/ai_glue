from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    print("Testing example.com...")
    page.goto("https://example.com", timeout=15000)
    print("Title:", page.title())
    print("Content length:", len(page.content()))

    print("\nTesting Wikipedia...")
    page.goto("https://en.wikipedia.org/wiki/Germany", timeout=20000)
    print("Title:", page.title())
    print("Content length:", len(page.content()))

    browser.close()
    print("\nPlaywright WORKS")