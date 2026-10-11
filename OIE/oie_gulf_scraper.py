"""
Gulf Scraper — Bayt.com + NaukriGulf
Scrapes C/D class (blue-collar) jobs from UAE, Saudi, Qatar, Kuwait, Bahrain, Oman.
Uses Playwright stealth to bypass bot detection.
"""
import os, sys, time, sqlite3, random, re
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

# Blue-collar job keywords (English + Arabic-ish)
BLUE_COLLAR_KEYWORDS = [
    "driver", "worker", "cleaner", "security", "guard", "mason", "welder",
    "plumber", "technician", "helper", "operator", "cook", "chef", "packer",
    "loader", "warehouse", "construction", "electrician", "carpenter",
    "painter", "mechanic", "fitter", "machine", "production", "packaging",
    "kitchen", "housekeeping", "laundry", "waiter", "server", "farm",
    "harvest", "butcher", "baker", "tailor", "gardener", "nurse",
    "caregiver", "housemaid", "maid", "nanny", "chauffeur", "delivery",
    "mover", "steel", "fixer", "mep", "hvac", "ac", "plumber", "pipe",
    "fabricator", "rigger", "denter", "tinsmith", "blacksmith", "moulder",
    "crane", "forklift", "bulldozer", "excavator", "dump", "loader"
]

