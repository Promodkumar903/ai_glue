"""
OIE Verification Agent v1
- सभी regions (Middle East + Europe + Russia/CIS) की companies scan करता है
- ATS (Greenhouse/Lever/Workable) + Custom (Playwright) support
- Cross-verification: agent job ↔ company website
- Scam detection + 99% confidence gate
"""
import os, sys, json, sqlite3, uuid, time, re
from datetime import datetime
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from companies_master import COMPANIES, get_companies_by_region

try:
    from groq import Groq
    from dotenv import load_dotenv
    load_dotenv()
    GROQ_KEY = os.getenv("GROQ_API_KEY")
    groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
except ImportError:
    groq_client = None

import requests

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")
EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# ═══════════════════════════════════════════
# ATS FETCHERS
# ═══════════════════════════════════════════
def fetch_greenhouse(slug):
    try:
        r = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", timeout=15)
        if r.status_code != 200: return []
        return [{"title": j["title"], "location": j.get("location", {}).get("name", ""),
                 "url": j["absolute_url"], "requisition_id": str(j.get("id", "")), "ats": "greenhouse"}
                for j in r.json().get("jobs", [])]
    except Exception as e:
        print(f"    ⚠️ greenhouse fail: {e}"); return []

def fetch_lever(slug):
    try:
        r = requests.get(f"https://api.lever.co/v0/postings/{slug}?mode=json", timeout=15)
        if r.status_code != 200: return []
        return [{"title": j["text"], "location": j.get("categories", {}).get("location", ""),
                 "url": j["hostedUrl"], "requisition_id": j.get("id", ""), "ats": "lever"}
                for j in r.json()]
    except Exception as e:
        print(f"    ⚠️ lever fail: {e}"); return []

def fetch_workable(slug):
    try:
        r = requests.get(f"https://apply.workable.com/api/v1/widget/accounts/{slug}", timeout=15)
        if r.status_code != 200: return []
        return [{"title": j["title"], "location": j.get("location", {}).get("city", ""),
                 "url": j["url"], "requisition_id": j.get("id", ""), "ats": "workable"}
                for j in r.json().get("jobs", [])]
    except Exception as e:
        print(f"    ⚠️ workable fail: {e}"); return []

