"""
OIE Master Context — Unified view of every job
Combines: Job details + Benefits + HR Contact + Company Profile
Ek single row mein sab kuch
"""
import sqlite3
import json

DB = "ai_glue.db"


# ============================================================
# CREATE MASTER VIEW
# ============================================================
def create_master_view():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Drop if exists
    cur.execute("DROP VIEW IF EXISTS job_full_context")

    cur.execute("""
        CREATE VIEW job_full_context AS
        SELECT
            jbd.id as benefit_id,
            jbd.company_name,
            jbd.country,
            hrc.city,
            jbd.job_title,
            jbd.category,
            
            -- Salary (linked from opportunities if available)
            o.salary as salary_text,
            
            -- Work conditions
            jbd.hours_per_day,
            jbd.days_per_week,
            jbd.overtime_available,
            jbd.overtime_rate,
            jbd.off_days,
            jbd.shift_timing,
            jbd.shift_type,
            jbd.night_shift,
            
            -- Travel benefits
            jbd.visa_free,
            jbd.visa_type,
            jbd.ticket_free,
            jbd.ticket_type,
            jbd.airport_pickup,
            
            -- Stay
            jbd.accommodation,
            jbd.accommodation_type,
            jbd.accommodation_ac,
            
            -- Food
            jbd.food_lunch,
            jbd.food_dinner,
            jbd.food_breakfast,
            jbd.food_allowance_usd,
            
            -- Extras
            jbd.medical_insurance,
            jbd.transport_free,
            jbd.uniform_free,
            
            -- Contract
            jbd.contract_duration_months,
            jbd.leave_days_per_year,
            
            -- HR Contact
            hrc.hr_name,
            hrc.hr_designation,
            hrc.hr_email,
            hrc.hr_phone,
            hrc.hr_whatsapp,
            hrc.website,
            hrc.linkedin_url,
            
            -- Company profile
            hrc.company_legal_name,
            hrc.company_size,
            hrc.industry,
            hrc.founded_year,
            hrc.company_description,
            
            -- Verification status
            hrc.verification_status,
            hrc.verified_at,
            jbd.verified as job_verified,
            
            -- Source
            jbd.source
        
        FROM job_benefits_deep jbd
        LEFT JOIN hr_contacts hrc ON LOWER(hrc.company_name) = LOWER(jbd.company_name)
        LEFT JOIN opportunities o ON LOWER(o.company) = LOWER(jbd.company_name)
    """)

    conn.commit()
    conn.close()
    print("OK: job_full_context view created")


