"""
AI Glue — Daily Report Generator + Scheduler
(Yeh file poori tarah alag hai, existing notification.py se connected nahi)
"""
import os
import csv
import smtplib
import sqlite3
import requests
from datetime import datetime
from email.message import EmailMessage
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# ---------------- Config ----------------
DB_PATH = "ai_glue.db"
REPORTS_DIR = "reports"


def _env_bool(key, default=False):
    v = os.getenv(key, str(default)).lower()
    return v in ("1", "true", "yes", "on")


# ---------------- CSV Generator ----------------
def generate_daily_report_csv():
    """Aaj ka data CSV mein nikalta hai. Returns (csv_path, summary_dict)"""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    csv_path = os.path.join(REPORTS_DIR, f"daily_report_{today}.csv")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # --- Today's leads ---
    cur.execute("""
        SELECT student_name, email, country, course, stage
        FROM leads WHERE DATE(created_at) = DATE('now')
        ORDER BY created_at DESC
    """)
    today_leads = cur.fetchall()

    # --- Today's payments ---
    cur.execute("""
        SELECT amount, currency, status, payee_type, gateway_ref
        FROM payments WHERE DATE(created_at) = DATE('now')
        ORDER BY created_at DESC
    """)
    today_payments = cur.fetchall()

    # --- Pending payments ---
    cur.execute("""
        SELECT amount, currency, status, payee_type
        FROM payments WHERE status IN ('PENDING','PROCESSING','INITIATED')
        ORDER BY created_at DESC LIMIT 100
    """)
    pending_payments = cur.fetchall()

    # --- Visa updates today ---
    cur.execute("""
        SELECT COUNT(*) FROM visa_cases
        WHERE DATE(COALESCE(last_checked_at, created_at)) = DATE('now')
    """)
    visa_updates = cur.fetchone()[0]

    # --- Active leads count ---
    cur.execute("""
        SELECT COUNT(*) FROM leads WHERE stage NOT IN ('LOST','CONVERTED')
    """)
    active_leads = cur.fetchone()[0]

    # --- Total visa cases ---
    cur.execute("SELECT COUNT(*) FROM visa_cases")
    total_visa = cur.fetchone()[0]

    # --- Totals ---
    today_payment_total = sum(
        float(r["amount"] or 0) for r in today_payments if r["status"] == "SUCCESS"
    )
    pending_total = sum(float(r["amount"] or 0) for r in pending_payments)

    # --- Write CSV ---
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Type", "Name/Detail", "Country/Type",
                    "Status", "Amount", "Notes"])
        for r in today_leads:
            w.writerow([today, "LEAD", r["student_name"], r["country"] or "",
                        r["stage"] or "", "", r["email"] or ""])
        for r in today_payments:
            w.writerow([today, "PAYMENT", r["payee_type"] or "", r["currency"] or "",
                        r["status"] or "", r["amount"] or 0, r["gateway_ref"] or ""])
        for r in pending_payments:
            w.writerow([today, "PENDING", r["payee_type"] or "", r["currency"] or "",
                        r["status"] or "", r["amount"] or 0, ""])

    conn.close()

    summary = {
        "date": today,
        "today_leads": len(today_leads),
        "today_payment": today_payment_total,
        "pending_payment": pending_total,
        "pending_count": len(pending_payments),
        "visa_updates": visa_updates,
        "active_leads": active_leads,
        "total_visa": total_visa,
    }
    return csv_path, summary


def _build_summary_text(summary):
    return (
        f"📅 Date: {summary['date']}\n\n"
        f"✅ Aaj ke naye leads: {summary['today_leads']}\n"
        f"💰 Aaj ka payment: ₹{summary['today_payment']:,.0f}\n"
        f"⏳ Pending payment: ₹{summary['pending_payment']:,.0f} "
        f"({summary['pending_count']} clients)\n"
        f"📋 Visa updates aaj: {summary['visa_updates']}\n"
        f"👥 Active leads (total): {summary['active_leads']}\n"
        f"📂 Total visa cases: {summary['total_visa']}"
    )