# Gulf search URLs (multiple pages per category)
BAYT_SEARCHES = [
    # ═══════════════════════════════════════════
    # UAE — सबसे बड़ा market
    # ═══════════════════════════════════════════
    ("https://www.bayt.com/en/uae/jobs/driver-jobs/", "UAE", "Driver"),
    ("https://www.bayt.com/en/uae/jobs/construction-jobs/", "UAE", "Construction"),
    ("https://www.bayt.com/en/uae/jobs/security-jobs/", "UAE", "Security"),
    ("https://www.bayt.com/en/uae/jobs/cleaning-jobs/", "UAE", "Cleaning"),
    ("https://www.bayt.com/en/uae/jobs/warehouse-jobs/", "UAE", "Warehouse"),
    ("https://www.bayt.com/en/uae/jobs/technician-jobs/", "UAE", "Technician"),
    ("https://www.bayt.com/en/uae/jobs/cook-jobs/", "UAE", "Cook"),
    ("https://www.bayt.com/en/uae/jobs/welder-jobs/", "UAE", "Welder"),
    ("https://www.bayt.com/en/uae/jobs/electrician-jobs/", "UAE", "Electrician"),
    ("https://www.bayt.com/en/uae/jobs/mechanic-jobs/", "UAE", "Mechanic"),
    ("https://www.bayt.com/en/uae/jobs/housekeeping-jobs/", "UAE", "Housekeeping"),
    ("https://www.bayt.com/en/uae/jobs/nurse-jobs/", "UAE", "Nurse"),
    ("https://www.bayt.com/en/uae/jobs/delivery-driver-jobs/", "UAE", "Delivery Driver"),
    ("https://www.bayt.com/en/uae/jobs/steel-fixer-jobs/", "UAE", "Steel Fixer"),
    ("https://www.bayt.com/en/uae/jobs/mep-technician-jobs/", "UAE", "MEP Technician"),
    ("https://www.bayt.com/en/uae/jobs/pipe-fitter-jobs/", "UAE", "Pipe Fitter"),
    ("https://www.bayt.com/en/uae/jobs/ac-technician-jobs/", "UAE", "AC Technician"),
    ("https://www.bayt.com/en/uae/jobs/painter-jobs/", "UAE", "Painter"),
    ("https://www.bayt.com/en/uae/jobs/mason-jobs/", "UAE", "Mason"),
    ("https://www.bayt.com/en/uae/jobs/factory-worker-jobs/", "UAE", "Factory Worker"),
    ("https://www.bayt.com/en/uae/jobs/storekeeper-jobs/", "UAE", "Storekeeper"),
    ("https://www.bayt.com/en/uae/jobs/waiter-jobs/", "UAE", "Waiter"),
    ("https://www.bayt.com/en/uae/jobs/baker-jobs/", "UAE", "Baker"),
    ("https://www.bayt.com/en/uae/jobs/butcher-jobs/", "UAE", "Butcher"),
    ("https://www.bayt.com/en/uae/jobs/barber-jobs/", "UAE", "Barber"),
    ("https://www.bayt.com/en/uae/jobs/gardener-jobs/", "UAE", "Gardener"),
    ("https://www.bayt.com/en/uae/jobs/laundry-jobs/", "UAE", "Laundry"),
    ("https://www.bayt.com/en/uae/jobs/kitchen-helper-jobs/", "UAE", "Kitchen Helper"),
    ("https://www.bayt.com/en/uae/jobs/forklift-operator-jobs/", "UAE", "Forklift"),
    ("https://www.bayt.com/en/uae/jobs/heavy-equipment-operator-jobs/", "UAE", "Heavy Equipment"),
    ("https://www.bayt.com/en/uae/jobs/scaffolder-jobs/", "UAE", "Scaffolder"),
    ("https://www.bayt.com/en/uae/jobs/tiler-jobs/", "UAE", "Tiler"),
    ("https://www.bayt.com/en/uae/jobs/plumber-jobs/", "UAE", "Plumber"),
    ("https://www.bayt.com/en/uae/jobs/aluminium-fitter-jobs/", "UAE", "Aluminium Fitter"),
    ("https://www.bayt.com/en/uae/jobs/auto-mechanic-jobs/", "UAE", "Auto Mechanic"),
    
    # ═══════════════════════════════════════════
    # SAUDI ARABIA
    # ═══════════════════════════════════════════
    ("https://www.bayt.com/en/saudi-arabia/jobs/driver-jobs/", "Saudi Arabia", "Driver"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/construction-jobs/", "Saudi Arabia", "Construction"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/warehouse-jobs/", "Saudi Arabia", "Warehouse"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/technician-jobs/", "Saudi Arabia", "Technician"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/security-jobs/", "Saudi Arabia", "Security"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/electrician-jobs/", "Saudi Arabia", "Electrician"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/mechanic-jobs/", "Saudi Arabia", "Mechanic"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/welder-jobs/", "Saudi Arabia", "Welder"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/nurse-jobs/", "Saudi Arabia", "Nurse"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/steel-fixer-jobs/", "Saudi Arabia", "Steel Fixer"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/pipe-fitter-jobs/", "Saudi Arabia", "Pipe Fitter"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/mason-jobs/", "Saudi Arabia", "Mason"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/painter-jobs/", "Saudi Arabia", "Painter"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/cleaner-jobs/", "Saudi Arabia", "Cleaner"),
    ("https://www.bayt.com/en/saudi-arabia/jobs/cook-jobs/", "Saudi Arabia", "Cook"),
    
    # ═══════════════════════════════════════════
    # QATAR
    # ═══════════════════════════════════════════
    ("https://www.bayt.com/en/qatar/jobs/driver-jobs/", "Qatar", "Driver"),
    ("https://www.bayt.com/en/qatar/jobs/construction-jobs/", "Qatar", "Construction"),
    ("https://www.bayt.com/en/qatar/jobs/warehouse-jobs/", "Qatar", "Warehouse"),
    ("https://www.bayt.com/en/qatar/jobs/security-jobs/", "Qatar", "Security"),
    ("https://www.bayt.com/en/qatar/jobs/technician-jobs/", "Qatar", "Technician"),
    ("https://www.bayt.com/en/qatar/jobs/electrician-jobs/", "Qatar", "Electrician"),
    ("https://www.bayt.com/en/qatar/jobs/welder-jobs/", "Qatar", "Welder"),
    ("https://www.bayt.com/en/qatar/jobs/mason-jobs/", "Qatar", "Mason"),
    ("https://www.bayt.com/en/qatar/jobs/cook-jobs/", "Qatar", "Cook"),
    ("https://www.bayt.com/en/qatar/jobs/cleaner-jobs/", "Qatar", "Cleaner"),
    
    # ═══════════════════════════════════════════
    # KUWAIT
    # ═══════════════════════════════════════════
    ("https://www.bayt.com/en/kuwait/jobs/driver-jobs/", "Kuwait", "Driver"),
    ("https://www.bayt.com/en/kuwait/jobs/construction-jobs/", "Kuwait", "Construction"),
    ("https://www.bayt.com/en/kuwait/jobs/warehouse-jobs/", "Kuwait", "Warehouse"),
    ("https://www.bayt.com/en/kuwait/jobs/technician-jobs/", "Kuwait", "Technician"),
    ("https://www.bayt.com/en/kuwait/jobs/security-jobs/", "Kuwait", "Security"),
    ("https://www.bayt.com/en/kuwait/jobs/cleaner-jobs/", "Kuwait", "Cleaner"),
    ("https://www.bayt.com/en/kuwait/jobs/cook-jobs/", "Kuwait", "Cook"),
    ("https://www.bayt.com/en/kuwait/jobs/nurse-jobs/", "Kuwait", "Nurse"),
    
    # ═══════════════════════════════════════════
    # OMAN
    # ═══════════════════════════════════════════
    ("https://www.bayt.com/en/oman/jobs/driver-jobs/", "Oman", "Driver"),
    ("https://www.bayt.com/en/oman/jobs/construction-jobs/", "Oman", "Construction"),
    ("https://www.bayt.com/en/oman/jobs/warehouse-jobs/", "Oman", "Warehouse"),
    ("https://www.bayt.com/en/oman/jobs/technician-jobs/", "Oman", "Technician"),
    ("https://www.bayt.com/en/oman/jobs/security-jobs/", "Oman", "Security"),
    ("https://www.bayt.com/en/oman/jobs/cook-jobs/", "Oman", "Cook"),
    
    # ═══════════════════════════════════════════
    # BAHRAIN
    # ═══════════════════════════════════════════
    ("https://www.bayt.com/en/bahrain/jobs/driver-jobs/", "Bahrain", "Driver"),
    ("https://www.bayt.com/en/bahrain/jobs/construction-jobs/", "Bahrain", "Construction"),
    ("https://www.bayt.com/en/bahrain/jobs/security-jobs/", "Bahrain", "Security"),
    ("https://www.bayt.com/en/bahrain/jobs/cleaner-jobs/", "Bahrain", "Cleaner"),
    ("https://www.bayt.com/en/bahrain/jobs/warehouse-jobs/", "Bahrain", "Warehouse"),
]

NAUKRI_SEARCHES = [
    # Correct NaukriGulf URL format: /{keyword}-jobs-in-{country}
    ("https://www.naukrigulf.com/driver-jobs-in-uae", "UAE", "Driver"),
    ("https://www.naukrigulf.com/construction-jobs-in-uae", "UAE", "Construction"),
    ("https://www.naukrigulf.com/warehouse-jobs-in-uae", "UAE", "Warehouse"),
    ("https://www.naukrigulf.com/security-jobs-in-uae", "UAE", "Security"),
    ("https://www.naukrigulf.com/cleaner-jobs-in-uae", "UAE", "Cleaner"),
    ("https://www.naukrigulf.com/cook-jobs-in-uae", "UAE", "Cook"),
    ("https://www.naukrigulf.com/driver-jobs-in-saudi-arabia", "Saudi Arabia", "Driver"),
    ("https://www.naukrigulf.com/construction-jobs-in-saudi-arabia", "Saudi Arabia", "Construction"),
    ("https://www.naukrigulf.com/driver-jobs-in-qatar", "Qatar", "Driver"),
    ("https://www.naukrigulf.com/construction-jobs-in-qatar", "Qatar", "Construction"),
    ("https://www.naukrigulf.com/driver-jobs-in-kuwait", "Kuwait", "Driver"),
    ("https://www.naukrigulf.com/driver-jobs-in-oman", "Oman", "Driver"),
    ("https://www.naukrigulf.com/driver-jobs-in-bahrain", "Bahrain", "Driver"),
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

JUNK_KEYWORDS = [
    "search jobs", "view all jobs", "saved jobs", "follow us",
    "about us", "who we are", "contact us", "privacy policy",
    "terms of use", "cookie", "sign in", "register", "newsletter",
    "job alerts", "employers", "career advice", "login", "post job",
]


def is_real_job_title(title):
    """Filter out navigation links and junk"""
    if not title or len(title) < 5 or len(title) > 100:
        return False
    t = title.lower().strip()
    for junk in JUNK_KEYWORDS:
        if t == junk or t.startswith(junk):
            return False
    return True


def is_blue_collar(title):
    """Check if title matches C/D class keywords"""
    t = title.lower()
    return any(kw in t for kw in BLUE_COLLAR_KEYWORDS)


def _try_scrape(url, wait_ms=5000, disable_http2=False):
    """Playwright stealth scrape"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("   X Playwright not installed. Run: pip install playwright")
        return []

    args = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ]
    if disable_http2:
        args.append("--disable-http2")

    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=args)
        ctx = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        ctx.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
        """)

        page = ctx.new_page()
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(wait_ms + 3000)  # Extra wait for JS

            # Scroll to load lazy content
            for _ in range(3):
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                page.wait_for_timeout(1500)

            # Job card selectors (Bayt + NaukriGulf)
                       # Job card selectors — separate for each source
            if "naukrigulf" in url.lower():
                selectors = [
                    "div[class*='job-tittle'] a",       # NaukriGulf specific
                    "div[class*='jobTuple'] a",
                    "h2 a",                              # Usually wraps title
                    "article h2 a",
                    "div[class*='list'] a[href*='jobs-in']",
                    "a[href*='/job/']",
                    "a[class*='title']",
                ]
            else:
                # Bayt.com
                selectors = [
                    "li[class*='has-pointer-d'] a",
                    "div[class*='job-card'] a",
                    "h2 a",
                    "article a",
                    "li[class*='job'] a",
                    "a[class*='job-title']",
                    "a[href*='/jobs/']",
                    "a[href*='/job/']",
                ]
            seen_urls = set()
            for sel in selectors:
                try:
                    els = page.query_selector_all(sel)
                    for el in els[:80]:
                        title = (el.inner_text() or "").strip().replace("\n", " ")[:130]
                        href = el.get_attribute("href") or ""
                        if title and 5 < len(title) < 130 and href:
                            if href.startswith("http"):
                                full_url = href
                            elif href.startswith("/"):
                                from urllib.parse import urlparse
                                pp = urlparse(url)
                                full_url = f"{pp.scheme}://{pp.netloc}{href}"
                            else:
                                full_url = url.rstrip("/") + "/" + href.lstrip("/")

                            if full_url in seen_urls:
                                continue
                            seen_urls.add(full_url)

                            if is_real_job_title(title):
                                jobs.append({
                                    "title": title,
                                    "url": full_url,
                                    "location": "",
                                })
                    if len(jobs) >= 10:
                        break
                except Exception:
                    continue

        except Exception as e:
            pass
        finally:
            try:
                browser.close()
            except Exception:
                pass

    return jobs


def fetch_with_fallback(url):
    """Try normal, then with HTTP/2 disabled"""
    jobs = _try_scrape(url, wait_ms=5000, disable_http2=False)
    if len(jobs) >= 3:
        return jobs
    jobs2 = _try_scrape(url, wait_ms=5000, disable_http2=True)
    if len(jobs2) > len(jobs):
        return jobs2
    return jobs


def scan_and_save(source_name, searches):
    """Scan a source (Bayt/NaukriGulf) and save to DB"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    total_saved = 0
    blue_saved = 0

    print(f"\n{'='*60}")
    print(f"  {source_name} — {len(searches)} search queries")
    print(f"{'='*60}\n")

    for i, (url, country, category) in enumerate(searches, 1):
        print(f"[{i}/{len(searches)}] {country} | {category}")
        print(f"    URL: {url[:70]}...", flush=True)

        try:
            jobs = fetch_with_fallback(url)
            print(f"    -> {len(jobs)} jobs found")

            saved = 0
            for j in jobs:
                try:
                    cur.execute("""INSERT OR IGNORE INTO scraped_company_jobs
                        (company_name, company_country, company_region, job_title,
                         job_location, job_url, requisition_id, ats_platform)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (f"{source_name} Listing", country, "Middle East",
                         j["title"], j.get("location", ""), j["url"], "",
                         source_name.lower().replace(".", "_")))
                    if cur.rowcount > 0:
                        saved += 1
                        if is_blue_collar(j["title"]):
                            blue_saved += 1
                            if blue_saved <= 5:
                                print(f"      * {j['title'][:70]}")
                except Exception:
                    pass

            conn.commit()
            total_saved += saved
            print(f"    -> {saved} new saved\n")

        except Exception as e:
            print(f"    X {e}\n")

        time.sleep(random.uniform(2, 4))

    conn.close()
    print(f"\n{'='*60}")
    print(f"  {source_name} TOTAL: {total_saved} new, {blue_saved} blue-collar")
    print(f"{'='*60}\n")
    return total_saved, blue_saved


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["bayt", "naukri", "both"], default="both")
    args = ap.parse_args()

    grand_total = 0
    grand_blue = 0

    if args.source in ("bayt", "both"):
        t, b = scan_and_save("Bayt.com", BAYT_SEARCHES)
        grand_total += t
        grand_blue += b

    if args.source in ("naukri", "both"):
        t, b = scan_and_save("NaukriGulf", NAUKRI_SEARCHES)
        grand_total += t
        grand_blue += b

    print(f"\n>>> GRAND TOTAL: {grand_total} new jobs, {grand_blue} blue-collar\n")


if __name__ == "__main__":
    main()