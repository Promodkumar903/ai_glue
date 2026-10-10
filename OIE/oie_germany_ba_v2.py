"""Bundesagentur für Arbeit v6 — Corrected field names"""
import os, sys, sqlite3, requests, time, random

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

BLUE_COLLAR_SEARCHES = [
    "Berufskraftfahrer", "Lagerhelfer", "Reinigungskraft", "Produktionshelfer",
    "Koch", "Bauhelfer", "Maler", "Maurer", "Schweißer", "Elektriker",
    "Küchenhilfe", "Gärtner", "Metzger", "Bäcker", "Fleischer",
    "Paketfahrer", "Sicherheitsmitarbeiter", "Altenpfleger", "Krankenpfleger",
    "Verkäufer", "Kellner", "Zimmermann", "Dachdecker", "Fliesenleger",
    "Tischler", "Mechaniker", "Schlosser", "Lagerist", "Kommissionierer",
    "Busfahrer", "Kranführer", "Baggerführer", "Gabelstaplerfahrer",
]

HEADERS = {
    "X-API-Key": "jobboerse-jobsuche",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "de-DE,de;q=0.9",
}

def search_jobs(keyword, size=100):
    url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
    params = {"was": keyword, "size": size, "page": 1}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return []
        data = r.json()
        return data.get("ergebnisliste", [])   # ← correct field
    except Exception as e:
        print(f"     ❌ {e}")
        return []

def fetch_and_save():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    total_saved = 0
    
    print(f"🌍 Scanning {len(BLUE_COLLAR_SEARCHES)} blue-collar categories...\n")
    
    for i, keyword in enumerate(BLUE_COLLAR_SEARCHES, 1):
        print(f"[{i}/{len(BLUE_COLLAR_SEARCHES)}] 🔍 {keyword}...", flush=True)
        jobs = search_jobs(keyword)
        print(f"     → {len(jobs)} found")
        
        saved = 0
        for j in jobs:
            # Correct field names
            title = (j.get("stellenangebotsTitel") or "").strip()
            if not title:
                continue
            
            company = j.get("firma", "Unknown")
            refnr = j.get("referenznummer", "")
            
            # Location — nested structure
            location = ""
            locs = j.get("stellenlokationen") or []
            if locs and isinstance(locs, list):
                addr = locs[0].get("adresse", {})
                ort = addr.get("ort", "")
                plz = addr.get("plz", "")
                land = addr.get("land", "DEUTSCHLAND")
                location = f"{plz} {ort}, {land}".strip()
            
            # URL
            job_url = j.get("externeURL") or f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{refnr}"
            
            # Country check — Deutschland only
            country = "Germany"
            if location and "OESTERREICH" in location:
                country = "Austria"
            elif location and "SCHWEIZ" in location:
                country = "Switzerland"
            
            try:
                cur.execute("""INSERT OR IGNORE INTO scraped_company_jobs
                    (company_name, company_country, company_region, job_title,
                     job_location, job_url, requisition_id, ats_platform)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (company, country, "Europe", title, location, job_url, refnr, "bundesagentur"))
                if cur.rowcount > 0:
                    saved += 1
                    if saved <= 2:
                        print(f"       ✅ {title[:60]} @ {company[:30]}")
            except: pass
        
        conn.commit()
        total_saved += saved
        print(f"     → {saved} new saved")
        time.sleep(random.uniform(0.3, 0.8))
    
    conn.close()
    print(f"\n✅ Total new jobs saved: {total_saved}")

if __name__ == "__main__":
    fetch_and_save()