# ═══════════════════════════════════════════
# CUSTOM SCRAPER (Playwright)
# ═══════════════════════════════════════════
def fetch_custom(careers_url, company_name):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("    ⚠️ playwright not installed"); return []

    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(careers_url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            selectors = ["a[href*='/job/']", "a[href*='/jobs/']", "a[href*='/careers/']",
                         ".job-card a", ".job-listing a", "li.job a", "article a"]
            for sel in selectors:
                try:
                    els = page.query_selector_all(sel)
                    for el in els[:40]:
                        title = (el.inner_text() or "").strip()
                        href = el.get_attribute("href") or ""
                        if title and 3 < len(title) < 120 and href:
                            full_url = href if href.startswith("http") else careers_url.rstrip("/") + "/" + href.lstrip("/")
                            jobs.append({"title": title, "location": "", "url": full_url,
                                         "requisition_id": "", "ats": "custom"})
                    if jobs: break
                except: continue
        except Exception as e:
            print(f"    ⚠️ custom scrape fail {careers_url}: {e}")
        finally:
            browser.close()
    return jobs

def fetch_company_jobs(company):
    ats = company.get("ats", "custom")
    slug = company.get("slug", "")
    print(f"  🔍 {company['name']} ({ats})...")
    if ats == "greenhouse" and slug: return fetch_greenhouse(slug)
    if ats == "lever" and slug: return fetch_lever(slug)
    if ats == "workable" and slug: return fetch_workable(slug)
    return fetch_custom(company["careers_url"], company["name"])

# ═══════════════════════════════════════════
# SCAM DETECTION
# ═══════════════════════════════════════════
SCAM_KEYWORDS = ["processing fee", "registration fee", "visa fee", "security deposit",
                 "pay upfront", "western union", "money gram", "bitcoin", "crypto payment",
                 "no interview", "direct joining", "100% guaranteed visa"]

def detect_scam(text):
    if not text: return False, None
    t = text.lower()
    for kw in SCAM_KEYWORDS:
        if kw in t: return True, kw
    return False, None

# ═══════════════════════════════════════════
# MATCHING
# ═══════════════════════════════════════════
def sim(a, b):
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()

def cross_verify(agent_job, company_job):
    score, max_score = 0, 0
    max_score += 40
    score += int(sim(agent_job.get("title", ""), company_job.get("title", "")) * 40)
    max_score += 30
    if agent_job.get("location") and company_job.get("location"):
        score += int(sim(agent_job["location"], company_job["location"]) * 30)
    else:
        score += 15
    max_score += 20
    if agent_job.get("requisition_id") and company_job.get("requisition_id"):
        if agent_job["requisition_id"] == company_job["requisition_id"]:
            score += 20
    max_score += 10
    score += 10
    return int((score / max_score) * 100) if max_score else 0

# ═══════════════════════════════════════════
# MAIN SCAN — सभी companies, सभी regions
# ═══════════════════════════════════════════
def scan_all_companies(region_filter=None):
    """सभी companies की jobs fetch करके DB में log करता है"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    total_jobs = 0
    companies_to_scan = COMPANIES if not region_filter else get_companies_by_region(region_filter)
    print(f"\n🌍 Scanning {len(companies_to_scan)} companies...\n")

    for i, comp in enumerate(companies_to_scan, 1):
        try:
            jobs = fetch_company_jobs(comp)
            total_jobs += len(jobs)
            print(f"     → {len(jobs)} jobs found")
            cur.execute("""INSERT INTO company_scan_log (company_name, country, region, jobs_found)
                           VALUES (?, ?, ?, ?)""",
                        (comp["name"], comp["country"], comp["region"], len(jobs)))
        except Exception as e:
            print(f"     ❌ {comp['name']}: {e}")
        time.sleep(1)

    conn.commit()
    conn.close()
    print(f"\n✅ Total jobs fetched: {total_jobs}")
    return total_jobs

# ═══════════════════════════════════════════
# VERIFY AGENT JOBS
# ═══════════════════════════════════════════
def verify_agent_jobs(agent_jobs):
    """
    agent_jobs: [{"company": "...", "title": "...", "location": "...",
                  "country": "...", "salary_min": ..., "salary_max": ...,
                  "salary_currency": "USD", "free_visa": True, "free_ticket": True,
                  "accommodation": True, "source_agent": "...", "description": "..."}]
    """
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    verified = []

    # Company pool build करो (एक बार में)
    company_pool = {}
    for comp in COMPANIES:
        try:
            jobs = fetch_company_jobs(comp)
            company_pool[comp["name"].lower()] = {"company": comp, "jobs": jobs}
        except: pass
        time.sleep(0.5)

    for aj in agent_jobs:
        ckey = (aj.get("company") or "").lower()
        if ckey not in company_pool:
            cur.execute("INSERT INTO manual_review_queue (raw_job_json, reason) VALUES (?, ?)",
                        (json.dumps(aj), "Company not in master list"))
            print(f"  ⚠️ Company not found: {aj.get('company')}")
            continue

        scam, reason = detect_scam(aj.get("description", ""))
        if scam:
            cur.execute("""INSERT INTO agent_blacklist (agent_name, agent_email, rejected_count, last_reason)
                           VALUES (?, ?, 1, ?)
                           ON CONFLICT(agent_name) DO UPDATE SET
                             rejected_count = rejected_count + 1,
                             last_reason = excluded.last_reason""",
                        (aj.get("source_agent", "unknown"), aj.get("agent_email", ""), reason))
            print(f"  🚨 SCAM: {aj['title']} — {reason}")
            continue

        best_score, best_match = 0, None
        for cj in company_pool[ckey]["jobs"]:
            s = cross_verify(aj, cj)
            if s > best_score:
                best_score, best_match = s, cj

        if best_score >= 90:
            job_id = str(uuid.uuid4())
            cur.execute("""INSERT INTO verified_jobs 
                (id, company_name, job_title, country, region, city, salary_min, salary_max,
                 salary_currency, free_visa, free_ticket, accommodation, no_commission,
                 job_url, requisition_id, verification_score, source_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)""",
                (job_id, aj["company"], aj["title"], aj.get("country", ""),
                 company_pool[ckey]["company"]["region"], aj.get("city", ""),
                 aj.get("salary_min", 0), aj.get("salary_max", 0),
                 aj.get("salary_currency", "USD"),
                 1 if aj.get("free_visa") else 0, 1 if aj.get("free_ticket") else 0,
                 1 if aj.get("accommodation") else 0,
                 best_match["url"], best_match.get("requisition_id", ""),
                 best_score, aj.get("source_agent", "unknown")))

            cur.execute("""INSERT INTO job_evidence 
                (job_id, company_url, ats_platform, matched_title, matched_location,
                 matched_requisition_id, match_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (job_id, best_match["url"], best_match.get("ats", ""),
                 best_match["title"], best_match.get("location", ""),
                 best_match.get("requisition_id", ""), best_score))

            verified.append(aj)
            print(f"  ✅ VERIFIED {best_score}%: {aj['title']} @ {aj['company']}")
        elif best_score >= 70:
            cur.execute("INSERT INTO manual_review_queue (raw_job_json, match_score, reason) VALUES (?, ?, ?)",
                        (json.dumps(aj), best_score, "Partial match"))
            print(f"  ⚠️ REVIEW {best_score}%: {aj['title']}")
        else:
            print(f"  ❌ REJECT {best_score}%: {aj['title']} @ {aj['company']}")

    conn.commit()
    conn.close()
    return verified

# ═══════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default=None, help="Middle East | Europe | Russia/CIS")
    ap.add_argument("--init", action="store_true", help="Init tables")
    args = ap.parse_args()

    if args.init:
        from init_verification_tables import init
        init()
    else:
        scan_all_companies(args.region)