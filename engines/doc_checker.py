"""
Document Checker Engine
Country-wise required documents + missing detection
"""
from datetime import datetime


# ============================================================
# COUNTRY-WISE DOCUMENT REQUIREMENTS
# ============================================================
COUNTRY_REQUIREMENTS = {
    "UK": {
        "name": "United Kingdom",
        "docs": [
            "Passport",
            "Marksheet 10th",
            "Marksheet 12th",
            "Degree",
            "IELTS/TOEFL",
            "SOP",
            "LOR",
            "Bank Statement",
            "Offer Letter",
            "Visa",
        ],
        "mandatory": ["Passport", "IELTS/TOEFL", "SOP", "Bank Statement"],
    },
    "Canada": {
        "name": "Canada",
        "docs": [
            "Passport",
            "Marksheet 10th",
            "Marksheet 12th",
            "Degree",
            "IELTS/TOEFL",
            "SOP",
            "LOR",
            "Bank Statement",
            "Offer Letter",
            "Visa",
        ],
        "mandatory": ["Passport", "IELTS/TOEFL", "SOP", "Bank Statement"],
    },
    "Australia": {
        "name": "Australia",
        "docs": [
            "Passport",
            "Marksheet 10th",
            "Marksheet 12th",
            "Degree",
            "IELTS/TOEFL",
            "SOP",
            "Bank Statement",
            "Offer Letter",
            "Visa",
        ],
        "mandatory": ["Passport", "IELTS/TOEFL", "Bank Statement"],
    },
    "USA": {
        "name": "United States",
        "docs": [
            "Passport",
            "Marksheet 10th",
            "Marksheet 12th",
            "Degree",
            "IELTS/TOEFL",
            "SOP",
            "LOR",
            "Bank Statement",
            "Offer Letter",
            "Visa",
        ],
        "mandatory": ["Passport", "IELTS/TOEFL", "SOP", "LOR", "Bank Statement"],
    },
    "Germany": {
        "name": "Germany",
        "docs": [
            "Passport",
            "Marksheet 10th",
            "Marksheet 12th",
            "Degree",
            "IELTS/TOEFL",
            "SOP",
            "Bank Statement",
            "Offer Letter",
            "Visa",
        ],
        "mandatory": ["Passport", "IELTS/TOEFL", "Bank Statement"],
    },
    "Ireland": {
        "name": "Ireland",
        "docs": [
            "Passport",
            "Marksheet 10th",
            "Marksheet 12th",
            "Degree",
            "IELTS/TOEFL",
            "SOP",
            "LOR",
            "Bank Statement",
            "Offer Letter",
            "Visa",
        ],
        "mandatory": ["Passport", "IELTS/TOEFL", "Bank Statement"],
    },
    "New Zealand": {
        "name": "New Zealand",
        "docs": [
            "Passport",
            "Marksheet 10th",
            "Marksheet 12th",
            "Degree",
            "IELTS/TOEFL",
            "SOP",
            "Bank Statement",
            "Offer Letter",
            "Visa",
        ],
        "mandatory": ["Passport", "IELTS/TOEFL", "Bank Statement"],
    },
    "Singapore": {
        "name": "Singapore",
        "docs": [
            "Passport",
            "Marksheet 10th",
            "Marksheet 12th",
            "Degree",
            "IELTS/TOEFL",
            "SOP",
            "Bank Statement",
            "Offer Letter",
        ],
        "mandatory": ["Passport", "IELTS/TOEFL"],
    },
    "Dubai": {
        "name": "UAE / Dubai",
        "docs": [
            "Passport",
            "Marksheet 10th",
            "Marksheet 12th",
            "Degree",
            "IELTS/TOEFL",
            "Bank Statement",
            "Offer Letter",
            "Visa",
        ],
        "mandatory": ["Passport", "Bank Statement"],
    },
    "France": {
        "name": "France",
        "docs": [
            "Passport",
            "Marksheet 10th",
            "Marksheet 12th",
            "Degree",
            "IELTS/TOEFL",
            "SOP",
            "Bank Statement",
            "Offer Letter",
            "Visa",
        ],
        "mandatory": ["Passport", "IELTS/TOEFL", "Bank Statement"],
    },
}


class DocumentCheckerEngine:

    @staticmethod
    def get_country_list():
        """All supported countries."""
        return [
            {"code": code, "name": info["name"]}
            for code, info in COUNTRY_REQUIREMENTS.items()
        ]

    @staticmethod
    def get_requirements(country_code):
        """Get required docs for a country."""
        if country_code not in COUNTRY_REQUIREMENTS:
            return {"error": f"Country '{country_code}' not supported"}
        return COUNTRY_REQUIREMENTS[country_code]

    @staticmethod
    def check_lead(lead_country, uploaded_docs):
        """
        Check a lead's uploaded docs against country requirements.
        uploaded_docs: list of dicts with keys: document_type, status
        """
        if not lead_country or lead_country not in COUNTRY_REQUIREMENTS:
            return {
                "status": "error",
                "message": f"Country '{lead_country}' not supported",
                "supported": list(COUNTRY_REQUIREMENTS.keys()),
            }

        requirements = COUNTRY_REQUIREMENTS[lead_country]
        required_list = requirements["docs"]
        mandatory_list = requirements["mandatory"]

        # Build set of uploaded doc types (case-insensitive)
        uploaded_types = {}
        for d in (uploaded_docs or []):
            dt = (d.get("document_type") or "").strip()
            st = (d.get("status") or "MISSING").upper()
            if dt:
                if dt in uploaded_types:
                    # Keep the "best" status
                    if st == "VERIFIED":
                        uploaded_types[dt] = "VERIFIED"
                    elif st == "UPLOADED" and uploaded_types[dt] == "MISSING":
                        uploaded_types[dt] = "UPLOADED"
                else:
                    uploaded_types[dt] = st

        checklist = []
        missing = []
        missing_mandatory = []
        uploaded_count = 0
        verified_count = 0

        for req in required_list:
            status = uploaded_types.get(req, "MISSING")
            is_mandatory = req in mandatory_list

            if status == "MISSING":
                missing.append(req)
                if is_mandatory:
                    missing_mandatory.append(req)
            elif status == "UPLOADED":
                uploaded_count += 1
            elif status == "VERIFIED":
                uploaded_count += 1
                verified_count += 1

            checklist.append({
                "document_type": req,
                "status": status,
                "mandatory": is_mandatory,
            })

        total = len(required_list)
        completion_pct = int((verified_count / total) * 100) if total > 0 else 0

        # Overall verdict
        if missing_mandatory:
            verdict = "INCOMPLETE"
            message = f"{len(missing_mandatory)} mandatory document(s) missing"
        elif missing:
            verdict = "PARTIAL"
            message = f"{len(missing)} optional document(s) pending"
        else:
            verdict = "COMPLETE"
            message = "All documents received"

        return {
            "status": "ok",
            "country": lead_country,
            "country_name": requirements["name"],
            "checklist": checklist,
            "total_required": total,
            "uploaded_count": uploaded_count,
            "verified_count": verified_count,
            "missing": missing,
            "missing_mandatory": missing_mandatory,
            "completion_pct": completion_pct,
            "verdict": verdict,
            "message": message,
        }


doc_checker = DocumentCheckerEngine()