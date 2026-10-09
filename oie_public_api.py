"""OIE Public API — Stats endpoint for landing page"""
import sqlite3
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/oie", tags=["OIE Public"])
DB = "ai_glue.db"


@router.get("/stats")
def get_stats():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    stats = {"universities": 0, "jobs": 0, "scholarships": 0, "pr_friendly": 0, "companies": 0}
    try:
        cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE status='DISCOVERED'")
        stats["universities"] = cur.fetchone()[0]
    except: pass
    try:
        cur.execute("SELECT COUNT(*) FROM opportunities WHERE status='DISCOVERED'")
        stats["jobs"] = cur.fetchone()[0]
    except: pass
    try:
        cur.execute("SELECT COUNT(*) FROM scholarships")
        stats["scholarships"] = cur.fetchone()[0]
    except: pass
    try:
        cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE pr_possible=1")
        stats["pr_friendly"] = cur.fetchone()[0]
    except: pass
    try:
        cur.execute("SELECT COUNT(*) FROM company_intel")
        stats["companies"] = cur.fetchone()[0]
    except: pass
    conn.close()
    return stats