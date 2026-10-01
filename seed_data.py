"""
AI GLUE — Demo Data Seeder
Run: python seed_data.py
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import (
    db, User, UserRole, Country, University, City, Campus, Department,
    Course, IntakeSeat, Opportunity, Organization, Notification, Deal,
    VisaCase, Document, StudentLife, PartnerRegistry, Application, Offer
)

session = db.get_session()


def safe_add(obj):
    try:
        session.add(obj)
        session.flush()
        return obj
    except Exception as e:
        session.rollback()
        print(f"  Skip: {e}")
        return None


print("Seeding demo data...")
print("=" * 50)

# ---------- 1. Countries ----------
countries_data = [
    ("Germany", "DE"),
    ("Canada", "CA"),
    ("United Kingdom", "GB"),
    ("Australia", "AU"),
    ("United States", "US"),
    ("Ireland", "IE"),
]
countries = []
for name, iso in countries_data:
    existing = session.query(Country).filter(Country.iso_code == iso).first()
    if existing:
        countries.append(existing)
        continue
    c = safe_add(Country(name=name, iso_code=iso, visa_difficulty=3.0, cost_of_living_index=70.0))
    if c:
        countries.append(c)
session.commit()
print(f"OK Countries: {len(countries)}")

# ---------- 2. Universities ----------
if len(countries) >= 6:
    univ_data = [
        ("Technical University of Munich", countries[0].id, "https://tum.de"),
        ("University of Toronto", countries[1].id, "https://utoronto.ca"),
        ("University of Oxford", countries[2].id, "https://ox.ac.uk"),
        ("University of Melbourne", countries[3].id, "https://unimelb.edu.au"),
        ("MIT", countries[4].id, "https://mit.edu"),
        ("Trinity College Dublin", countries[5].id, "https://tcd.ie"),
    ]
    universities = []
    for name, cid, web in univ_data:
        existing = session.query(University).filter(University.name == name).first()
        if existing:
            universities.append(existing)
            continue
        u = safe_add(University(country_id=cid, name=name, website=web, ranking_global=50))
        if u:
            universities.append(u)
    session.commit()
    print(f"OK Universities: {len(universities)}")
else:
    universities = []
    print("SKIP Universities (countries missing)")

# ---------- 3. Cities ----------
if len(countries) >= 6:
    cities_data = [
        ("Munich", countries[0].id, "Bavaria"),
        ("Toronto", countries[1].id, "Ontario"),
        ("Oxford", countries[2].id, "England"),
        ("Melbourne", countries[3].id, "Victoria"),
        ("Boston", countries[4].id, "Massachusetts"),
        ("Dublin", countries[5].id, "Leinster"),
    ]
    cities = []
    for name, cid, state in cities_data:
        existing = session.query(City).filter(City.name == name).first()
        if existing:
            cities.append(existing)
            continue
        c = safe_add(City(name=name, country_id=cid, state=state))
        if c:
            cities.append(c)
    session.commit()
    print(f"OK Cities: {len(cities)}")
else:
    cities = []
    print("SKIP Cities (countries missing)")

# ---------- 4. Organizations ----------
orgs_data = [
    ("Google Inc.", "EMPLOYER"),
    ("Siemens AG", "EMPLOYER"),
    ("SAP SE", "EMPLOYER"),
    ("Infosys", "EMPLOYER"),
    ("Tata Consultancy", "EMPLOYER"),
]
orgs = []
for name, otype in orgs_data:
    existing = session.query(Organization).filter(Organization.name == name).first()
    if existing:
        orgs.append(existing)
        continue
    o = safe_add(Organization(name=name, type=otype, verification_status='VERIFIED'))
    if o:
        orgs.append(o)
session.commit()
print(f"OK Organizations: {len(orgs)}")

# ---------- 5. Users ----------
users_data = [
    ("admin@aiglue.com", "Admin User", "ADMIN"),
    ("student@aiglue.com", "Rahul Student", "STUDENT"),
    ("seeker@aiglue.com", "Priya Seeker", "JOB_SEEKER"),
    ("agent@aiglue.com", "Vikram Agent", "AGENT"),
    ("broker@aiglue.com", "Deepak Broker", "BROKER"),
    ("employer@aiglue.com", "Anita Employer", "EMPLOYER"),
]
users = []
for email, name, role in users_data:
    existing = session.query(User).filter(User.email == email).first()
    if existing:
        users.append(existing)
        continue
    u = safe_add(User(
        email=email,
        password_hash="demo_hash",
        full_name=name,
        status='ACTIVE'
    ))
    if u:
        users.append(u)
        safe_add(UserRole(user_id=u.id, role_code=role))
session.commit()
print(f"OK Users: {len(users)}")

# ---------- 6. Campus + Department + Courses ----------
courses = []
if universities and cities:
    campus = session.query(Campus).filter(Campus.name == "TUM Main Campus").first()
    if not campus:
        campus = safe_add(Campus(
            university_id=universities[0].id,
            city_id=cities[0].id,
            name="TUM Main Campus"
        ))
        session.commit()
    if campus:
        dept = session.query(Department).filter(Department.name == "Computer Science").first()
        if not dept:
            dept = safe_add(Department(campus_id=campus.id, name="Computer Science"))
            session.commit()
        if dept:
            courses_data = [
                ("MSc Computer Science", "Master", 24, 15000),
                ("BSc Data Science", "Bachelor", 36, 12000),
                ("MSc AI & ML", "Master", 24, 18000),
            ]
            for name, level, dur, fee in courses_data:
                existing = session.query(Course).filter(Course.name == name).first()
                if existing:
                    courses.append(existing)
                    continue
                c = safe_add(Course(
                    department_id=dept.id,
                    name=name,
                    level=level,
                    duration_months=dur,
                    tuition_fee=fee,
                    currency='EUR'
                ))
                if c:
                    courses.append(c)
                    safe_add(IntakeSeat(
                        course_id=c.id,
                        academic_year="2026/2027",
                        total_seats=50,
                        filled_seats=35,
                        waiting_seats=5
                    ))
            session.commit()
print(f"OK Courses: {len(courses)}")

# ---------- 7. Opportunities (Jobs) ----------
opps = []
if orgs:
    jobs_data = [
        ("Senior Software Engineer", "VACANCY", "Germany", 80000),
        ("Data Scientist", "VACANCY", "Canada", 90000),
        ("DevOps Engineer", "VACANCY", "United Kingdom", 75000),
        ("Product Manager", "VACANCY", "Australia", 95000),
        ("Research Fellowship", "SCHOLARSHIP", "Germany", 30000),
        ("MSc Computer Science", "PROGRAMME", "Germany", 15000),
        ("Cloud Architect", "VACANCY", "United States", 120000),
        ("Backend Developer", "VACANCY", "Ireland", 70000),
    ]
    for i, (title, jtype, country, salary) in enumerate(jobs_data):
        existing = session.query(Opportunity).filter(Opportunity.title == title).first()
        if existing:
            opps.append(existing)
            continue
        o = safe_add(Opportunity(
            organization_id=orgs[i % len(orgs)].id,
            type=jtype,
            title=title,
            description=f"Exciting {jtype} opportunity in {country}. Join our team!",
            status='OPEN',
            capacity=10,
            filled_count=2,
            requirements={"country": country, "salary": salary}
        ))
        if o:
            opps.append(o)
    session.commit()
print(f"OK Opportunities: {len(opps)}")

# ---------- 8. Notifications ----------
notif_count = 0
for i, u in enumerate(users[:4]):
    n = safe_add(Notification(
        user_id=u.id,
        title=f"Welcome {u.full_name}",
        message="Your AI Glue account is ready. Explore your dashboard!",
        is_read=False
    ))
    if n:
        notif_count += 1
session.commit()
print(f"OK Notifications: {notif_count}")

# ---------- 9. Deals ----------
deal_count = 0
if len(users) >= 5 and orgs and opps:
    for i in range(3):
        try:
            d = Deal(
                agent_id=users[3].id,
                broker_id=users[4].id,
                company_id=orgs[i % len(orgs)].id,
                candidate_id=users[2].id,
                opportunity_id=opps[i % len(opps)].id,
                status='PENDING',
                deal_fee=5000,
                platform_cut=500,
                agent_commission=3000,
                broker_commission=1500
            )
            d = safe_add(d)
            if d:
                deal_count += 1
        except Exception as e:
            session.rollback()
    session.commit()
print(f"OK Deals: {deal_count}")

# ---------- 10. Visa Cases ----------
visa_count = 0
if len(users) >= 4:
    statuses = ["PENDING", "APPROVED", "IN_PROGRESS"]
    visa_countries = ["Germany", "Canada", "United Kingdom"]
    for i, u in enumerate(users[1:4]):
        v = safe_add(VisaCase(
            candidate_id=u.id,
            country=visa_countries[i],
            visa_type="WORK",
            status=statuses[i]
        ))
        if v:
            visa_count += 1
    session.commit()
print(f"OK Visa Cases: {visa_count}")

# ---------- 11. Vendors / Partners ----------
vendors_data = [
    ("Student Hotel Munich", "hotel", "Munich"),
    ("Oxford Bookstore", "book", "Oxford"),
    ("IKEA Toronto", "furniture", "Toronto"),
    ("Campus Library", "library", "Melbourne"),
    ("Fresh Mart Grocery", "grocery", "Boston"),
    ("City Cabs", "transport", "Dublin"),
]
vendor_count = 0
for name, cat, loc in vendors_data:
    existing = session.query(PartnerRegistry).filter(PartnerRegistry.name == name).first()
    if existing:
        vendor_count += 1
        continue
    v = safe_add(PartnerRegistry(
        name=name,
        category=cat,
        location=loc,
        status='ACTIVE',
        trust_score=85.0
    ))
    if v:
        vendor_count += 1
session.commit()
print(f"OK Vendors: {vendor_count}")

# ---------- DONE ----------
session.close()
print("=" * 50)
print("SEED COMPLETE!")
print("=" * 50)
print("Login credentials (demo — any password):")
print("  admin@aiglue.com       (ADMIN)")
print("  student@aiglue.com     (STUDENT)")
print("  seeker@aiglue.com      (JOB_SEEKER)")
print("  agent@aiglue.com       (AGENT)")
print("  broker@aiglue.com      (BROKER)")
print("  employer@aiglue.com    (EMPLOYER)")
print("=" * 50)