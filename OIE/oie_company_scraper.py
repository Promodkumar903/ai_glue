"""OIE Company Scraper v3 — HTTP/2 fallback, saves to DB"""
import os, sys, time, sqlite3, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from companies_master import COMPANIES, get_companies_by_region
import requests

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
]

# ═══════════════════════════════════════════
# JUNK FILTER — navigation links skip
# ═══════════════════════════════════════════
JUNK_KEYWORDS = [
    "saved jobs", "search jobs", "search all jobs", "view all jobs",
    "entry-level roles", "early career", "follow us", "faqs", "support",
    "discover more", "about us", "who we are", "what we do",
    "view open roles", "view positions", "discover our", "our locations",
    "job search", "how to apply", "culture and benefits",
    "learn more", "read more", "get to know", "real people",
    "click here", "see more", "find out more", "our story",
    "privacy policy", "terms of service", "cookie policy",
    "sign in", "log in", "register", "subscribe", "newsletter",
    "contact us", "help center", "career home", "back to",
    "built on ownership", "driven by collaboration",
    "trainee programmes", "managers", "finance and more",
    "review accommodations", "discover the faces",
]

def is_real_job_title(title):
    if not title or len(title) < 5 or len(title) > 90:
        return False
    t = title.lower().strip()
    for junk in JUNK_KEYWORDS:
        if t == junk or t.startswith(junk):
            return False
    generic = ["career", "sales", "managers", "supply chain", "finance",
               "programmes", "internship", "job search"]
    if t in generic:
        return False
    return True

def fetch_greenhouse(slug):
    try:
        r = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
                         headers={"User-Agent": random.choice(UAS)}, timeout=15)
        if r.status_code != 200: return []
        return [{"title": j["title"], "location": j.get("location", {}).get("name", ""),
                 "url": j["absolute_url"], "requisition_id": str(j.get("id", "")), "ats": "greenhouse"}
                for j in r.json().get("jobs", [])]
    except: return []

def fetch_lever(slug):
    try:
        r = requests.get(f"https://api.lever.co/v0/postings/{slug}?mode=json",
                         headers={"User-Agent": random.choice(UAS)}, timeout=15)
        if r.status_code != 200: return []
        return [{"title": j["text"], "location": j.get("categories", {}).get("location", ""),
                 "url": j["hostedUrl"], "requisition_id": j.get("id", ""), "ats": "lever"}
                for j in r.json()]
    except: return []

def fetch_workable(slug):
    try:
        r = requests.get(f"https://apply.workable.com/api/v1/widget/accounts/{slug}",
                         headers={"User-Agent": random.choice(UAS)}, timeout=15)
        if r.status_code != 200: return []
        return [{"title": j["title"], "location": j.get("location", {}).get("city", ""),
                 "url": j["url"], "requisition_id": j.get("id", ""), "ats": "workable"}
                for j in r.json().get("jobs", [])]
    except: return []

