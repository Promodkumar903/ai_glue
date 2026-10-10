"""
Candidate ↔ Job Matcher
- Match score 50+ वाली jobs candidates को भेजता है
- Top 20 jobs per candidate
- AI Glue logo CID-attached (Gmail में हमेशा दिखेगा)
"""
import os, sys, sqlite3, smtplib, uuid
from datetime import datetime
from email.message import EmailMessage
from email.utils import make_msgid
from urllib.parse import quote
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE_DIR, "ai_glue.db")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
PORTAL_BASE = os.getenv("PORTAL_URL", "http://localhost:5173")

# Logo paths
LOGO_PATH = os.path.join(BASE_DIR, "frontend", "public", "logo.png")
LOGO_DARK_PATH = os.path.join(BASE_DIR, "frontend", "public", "logo-dark.png")


# ═══════════════════════════════════════════
# Matching Logic
# ═══════════════════════════════════════════
def match_score(candidate, job):
    score = 0
    target_countries = (candidate.get("target_countries") or "").lower()
    job_country = (job.get("country") or "").lower()
    if job_country and target_countries and job_country in target_countries:
        score += 40
    elif target_countries and not job_country:
        score += 5

    field = (candidate.get("field_of_study") or "").lower()
    title = (job.get("job_title") or "").lower()
    if field and title:
        field_words = [w for w in field.split() if len(w) > 3]
        for w in field_words:
            if w in title:
                score += 30
                break

    budget = candidate.get("budget_usd") or 0
    salary_min = job.get("salary_min") or 0
    if salary_min and budget and salary_min >= budget * 0.8:
        score += 20
    elif salary_min:
        score += 10
    else:
        score += 5

    exp = candidate.get("work_experience_years") or 0
    score += 10 if exp <= 2 else 5

    return min(score, 100)


