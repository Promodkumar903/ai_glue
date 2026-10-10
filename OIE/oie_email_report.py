"""OIE Email Report — Daily summary"""
import os
import sqlite3
import smtplib
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
DB = "ai_glue.db"


def get_stats():
    conn = sqlite3.connect(DB); cur = conn.cursor()
    s = {}
    for key, q in [
        ("jobs", "SELECT COUNT(*) FROM opportunities WHERE status='DISCOVERED'"),
        ("universities", "SELECT COUNT(*) FROM study_opportunities WHERE status='DISCOVERED'"),
        ("scholarships", "SELECT COUNT(*) FROM scholarships"),
        ("verified_jobs", "SELECT COUNT(*) FROM hr_contacts WHERE verification_status='VERIFIED'"),
        ("job_agents", "SELECT COUNT(*) FROM registry_entities"),
        ("study_agents", "SELECT COUNT(*) FROM study_agents"),
        ("conflicts", "SELECT COUNT(*) FROM verification_conflicts WHERE resolved=0"),
    ]:
        try:
            cur.execute(q); s[key] = cur.fetchone()[0]
        except: s[key] = 0
    conn.close()
    return s


def get_new_jobs(limit=5):
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT title, company, country FROM opportunities
        WHERE status='DISCOVERED' AND DATE(created_at)=DATE('now')
        ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_conflicts(limit=5):
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT field_name, conflict_values, severity FROM verification_conflicts
            WHERE resolved=0 OR resolved IS NULL
            ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        rows = [dict(r) for r in cur.fetchall()]
    except:
        rows = []
    conn.close()
    return rows


def build_html(stats, jobs, conflicts):
    today = datetime.now().strftime('%d %b %Y')
    jobs_html = "".join([f"<li><b>{j.get('title','')}</b> @ {j.get('company','')} ({j.get('country','')})</li>" for j in jobs]) or "<li>No new jobs today</li>"
    conflicts_html = "".join([f"<li><b>{c.get('field_name','')}</b>: {c.get('conflict_values','')} — <i>{c.get('severity','')}</i></li>" for c in conflicts]) or "<li>No open conflicts</li>"

    return f"""
    <html><body style="font-family:Arial;max-width:640px;margin:auto;padding:20px;color:#1e293b">
    <div style="background:linear-gradient(135deg,#8B5CF6,#EC4899);padding:20px;border-radius:12px;color:white">
      <h1 style="margin:0">✨ AI Glue OIE</h1>
      <p style="margin:5px 0 0;opacity:0.9">Daily Report — {today}</p>
    </div>
    <h2>📊 Platform Stats</h2>
    <table style="width:100%;border-collapse:collapse;background:#f8fafc;border-radius:8px">
      <tr><td style="padding:10px">💼 Live Jobs</td><td style="text-align:right;padding:10px"><b>{stats.get('jobs',0)}</b></td></tr>
      <tr><td style="padding:10px">🎓 Universities</td><td style="text-align:right;padding:10px"><b>{stats.get('universities',0)}</b></td></tr>
      <tr><td style="padding:10px">🏆 Scholarships</td><td style="text-align:right;padding:10px"><b>{stats.get('scholarships',0)}</b></td></tr>
      <tr><td style="padding:10px">✅ Verified Jobs</td><td style="text-align:right;padding:10px"><b>{stats.get('verified_jobs',0)}</b></td></tr>
      <tr><td style="padding:10px">👥 Job Agents</td><td style="text-align:right;padding:10px"><b>{stats.get('job_agents',0)}</b></td></tr>
      <tr><td style="padding:10px">🎯 Study Agents</td><td style="text-align:right;padding:10px"><b>{stats.get('study_agents',0)}</b></td></tr>
      <tr><td style="padding:10px">⚠️ Open Conflicts</td><td style="text-align:right;padding:10px"><b style="color:#dc2626">{stats.get('conflicts',0)}</b></td></tr>
    </table>
    <h2>🆕 New Jobs Today</h2>
    <ul>{jobs_html}</ul>
    <h2>⚠️ Conflicts Needing Review</h2>
    <ul>{conflicts_html}</ul>
    <p style="color:#94a3b8;font-size:12px;margin-top:30px">AI Glue OIE · Automated Report · {today}</p>
    </body></html>
    """


def send_email(html_body):
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    pwd = os.getenv("SMTP_PASS", "")
    to = os.getenv("REPORT_EMAIL_TO") or user
    if not (host and user and pwd and to):
        return False, "SMTP not configured in .env"

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = f"AI Glue OIE — Daily Report {datetime.now().strftime('%d %b')}"
    msg.set_content("Daily OIE Report — view in HTML")
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(host, port, timeout=20) as s:
            s.starttls()
            s.login(user, pwd)
            s.send_message(msg)
        return True, f"Email sent to {to}"
    except Exception as e:
        return False, str(e)


def run():
    print("=" * 60)
    print("OIE EMAIL REPORT")
    print("=" * 60)
    stats = get_stats()
    jobs = get_new_jobs(5)
    conflicts = get_conflicts(5)
    print("\nStats:", stats)
    print(f"Jobs today: {len(jobs)}")
    print(f"Conflicts: {len(conflicts)}")
    html = build_html(stats, jobs, conflicts)
    ok, msg = send_email(html)
    print(f"\n{'OK' if ok else 'FAIL'}: {msg}")
    return ok


if __name__ == "__main__":
    run()