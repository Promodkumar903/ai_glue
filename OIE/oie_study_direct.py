"""
Study OIE — Direct Apply Universities
Universities where students can apply without agent
"""
import sqlite3
from datetime import datetime

DB = "ai_glue.db"

# Universities with direct online application (no agent needed)
DIRECT_APPLY = [
    # Germany — Uni-Assist + direct
    ("Technical University of Munich", "Germany", "https://www.tum.de/en/studies/application"),
    ("RWTH Aachen", "Germany", "https://www.rwth-aachen.de/go/id/bdml/"),
    ("Heidelberg University", "Germany", "https://www.uni-heidelberg.de/en/study/application"),
    ("Humboldt University", "Germany", "https://www.hu-berlin.de/en/studies/apply"),
    ("Free University of Berlin", "Germany", "https://www.fu-berlin.de/en/studies/apply"),

    # UK — UCAS + Direct
    ("University of Oxford", "United Kingdom", "https://www.ox.ac.uk/admissions"),
    ("University of Cambridge", "United Kingdom", "https://www.cam.ac.uk/admissions"),
    ("Imperial College London", "United Kingdom", "https://www.imperial.ac.uk/study/apply"),
    ("University College London", "United Kingdom", "https://www.ucl.ac.uk/prospective-students"),
    ("London School of Economics", "United Kingdom", "https://www.lse.ac.uk/study-at-lse"),
    ("University of Edinburgh", "United Kingdom", "https://www.ed.ac.uk/studying/apply"),
    ("University of Manchester", "United Kingdom", "https://www.manchester.ac.uk/study/apply"),

    # USA — Common App + Direct
    ("Massachusetts Institute of Technology", "United States", "https://mitadmissions.org/apply"),
    ("Stanford University", "United States", "https://admission.stanford.edu/apply"),
    ("Harvard University", "United States", "https://college.harvard.edu/admissions/apply"),
    ("Carnegie Mellon University", "United States", "https://www.cmu.edu/admission/apply"),
    ("University of California, Berkeley", "United States", "https://admissions.berkeley.edu/apply"),
    ("Georgia Institute of Technology", "United States", "https://admission.gatech.edu/apply"),
    ("New York University", "United States", "https://www.nyu.edu/admissions/undergraduate-admissions/apply.html"),

    # Canada — Direct
    ("University of Toronto", "Canada", "https://future.utoronto.ca/apply"),
    ("University of British Columbia", "Canada", "https://you.ubc.ca/applying-ubc/"),
    ("McGill University", "Canada", "https://www.mcgill.ca/applying"),
    ("University of Waterloo", "Canada", "https://uwaterloo.ca/future-students/admissions"),

    # Australia
    ("University of Melbourne", "Australia", "https://study.unimelb.edu.au/how-to-apply"),
    ("University of Sydney", "Australia", "https://www.sydney.edu.au/study/how-to-apply.html"),
    ("Australian National University", "Australia", "https://www.anu.edu.au/study/apply"),

    # Japan
    ("University of Tokyo", "Japan", "https://www.u-tokyo.ac.jp/en/prospective-students/"),
    ("Kyoto University", "Japan", "https://www.kyoto-u.ac.jp/en/education-campus/admissions"),
    ("Tokyo Institute of Technology", "Japan", "https://www.titech.ac.jp/english/admissions"),

    # Europe
    ("ETH Zurich", "Switzerland", "https://ethz.ch/en/studies/registration-application.html"),
    ("EPFL", "Switzerland", "https://www.epfl.ch/education/admission/"),
    ("Delft University of Technology", "Netherlands", "https://www.tudelft.nl/en/education/admission-and-application"),
    ("University of Amsterdam", "Netherlands", "https://www.uva.nl/en/education/master-s/master-s-programmes/application-and-admission"),
    ("KTH Royal Institute of Technology", "Sweden", "https://www.kth.se/en/studies/master"),
    ("Trinity College Dublin", "Ireland", "https://www.tcd.ie/study/apply/"),
    ("University College Dublin", "Ireland", "https://www.ucd.ie/apply/"),
    ("Sorbonne University", "France", "https://www.sorbonne-universite.fr/en/formation/international"),
]


def apply_direct_data():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    matched = 0
    not_found = []

    for uni_name, country, apply_url in DIRECT_APPLY:
        cur.execute("""
            SELECT id FROM study_opportunities
            WHERE university_name LIKE ? AND country = ?
            LIMIT 1
        """, (f"%{uni_name}%", country))
        row = cur.fetchone()
        if not row:
            not_found.append(f"{uni_name} ({country})")
            continue

        cur.execute("""
            UPDATE study_opportunities
            SET direct_apply = 1, application_url = ?, updated_at = ?
            WHERE id = ?
        """, (apply_url, now, row[0]))
        matched += 1

    conn.commit()
    conn.close()
    print(f"Direct apply marked: {matched}")
    if not_found:
        print(f"\nNot found ({len(not_found)}):")
        for n in not_found[:10]:
            print(f"  {n}")


def report():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    print("\n" + "=" * 70)
    print("DIRECT APPLY UNIVERSITIES")
    print("=" * 70)
    cur.execute("""
        SELECT university_name, country, application_url
        FROM study_opportunities
        WHERE direct_apply = 1
        ORDER BY country LIMIT 15
    """)
    for n, c, u in cur.fetchall():
        print(f"  {str(n)[:40]:40} | {c:15}")
    cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE direct_apply=1")
    print(f"\nTotal direct apply: {cur.fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("STUDY OIE — DIRECT APPLY")
    print("=" * 70)
    apply_direct_data()
    report()