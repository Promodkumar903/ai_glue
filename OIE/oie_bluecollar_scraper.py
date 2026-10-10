"""Blue-collar scraper — सिर्फ C/D class companies से jobs"""
import os, sys, time, sqlite3, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from companies_bluecollar import BLUE_COLLAR_COMPANIES, get_blue_collar_by_region
import requests

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
]

# C/D class keywords — इन titles को priority दो
BLUE_COLLAR_KEYWORDS = [
    "driver", "worker", "cleaner", "security", "mason", "welder", "plumber",
    "guard", "technician", "helper", "operator", "cook", "chef", "packer",
    "loader", "warehouse", "construction", "electrician", "carpenter",
    "painter", "mechanic", "fitter", "machine", "production", "packaging",
    "sorting", "kitchen", "housekeeping", "laundry", "server", "waiter",
    "farm", "harvest", "greenhouse", "meat", "slaughter", "butcher"
]

def is_blue_collar(title):
    t = title.lower()
    return any(kw in t for kw in BLUE_COLLAR_KEYWORDS)

def fetch_custom(careers_url):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return []
    
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--disable-blink-features=AutomationControlled", "--no-sandbox",
            "--disable-dev-shm-usage"])
        ctx = browser.new_context(user_agent=random.choice(UAS),
                                   viewport={"width":1920,"height":1080}, locale="en-US")
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        page = ctx.new_page()
        try:
            page.goto(careers_url, timeout=40000, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)
            selectors = ["a[href*='/job/']", "a[href*='/jobs/']", "a[href*='/position/']",
                "a[href*='/opening/']", "a[href*='/vacancy/']", "a[href*='/career/']",
                ".job-card a", ".job-listing a", ".position a", "li.job a",
                "article a", "[class*='JobCard'] a"]
            for sel in selectors:
                try:
                    els = page.query_selector_all(sel)
                    for el in els[:60]:
                        title = (el.inner_text() or "").strip().replace("\n"," ")[:120]
                        href = el.get_attribute("href") or ""
                        if title and 4 < len(title) < 130 and href:
                            if href.startswith("http"): full_url = href
                            elif href.startswith("/"):
                                from urllib.parse import urlparse
                                pp = urlparse(careers_url)
                                full_url = f"{pp.scheme}://{pp.netloc}{href}"
                            else: full_url = careers_url.rstrip("/") + "/" + href.lstrip("/")
                            jobs.append({"title": title, "location": "", "url": full_url})
                    if len(jobs) >= 5: break
                except: continue
        except: pass
        finally:
            try: browser.close()
            except: pass
    
    seen, unique = set(), []
    for j in jobs:
        k = (j["title"].lower(), j["url"])
        if k not in seen: seen.add(k); unique.append(j)
    return unique

def scan_and_save(region=None):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    companies = BLUE_COLLAR_COMPANIES if not region else get_blue_collar_by_region(region)
    print(f"\n🌍 Scanning {len(companies)} blue-collar companies...\n")
    
    total_saved = 0
    blue_collar_saved = 0
    for i, comp in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] 🔍 {comp['name']} ({comp['sector']})...", flush=True)
        try:
            jobs = fetch_custom(comp["careers_url"])
            saved = 0
            for j in jobs:
                try:
                    cur.execute("""INSERT OR IGNORE INTO scraped_company_jobs
                        (company_name, company_country, company_region, job_title,
                         job_location, job_url, requisition_id, ats_platform)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (comp["name"], comp["country"], comp["region"],
                         j["title"], j.get("location",""), j["url"], "", "custom"))
                    if cur.rowcount > 0:
                        saved += 1
                        if is_blue_collar(j["title"]):
                            blue_collar_saved += 1
                except: pass
            conn.commit()
            total_saved += saved
            print(f"     → {len(jobs)} found, {saved} new saved")
        except Exception as e:
            print(f"     ❌ {e}")
        time.sleep(random.uniform(1, 2))
    conn.close()
    print(f"\n✅ Total new: {total_saved}, of which blue-collar: {blue_collar_saved}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default=None)
    args = ap.parse_args()
    scan_and_save(args.region)