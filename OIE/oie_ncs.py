"""
OIE NCS India — National Career Service (Gov)
"""
import requests
import json
from oie_real_jobs import save_job

NCS_API = "https://www.ncs.gov.in/_vti_bin/NCSAPI/JobSearch.svc/SearchJobs"


def fetch_ncs(keyword="nurse", limit=20):
    """NCS India job search"""
    print(f"[NCS India] Searching: {keyword}")
    payload = {
        "keyword": keyword,
        "pageNo": 1,
        "pageSize": limit,
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        r = requests.post(NCS_API, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        jobs = data.get("d", {}).get("results", []) if isinstance(data, dict) else []
        print(f"  Got {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"  NCS API failed: {e}")
        return []


def extract_ncs(raw):
    """Map NCS to our schema"""
    return {
        "title": raw.get("jobTitle") or raw.get("title") or "UNKNOWN",
        "country": "India",
        "city": raw.get("location") or "UNKNOWN",
        "salary": 0,
        "currency": "INR",
        "visa_sponsorship": "UNKNOWN",
        "accommodation": "UNKNOWN",
        "airfare": "UNKNOWN",
        "food": "UNKNOWN",
        "transport": "UNKNOWN",
        "experience_years": 0,
        "education": raw.get("qualification") or "UNKNOWN",
        "language": "UNKNOWN",
        "skills": [],
        "application_url": raw.get("jobUrl") or raw.get("applyLink") or "UNKNOWN",
        "_evidence_text": raw.get("jobDescription", "")[:1000],
        "_employer": raw.get("employerName") or "UNKNOWN",
    }


if __name__ == "__main__":
    keywords = ["nurse", "developer", "engineer", "driver", "security"]

    total = 0
    for kw in keywords:
        jobs = fetch_ncs(kw, limit=20)
        for raw in jobs:
            extracted = extract_ncs(raw)
            result = save_job("ncs", extracted)
            if result:
                total += 1

    print(f"\nTotal NCS jobs saved: {total}")