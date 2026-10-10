"""
Arbeitnow Blue-Collar Jobs — Germany
Free API: 325+ jobs daily
Filters to C/D class only: driver, warehouse, cleaner, production, etc.
"""
import os, sys, sqlite3, requests
from datetime import datetime

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

BLUE_COLLAR_KEYWORDS = [
    "fahrer", "driver", "lager", "warehouse", "produktion", "production",
    "reinigung", "cleaner", "cleaning", "küche", "kitchen", "koch", "cook",
    "helfer", "helper", "monteur", "mechanic", "mechaniker", "techniker",
    "technician", "bau", "construction", "metzger", "butcher", "bäcker",
    "baker", "pflege", "care", "sicherheit", "security", "garten", "garden",
    "landwirt", "farm", "fleisch", "meat", "verpackung", "packaging",
    "stapler", "forklift", "transport", "logistik", "logistics",
    "handwerker", "craftsman", "schweißer", "welder", "installateur",
]

def is_blue_collar(title):
    t = title.lower()
    return any(kw in t for kw in BLUE_COLLAR_KEYWORDS)

def fetch_and_save():
    print("🔍 Fetching from Arbeitnow API...")
    try:
        r = requests.get("https://www.arbeitnow.com/api/job-board-api", timeout=20)
        data = r.json().get("data", [])
    except Exception as e:
        print(f"❌ API failed: {e}")
        return
    
    print(f"📊 Total jobs from API: {len(data)}")
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    saved = 0
    blue_saved = 0
    
    for j in data:
        title = j.get("title", "").strip()
        if not title:
            continue
        
        try:
            cur.execute("""INSERT OR IGNORE INTO scraped_company_jobs
                (company_name, company_country, company_region, job_title,
                 job_location, job_url, requisition_id, ats_platform)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (j.get("company_name", "Unknown"), "Germany", "Europe",
                 title, j.get("location", ""), j.get("url", ""),
                 str(j.get("slug", "")), "arbeitnow"))
            
            if cur.rowcount > 0:
                saved += 1
                if is_blue_collar(title):
                    blue_saved += 1
                    print(f"  ✅ {title} @ {j.get('company_name', '?')} / {j.get('location', '?')}")
        except Exception as e:
            pass
    
    conn.commit()
    conn.close()
    
    print(f"\n📥 Total new saved: {saved}")
    print(f"🔧 Of which blue-collar: {blue_saved}")

if __name__ == "__main__":
    fetch_and_save()