# ---------------- Email ----------------
def send_email_report(csv_path, summary):
    if not _env_bool("ENABLE_EMAIL", True):
        return (False, "Email disabled")
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")
    to = os.getenv("REPORT_EMAIL_TO") or user
    if not (host and user and pwd):
        return (False, "SMTP not configured in .env")

    try:
        msg = EmailMessage()
        msg["From"] = user
        msg["To"] = to
        msg["Subject"] = f"AI Glue — Daily Report {summary['date']}"
        msg.set_content(_build_summary_text(summary))

        if os.path.exists(csv_path):
            with open(csv_path, "rb") as f:
                msg.add_attachment(f.read(), maintype="text",
                                   subtype="csv",
                                   filename=os.path.basename(csv_path))

        with smtplib.SMTP(host, port, timeout=20) as s:
            s.starttls()
            s.login(user, pwd)
            s.send_message(msg)
        return (True, f"Email sent to {to}")
    except Exception as e:
        return (False, f"Email error: {e}")


# ---------------- Telegram ----------------
def send_telegram_report(csv_path, summary):
    if not _env_bool("ENABLE_TELEGRAM", False):
        return (False, "Telegram disabled")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return (False, "Telegram token/chat_id not set")

    try:
        base = f"https://api.telegram.org/bot{token}"
        text = f"*AI Glue Daily Report — {summary['date']}*\n\n{_build_summary_text(summary)}"
        r1 = requests.post(f"{base}/sendMessage",
                           json={"chat_id": chat_id, "text": text,
                                 "parse_mode": "Markdown"}, timeout=20)
        if r1.status_code != 200:
            return (False, f"Telegram text failed: {r1.text}")

        if os.path.exists(csv_path):
            with open(csv_path, "rb") as f:
                r2 = requests.post(f"{base}/sendDocument",
                                   data={"chat_id": chat_id},
                                   files={"document": f}, timeout=30)
            if r2.status_code != 200:
                return (True, f"Text sent, CSV failed: {r2.text}")
        return (True, f"Telegram sent to {chat_id}")
    except Exception as e:
        return (False, f"Telegram error: {e}")


# ---------------- WhatsApp (Disabled by default) ----------------
def send_whatsapp_report(csv_path, summary):
    if not _env_bool("ENABLE_WHATSAPP", False):
        return (False, "WhatsApp disabled")
    # Jab client pay kare, tab yahan Twilio code add karenge
    return (False, "WhatsApp not implemented yet")


# ---------------- Viber (Disabled by default) ----------------
def send_viber_report(csv_path, summary):
    if not _env_bool("ENABLE_VIBER", False):
        return (False, "Viber disabled")
    return (False, "Viber not implemented yet")


# ---------------- Master Runner ----------------
def run_daily_report():
    """Yeh function scheduler se call hoga"""
    print("[DailyReport] Starting...")
    try:
        csv_path, summary = generate_daily_report_csv()
        print(f"[DailyReport] CSV: {csv_path}")

        channels = [
            ("email", send_email_report),
            ("telegram", send_telegram_report),
            ("whatsapp", send_whatsapp_report),
            ("viber", send_viber_report),
        ]
        results = []
        for name, fn in channels:
            ok, msg = fn(csv_path, summary)
            results.append({"channel": name, "ok": ok, "msg": msg})
            print(f"[DailyReport] {name}: {'OK' if ok else 'SKIP/FAIL'} — {msg}")

        return {"summary": summary, "results": results, "csv": csv_path}
    except Exception as e:
        print(f"[DailyReport] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ---------------- APScheduler Setup ----------------
_scheduler = None


def start_daily_report_scheduler():
    global _scheduler
    if not _env_bool("ENABLE_DAILY_REPORT", False):
        print("[DailyReport] Scheduler DISABLED (ENABLE_DAILY_REPORT=false)")
        return
    if _scheduler is not None:
        return

    time_str = os.getenv("DAILY_REPORT_TIME", "21:00")
    try:
        hh, mm = time_str.split(":")
    except Exception:
        hh, mm = "21", "00"

    _scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    _scheduler.add_job(run_daily_report,
                       CronTrigger(hour=int(hh), minute=int(mm)),
                       id="daily_report", replace_existing=True)
    _scheduler.start()
    print(f"[DailyReport] Scheduler STARTED — daily at {time_str} IST")