def _try_scrape(careers_url, disable_http2=False):
    from playwright.sync_api import sync_playwright
    args = ["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
    if disable_http2:
        args.append("--disable-http2")
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=args)
        ctx = browser.new_context(user_agent=random.choice(UAS),
                                   viewport={"width":1920,"height":1080}, locale="en-US")
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        page = ctx.new_page()
        try:
            page.goto(careers_url, timeout=40000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            selectors = ["a[href*='/job/']", "a[href*='/jobs/']", "a[href*='/position/']",
                "a[href*='/opening/']", "a[href*='/vacancy/']", "a[href*='/career/']",
                ".job-card a", ".job-listing a", ".job-item a", ".position a",
                "li.job a", "article a", "[class*='JobCard'] a", "[class*='job-card'] a"]
            for sel in selectors:
                try:
                    els = page.query_selector_all(sel)
                    for el in els[:80]:
                        title = (el.inner_text() or "").strip().replace("\n"," ")[:120]
                        href = el.get_attribute("href") or ""
                        if title and 4 < len(title) < 130 and href:
                            if href.startswith("http"): full_url = href
                            elif href.startswith("/"):
                                from urllib.parse import urlparse
                                pp = urlparse(careers_url)
                                full_url = f"{pp.scheme}://{pp.netloc}{href}"
                            else: full_url = careers_url.rstrip("/") + "/" + href.lstrip("/")
                            if is_real_job_title(title):
                                jobs.append({"title": title, "location": "", "url": full_url,
                                             "requisition_id": "", "ats": "custom"})
                    if len(jobs) >= 5: break
                except: continue
        except: pass
        finally:
            try: browser.close()
            except: pass
    return jobs

def fetch_custom(careers_url):
    jobs = _try_scrape(careers_url, disable_http2=False)
    if len(jobs) >= 3: return jobs
    jobs2 = _try_scrape(careers_url, disable_http2=True)
    if len(jobs2) > len(jobs): jobs = jobs2
    seen, unique = set(), []
    for j in jobs:
        k = (j["title"].lower(), j["url"])
        if k not in seen: seen.add(k); unique.append(j)
    return unique
# ═══════════════════════════════════════════
# JUNK TITLE FILTER — navigation links skip
# ═══════════════════════════════════════════
JUNK_KEYWORDS = [
    "saved jobs", "search jobs", "search all jobs", "view all jobs",
    "entry-level roles", "early career", "follow us", "faqs", "support",
    "discover more", "about us", "who we are", "what we do",
    "view open roles", "view positions", "discover our", "our locations",
    "job search", "how to apply", "culture and benefits",
    "learn more", "read more", "get to know", "real people",
    "click here", "see more", "find out more", "our story",
    "privacy policy", "terms of service", "cookie policy",
    "sign in", "log in", "register", "subscribe", "newsletter",
    "contact us", "help center", "career home", "back to",
    "built on ownership", "driven by collaboration",
    "trainee programmes", "managers", "finance and more",
]

def is_real_job_title(title):
    """Junk navigation links और useful job titles में फर्क करो"""
    if not title or len(title) < 4:
        return False
    if len(title) > 80:  # real job titles इतने लंबे नहीं होते
        return False
    t = title.lower().strip()
    for junk in JUNK_KEYWORDS:
        if t == junk or t.startswith(junk):
            return False
    # Ye generic single-word links skip करो
    generic_single_words = ["career", "sales", "managers", "supply chain",
                            "finance", "programmes", "internship"]
    if t in generic_single_words:
        return False
    return True

def fetch_company(company):
    ats = company.get("ats","custom"); slug = company.get("slug","")
    if ats == "greenhouse" and slug: return fetch_greenhouse(slug)
    if ats == "lever" and slug: return fetch_lever(slug)
    if ats == "workable" and slug: return fetch_workable(slug)
    return fetch_custom(company["careers_url"])

def scan_and_save(region_filter=None):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    companies = COMPANIES if not region_filter else get_companies_by_region(region_filter)
    print(f"\n🌍 Scanning {len(companies)} companies...\n")
    total = 0
    for i, comp in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] 🔍 {comp['name']}...", flush=True)
        try:
            jobs = fetch_company(comp)
            saved = 0
            for j in jobs:
                try:
                    cur.execute("""INSERT OR IGNORE INTO scraped_company_jobs
                        (company_name, company_country, company_region, job_title,
                         job_location, job_url, requisition_id, ats_platform)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (comp["name"], comp["country"], comp["region"],
                         j["title"], j.get("location",""), j["url"],
                         j.get("requisition_id",""), j.get("ats","custom")))
                    if cur.rowcount > 0: saved += 1
                except: pass
            conn.commit()
            total += saved
            print(f"     → {len(jobs)} found, {saved} new saved")
        except Exception as e:
            print(f"     ❌ {e}")
        time.sleep(random.uniform(1, 2))
    conn.close()
    print(f"\n✅ Total new jobs saved: {total}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default=None)
    args = ap.parse_args()
    scan_and_save(args.region)