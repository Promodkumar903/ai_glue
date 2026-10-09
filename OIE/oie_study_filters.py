"""
Study OIE — Filter Query Engine
20+ filters, real-time query for admin/students
"""
import json
import sqlite3

DB = "ai_glue.db"


def query_study(filters):
    """
    Universal query engine for study_opportunities
    filters: dict with any of:
      country, countries (list),
      degree_level, field_of_study,
      max_tuition, max_total_cost,
      free_education, scholarship_available,
      max_hostel_cost, hostel_available,
      min_post_study_work, pr_possible,
      direct_apply, min_demand_score,
      part_time_allowed, language,
      min_scholarship, limit, order_by
    """
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    sql = ["SELECT id, university_name, country, course_name, degree_level,",
           "field_of_study, tuition_fee, hostel_cost_monthly_usd,",
           "scholarship_amount_usd, post_study_work_years, pr_possible,",
           "direct_apply, demand_score, language, application_url",
           "FROM study_opportunities WHERE status='DISCOVERED'"]
    params = []

    # Country filter
    if filters.get("countries"):
        countries = filters["countries"]
        if isinstance(countries, list):
            placeholders = ",".join(["?"] * len(countries))
            sql.append(f"AND country IN ({placeholders})")
            params.extend(countries)
    elif filters.get("country"):
        sql.append("AND country = ?")
        params.append(filters["country"])

    # Degree level
    if filters.get("degree_level"):
        sql.append("AND LOWER(degree_level) = ?")
        params.append(filters["degree_level"].lower())

    # Field of study
    if filters.get("field_of_study"):
        sql.append("AND LOWER(field_of_study) LIKE ?")
        params.append(f"%{filters['field_of_study'].lower()}%")

    # Max tuition
    if filters.get("max_tuition"):
        sql.append("AND (tuition_fee <= ? OR tuition_fee = 0)")
        params.append(filters["max_tuition"])

    # Free education
    if filters.get("free_education"):
        sql.append("AND free_education = 1")

    # Scholarship
    if filters.get("scholarship_available"):
        sql.append("AND scholarship_available = 1")

    if filters.get("min_scholarship"):
        sql.append("AND scholarship_amount_usd >= ?")
        params.append(filters["min_scholarship"])

    # Hostel
    if filters.get("hostel_available"):
        sql.append("AND hostel_available = 1")

    if filters.get("max_hostel_cost"):
        sql.append("AND hostel_cost_monthly_usd <= ?")
        params.append(filters["max_hostel_cost"])

    # Total cost (tuition + hostel per year)
    if filters.get("max_total_cost"):
        sql.append("""
            AND (COALESCE(tuition_fee, 0) + COALESCE(hostel_cost_monthly_usd, 0) * 12) <= ?
        """)
        params.append(filters["max_total_cost"])

    # Post study work
    if filters.get("min_post_study_work"):
        sql.append("AND post_study_work_years >= ?")
        params.append(filters["min_post_study_work"])

    # PR
    if filters.get("pr_possible"):
        sql.append("AND pr_possible = 1")

    # Direct apply
    if filters.get("direct_apply"):
        sql.append("AND direct_apply = 1")

    # Demand
    if filters.get("min_demand_score"):
        sql.append("AND demand_score >= ?")
        params.append(filters["min_demand_score"])

    # Part time
    if filters.get("part_time_allowed"):
        sql.append("AND part_time_allowed = 1")

    # Language
    if filters.get("language"):
        sql.append("AND LOWER(language) LIKE ?")
        params.append(f"%{filters['language'].lower()}%")

    # Order by
    order_by = filters.get("order_by", "demand_score DESC")
    valid_orders = [
        "demand_score DESC", "tuition_fee ASC",
        "hostel_cost_monthly_usd ASC", "post_study_work_years DESC",
        "scholarship_amount_usd DESC", "university_name ASC",
    ]
    if order_by not in valid_orders:
        order_by = "demand_score DESC"
    sql.append(f"ORDER BY {order_by}")

    # Limit
    limit = filters.get("limit", 50)
    sql.append("LIMIT ?")
    params.append(limit)

    final_sql = " ".join(sql)
    cur.execute(final_sql, params)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    conn.close()

    results = []
    for row in rows:
        results.append(dict(zip(cols, row)))
    return results