# ============================================================
# PRINT FULL CONTEXT — Ek Company
# ============================================================
def print_full_context(company_name):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM job_full_context
        WHERE LOWER(company_name) LIKE ?
    """, (f"%{company_name.lower()}%",))
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    conn.close()

    if not rows:
        print(f"❌ {company_name} not found")
        return

    for row in rows:
        ctx = dict(zip(cols, row))
        print("\n" + "=" * 90)
        print(f"🏢 {ctx['company_name']} — {ctx['job_title']}")
        print("=" * 90)

        # Company
        print(f"\n📋 COMPANY PROFILE")
        print(f"  Legal Name:     {ctx.get('company_legal_name') or 'N/A'}")
        print(f"  Industry:       {ctx.get('industry') or 'N/A'}")
        print(f"  Founded:        {ctx.get('founded_year') or 'N/A'}")
        print(f"  Size:           {ctx.get('company_size') or 'N/A'}")
        print(f"  Website:        {ctx.get('website') or 'N/A'}")
        print(f"  LinkedIn:       {ctx.get('linkedin_url') or 'N/A'}")

        # Job
        print(f"\n💼 JOB DETAILS")
        print(f"  Position:       {ctx['job_title']}")
        print(f"  Category:       {ctx.get('category') or 'N/A'}")
        print(f"  Location:       {ctx.get('city') or ''}, {ctx.get('country') or 'N/A'}")
        print(f"  Salary:         {ctx.get('salary_text') or 'N/A'}")

        # Work conditions
        print(f"\n⏰ WORK CONDITIONS")
        print(f"  Hours/Day:      {ctx.get('hours_per_day') or 'N/A'}")
        print(f"  Days/Week:      {ctx.get('days_per_week') or 'N/A'}")
        print(f"  Off Days:       {ctx.get('off_days') or 'N/A'}")
        print(f"  Shift Timing:   {ctx.get('shift_timing') or 'N/A'}")
        print(f"  Shift Type:     {ctx.get('shift_type') or 'N/A'}")
        print(f"  Overtime:       {'✅ Available' if ctx.get('overtime_available') else '❌ No'} ({ctx.get('overtime_rate') or 'N/A'})")
        print(f"  Night Shift:    {'✅ Yes' if ctx.get('night_shift') else '❌ No'}")

        # Benefits
        print(f"\n🎁 BENEFITS")
        print(f"  Visa:           {'✅ Free' if ctx.get('visa_free') else '❌ Not provided'} ({ctx.get('visa_type') or 'N/A'})")
        print(f"  Ticket:         {'✅ Free' if ctx.get('ticket_free') else '❌ Not provided'} ({ctx.get('ticket_type') or 'N/A'})")
        print(f"  Airport Pickup: {'✅ Yes' if ctx.get('airport_pickup') else '❌ No'}")
        print(f"  Accommodation:  {'✅ Yes' if ctx.get('accommodation') else '❌ No'} ({ctx.get('accommodation_type') or 'N/A'})")
        food = []
        if ctx.get('food_lunch'): food.append('Lunch')
        if ctx.get('food_dinner'): food.append('Dinner')
        if ctx.get('food_breakfast'): food.append('Breakfast')
        print(f"  Food:           {'✅ ' + ', '.join(food) if food else '❌ No food'}")
        if ctx.get('food_allowance_usd'):
            print(f"  Food Allowance: ${ctx['food_allowance_usd']}")
        print(f"  Medical Ins:    {'✅ Yes' if ctx.get('medical_insurance') else '❌ No'}")
        print(f"  Transport:      {'✅ Free' if ctx.get('transport_free') else '❌ No'}")
        print(f"  Uniform:        {'✅ Free' if ctx.get('uniform_free') else '❌ No'}")

        # Contract
        print(f"\n📝 CONTRACT")
        print(f"  Duration:       {ctx.get('contract_duration_months') or 'Open'} months")
        print(f"  Leave/Year:     {ctx.get('leave_days_per_year') or 'N/A'} days")

        # HR Contact
        print(f"\n📞 HR CONTACT (for Admin Verification)")
        print(f"  HR Name:        {ctx.get('hr_name') or 'N/A'}")
        print(f"  Designation:    {ctx.get('hr_designation') or 'N/A'}")
        print(f"  📧 Email:       {ctx.get('hr_email') or 'N/A'}")
        print(f"  📱 Phone:       {ctx.get('hr_phone') or 'N/A'}")
        if ctx.get('hr_whatsapp'):
            print(f"  💬 WhatsApp:    {ctx.get('hr_whatsapp')}")

        # Verification
        print(f"\n✅ VERIFICATION STATUS")
        print(f"  Status:         {ctx.get('verification_status') or 'PENDING'}")
        print(f"  Last Verified:  {ctx.get('verified_at') or 'Never'}")
        print(f"  Source:         {ctx.get('source') or 'Unknown'}")


# ============================================================
# ADMIN VERIFICATION WORKLIST
# ============================================================
def admin_worklist():
    """Show all jobs pending HR verification"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT company_name, job_title, country, hr_email, hr_phone,
               verification_status
        FROM job_full_context
        ORDER BY verification_status, company_name
    """)
    rows = cur.fetchall()
    conn.close()

    print("\n" + "=" * 90)
    print("📋 ADMIN VERIFICATION WORKLIST")
    print("=" * 90)
    print(f"\n{'Company':30} {'Job':25} {'Country':12} {'Status':10}")
    print("-" * 90)

    for co, job, country, email, phone, status in rows:
        status_str = status or "PENDING"
        print(f"{str(co)[:30]:30} {str(job)[:25]:25} {str(country)[:12]:12} {status_str:10}")

    print(f"\nTotal: {len(rows)} jobs to verify")


# ============================================================
# EXPORT FOR COPILOT
# ============================================================
def get_unified_data(company):
    """Return clean JSON for Copilot"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM job_full_context
        WHERE LOWER(company_name) LIKE ?
    """, (f"%{company.lower()}%",))
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 90)
    print("OIE MASTER CONTEXT — Unified Job View")
    print("=" * 90)

    create_master_view()

    # Show full context for 3 companies
    print("\n\n📖 SAMPLE FULL CONTEXT")
    print_full_context("Saudi Aramco")
    print_full_context("Charité Berlin")
    print_full_context("Toyota Motor")

    # Admin worklist
    admin_worklist()

    print("\nDone.")