# ═══════════════════════════════════════════
# Send Match Email
# ═══════════════════════════════════════════
def send_match_email(to_email, candidate_name, job, score):
    """Email with CID-embedded AI Glue logo"""
    company = job.get('company_name', 'Company') or 'Company'
    title = job.get('job_title', 'Position') or 'Position'
    country = job.get('country', 'Unknown') or 'Unknown'
    job_url = job.get('job_url', '') or '#'
    job_id = job.get('id', '') or ''

    # Company initials
    words = [w for w in company.split() if w and w[0].isalpha()]
    if len(words) >= 2:
        initials = (words[0][0] + words[1][0]).upper()
    elif words:
        initials = words[0][:2].upper()
    else:
        initials = "CO"

    portal_url = f"{PORTAL_BASE}/jobs/{job_id}"
    company_search = f"https://www.google.com/search?q={quote(company + ' careers official')}"

    subject = f"Job Match ({score}%) - {title} at {company}"

    # CID refs
    ai_glue_cid = make_msgid(domain="aiglue.com")[1:-1]
    ai_glue_dark_cid = make_msgid(domain="aiglue.com")[1:-1]

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, Helvetica, sans-serif; max-width: 620px; margin: 0 auto; padding: 20px; color: #1f2937; background: #f3f4f6;">

  <div style="text-align: center; padding: 24px; background: #ffffff; border-bottom: 3px solid #6366f1; border-radius: 12px 12px 0 0;">
    <img src="cid:{ai_glue_cid}" alt="AI Glue" width="160" style="max-width: 160px; height: auto; display: block; margin: 0 auto;" />
    <div style="font-size: 14px; color: #6366f1; margin-top: 12px; font-weight: 600;">Verified Job Match</div>
  </div>

  <div style="background: white; padding: 24px;">
    <p style="margin: 0 0 16px; font-size: 15px;">Hi <b>{candidate_name or 'there'}</b>,</p>
    <p style="margin: 0 0 20px; font-size: 15px; color: #4b5563;">A new job matching your profile is now available:</p>

    <div style="background: #f9fafb; padding: 20px; border-radius: 10px; border: 1px solid #e5e7eb;">
      <table style="width: 100%; border-collapse: collapse;">
        <tr>
          <td style="width: 76px; vertical-align: top;">
            <div style="width: 64px; height: 64px; background: #6366f1; border-radius: 10px; color: white; text-align: center; line-height: 64px; font-size: 24px; font-weight: bold; letter-spacing: 1px;">{initials}</div>
          </td>
          <td style="vertical-align: top; padding-left: 12px;">
            <div style="font-size: 18px; font-weight: bold; color: #111827; line-height: 1.3;">{title}</div>
            <div style="font-size: 14px; color: #6b7280; margin-top: 6px;">{company}</div>
          </td>
        </tr>
      </table>
      <table style="width: 100%; margin-top: 16px; font-size: 14px; border-collapse: collapse;">
        <tr><td style="padding: 6px 0; color: #6b7280; width: 120px;">Location</td><td style="padding: 6px 0; font-weight: bold;">{country}</td></tr>
        <tr><td style="padding: 6px 0; color: #6b7280;">Match Score</td><td style="padding: 6px 0; font-weight: bold; color: #6366f1;">{score}%</td></tr>
      </table>
    </div>

    <div style="margin-top: 20px; padding: 16px; background: #eef2ff; border-left: 4px solid #6366f1; border-radius: 6px;">
      <div style="font-weight: bold; margin-bottom: 10px; font-size: 14px; color: #4338ca;">Benefits</div>
      <div style="font-size: 14px; line-height: 1.8; color: #374151;">
        {"[YES] Free Visa provided" if job.get('free_visa') else "[NO] Visa not mentioned"}<br/>
        {"[YES] Free Air Ticket" if job.get('free_ticket') else "[NO] Ticket not mentioned"}<br/>
        {"[YES] Accommodation" if job.get('accommodation') else "[NO] Accommodation not mentioned"}<br/>
        {"[YES] No Commission" if job.get('no_commission') else "[NO] Commission info missing"}
      </div>
    </div>

    <div style="text-align: center; padding: 28px 0 16px;">
      <a href="{portal_url}" style="display: inline-block; padding: 16px 40px; background: #6366f1; color: white !important; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 16px;">Apply through AI Glue &raquo;</a>
      <div style="font-size: 12px; color: #9ca3af; margin-top: 10px;">Login required (we protect you from scams)</div>
    </div>

    <div style="padding-top: 20px; margin-top: 20px; border-top: 1px solid #e5e7eb; font-size: 13px;">
      <div style="margin-bottom: 8px;"><a href="{company_search}" style="color: #6366f1; text-decoration: none;">Learn about {company}</a></div>
      <div><a href="{job_url}" style="color: #9ca3af; text-decoration: none;">View original source listing</a></div>
    </div>
  </div>

  <div style="text-align: center; padding: 28px 20px; background: #1f2937; border-radius: 0 0 12px 12px;">
    <img src="cid:{ai_glue_dark_cid}" alt="AI Glue" width="130" style="max-width: 130px; height: auto; display: block; margin: 0 auto; opacity: 0.95;" />
    <div style="font-size: 13px; color: #9ca3af; margin-top: 12px;">Verified Jobs &middot; Global Opportunities</div>
    <div style="font-size: 11px; color: #6b7280; margin-top: 14px; line-height: 1.6;">&copy; 2026 AI Glue &middot; You received this because you signed up for job alerts.<br/><a href="{PORTAL_BASE}/unsubscribe" style="color: #6b7280; text-decoration: underline;">Unsubscribe</a></div>
  </div>

</body>
</html>"""

    text_body = f"""Hi {candidate_name or 'there'},

A new job matching your profile is available on AI Glue:

Company:  {company}
Position: {title}
Location: {country}
Match:    {score}%