def print_results(results, title="RESULTS"):
    print(f"\n{'='*100}")
    print(f"{title} — {len(results)} found")
    print(f"{'='*100}")

    if not results:
        print("No matches.")
        return

    for i, r in enumerate(results[:20], 1):
        print(f"\n[{i}] {r['university_name'][:60]}")
        print(f"    Country: {r['country']} | {r['degree_level'] or 'N/A'}")
        print(f"    Field: {r['field_of_study'] or 'N/A'}")
        print(f"    Tuition: ${r['tuition_fee'] or 0:,.0f} | "
              f"Hostel: ${r['hostel_cost_monthly_usd'] or 0:,.0f}/mo")
        print(f"    Scholarship: ${r['scholarship_amount_usd'] or 0:,.0f}")
        print(f"    Post-study work: {r['post_study_work_years'] or 0} months | "
              f"PR: {'Yes' if r['pr_possible'] else 'No'}")
        print(f"    Demand score: {r['demand_score'] or 0}")
        if r['application_url']:
            print(f"    Apply: {r['application_url'][:70]}")


# ============================================================
# DEMO QUERIES
# ============================================================
if __name__ == "__main__":
    print("=" * 100)
    print("STUDY OIE — FILTER QUERY ENGINE DEMO")
    print("=" * 100)

    # Query 1: Free education in Germany
    print("\n\n### Query 1: Free education in Germany")
    r = query_study({
        "country": "Germany",
        "free_education": 1,
        "limit": 10,
    })
    print_results(r, "Free Education in Germany")

    # Query 2: Scholarship + IT courses
    print("\n\n### Query 2: IT courses with scholarship")
    r = query_study({
        "field_of_study": "computer",
        "scholarship_available": 1,
        "limit": 10,
    })
    print_results(r, "IT with Scholarship")

    # Query 3: Cheap total cost < $10K
    print("\n\n### Query 3: Total yearly cost under $10K")
    r = query_study({
        "max_total_cost": 10000,
        "limit": 10,
    })
    print_results(r, "Budget Friendly (<$10K/year)")

    # Query 4: PR possible + Post-study work 24+ months
    print("\n\n### Query 4: PR-friendly countries with 2+ years work")
    r = query_study({
        "pr_possible": 1,
        "min_post_study_work": 24,
        "limit": 10,
        "order_by": "post_study_work_years DESC",
    })
    print_results(r, "PR + Long Post-Study Work")

    # Query 5: High demand AI courses
    print("\n\n### Query 5: High-demand AI courses (score 90+)")
    r = query_study({
        "field_of_study": "AI",
        "min_demand_score": 85,
        "limit": 10,
        "order_by": "demand_score DESC",
    })
    print_results(r, "High-Demand AI Courses")

    # Query 6: Direct apply with scholarship
    print("\n\n### Query 6: Direct Apply + Scholarship")
    r = query_study({
        "direct_apply": 1,
        "scholarship_available": 1,
        "limit": 10,
    })
    print_results(r, "Direct Apply + Scholarship")

    # Summary stats
    print("\n\n" + "=" * 100)
    print("DATABASE SUMMARY")
    print("=" * 100)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM study_opportunities")
    print(f"Total universities: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE free_education=1")
    print(f"Free education: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE scholarship_available=1")
    print(f"With scholarship: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE direct_apply=1")
    print(f"Direct apply: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE pr_possible=1")
    print(f"PR possible: {cur.fetchone()[0]}")
    conn.close()