Benefits:
{"[YES] Free Visa" if job.get('free_visa') else "[NO] Visa not mentioned"}
{"[YES] Free Ticket" if job.get('free_ticket') else "[NO] Ticket not mentioned"}
{"[YES] Accommodation" if job.get('accommodation') else "[NO] Accommodation not mentioned"}
{"[YES] No Commission" if job.get('no_commission') else "[NO] Commission missing"}

Apply through AI Glue Portal:
{portal_url}

Company info: {company_search}
Original source: {job_url}

Best regards,
AI Glue - OIE Team
"""

    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["Reply-To"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    html_part = msg.get_payload()[1]

    # Attach logos as CID
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            html_part.add_related(f.read(), 'image', 'png', cid=f"<{ai_glue_cid}>")

    if os.path.exists(LOGO_DARK_PATH):
        with open(LOGO_DARK_PATH, "rb") as f:
            html_part.add_related(f.read(), 'image', 'png', cid=f"<{ai_glue_dark_cid}>")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        return True, None
    except Exception as e:
        return False, str(e)


# ═══════════════════════════════════════════
# Notification
# ═══════════════════════════════════════════
def create_notification(user_id, job, score):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    notif_id = str(uuid.uuid4())
    title = f"New Job Match ({score}%)"
    message = f"{job.get('job_title', '')} @ {job.get('company_name', '')} - {job.get('country', 'Unknown')}"
    try:
        cur.execute("""INSERT INTO notifications (id, user_id, title, message, is_read, created_at)
            VALUES (?, ?, ?, ?, 0, ?)""",
            (notif_id, user_id, title, message, datetime.utcnow().isoformat()))
        conn.commit()
        return notif_id
    except Exception as e:
        print(f"Notif fail: {e}")
        return None
    finally:
        conn.close()


# ═══════════════════════════════════════════
# Main
# ═══════════════════════════════════════════
def run_matcher(min_score=50, send_email=True, top_n=20):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        candidates = [dict(r) for r in cur.execute("SELECT * FROM student_profiles_oie").fetchall()]
    except:
        candidates = []

    try:
        jobs = [dict(r) for r in cur.execute("SELECT * FROM verified_jobs WHERE status='VERIFIED'").fetchall()]
    except:
        jobs = []

    if not candidates or not jobs:
        print(f"⚠️ Candidates: {len(candidates)}, Jobs: {len(jobs)}")
        conn.close()
        return

    print(f"🔍 Matching {len(candidates)} candidates × {len(jobs)} jobs (min score: {min_score}, top {top_n})\n")

    matches_sent = 0
    for cand in candidates:
        user_id = cand.get("user_id")
        if not user_id:
            continue

        user_row = cur.execute("SELECT email, full_name FROM users WHERE id=?", (user_id,)).fetchone()
        if user_row:
            email = user_row["email"]
            name = user_row["full_name"]
        else:
            email = None
            name = "Student"

        scored = []
        for job in jobs:
            score = match_score(cand, job)
            if score >= min_score:
                scored.append((score, job))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_jobs = scored[:top_n]

        print(f"\n👤 {name} ({email or user_id}) — {len(top_jobs)} matches")

        for score, job in top_jobs:
            existing = cur.execute("""SELECT id FROM notifications
                WHERE user_id=? AND message LIKE ? LIMIT 1""",
                (user_id, f"%{job['job_title']}%{job['company_name']}%")).fetchone()
            if existing:
                continue

            create_notification(user_id, job, score)

            if send_email and email:
                ok, err = send_match_email(email, name, job, score)
                if ok:
                    print(f"  ✉️  {job['job_title'][:50]} @ {job['company_name'][:30]} ({score}%)")
                else:
                    print(f"  ❌ Email fail: {err}")
            else:
                print(f"  🔔 {job['job_title'][:50]} ({score}%)")

            matches_sent += 1

    conn.close()
    print(f"\n✅ Total matches sent: {matches_sent}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-score", type=int, default=50)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--no-email", action="store_true")
    args = ap.parse_args()
    run_matcher(min_score=args.min_score, send_email=not args.no_email, top_n=args.top)