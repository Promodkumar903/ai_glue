"""
Visa Tracking Tier System
- TIER 1: Auto API (USA USCIS, UAE ICP)
- TIER 2: Third-party API (UK, AUS, NZ — placeholder)
- TIER 3: Manual + SMS fallback (all countries)
"""
import os
from datetime import datetime


# ============================================================
# EMBASSY DATA — All countries
# ============================================================
EMBASSY_DATA = {
    "USA": {
        "name": "US Embassy / Consulate",
        "url": "https://ceac.state.gov/CEACStatTracker/Status.aspx",
        "phone": "+1-603-334-0700",
        "visa_portal": "https://www.ustraveldocs.com",
        "processing_time": "2-8 weeks",
        "tier": 1,
    },
    "UAE": {
        "name": "UAE ICP / GDRFA",
        "url": "https://smartservices.icp.gov.ae",
        "phone": "+971-4-313-9999",
        "visa_portal": "https://icp.gov.ae",
        "processing_time": "3-5 days",
        "tier": 1,
    },
    "UK": {
        "name": "UK Visas & Immigration (UKVI)",
        "url": "https://www.gov.uk/check-uk-visa",
        "phone": "+44-300-790-6268",
        "visa_portal": "https://visas-immigration.service.gov.uk",
        "processing_time": "3 weeks",
        "tier": 2,
    },
    "Canada": {
        "name": "Immigration, Refugees and Citizenship Canada (IRCC)",
        "url": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
        "phone": "+1-888-242-2100",
        "visa_portal": "https://www.canada.ca/en/immigration-refugees-citizenship/services/application.html",
        "processing_time": "4-12 weeks",
        "tier": 2,
    },
    "Australia": {
        "name": "Australian Department of Home Affairs",
        "url": "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing",
        "phone": "+61-131-881",
        "visa_portal": "https://online.immi.gov.au",
        "processing_time": "4-8 weeks",
        "tier": 2,
    },
    "Germany": {
        "name": "German Federal Foreign Office",
        "url": "https://www.auswaertiges-amt.de/en/visa-service",
        "phone": "+49-30-1817-0",
        "visa_portal": "https://videx.diplo.de",
        "processing_time": "2-6 weeks",
        "tier": 3,
    },
    "France": {
        "name": "France-Visas",
        "url": "https://france-visas.gouv.fr",
        "phone": "+33-1-53-59-55-55",
        "visa_portal": "https://france-visas.gouv.fr/en/web/france-visas",
        "processing_time": "2-4 weeks",
        "tier": 3,
    },
    "Ireland": {
        "name": "Irish Naturalisation and Immigration Service",
        "url": "https://www.irishimmigration.ie",
        "phone": "+353-1-616-7700",
        "visa_portal": "https://www.irishimmigration.ie/visa-services/",
        "processing_time": "6-8 weeks",
        "tier": 3,
    },
    "New Zealand": {
        "name": "Immigration New Zealand",
        "url": "https://www.immigration.govt.nz",
        "phone": "+64-9-914-4100",
        "visa_portal": "https://www.immigration.govt.nz/apply-for-visa",
        "processing_time": "4-8 weeks",
        "tier": 2,
    },
    "Singapore": {
        "name": "Immigration & Checkpoints Authority (ICA)",
        "url": "https://www.ica.gov.sg",
        "phone": "+65-6391-6100",
        "visa_portal": "https://eservices.ica.gov.sg",
        "processing_time": "1-2 weeks",
        "tier": 3,
    },
    "Dubai": {
        "name": "GDRFA Dubai",
        "url": "https://www.gdrfad.gov.ae",
        "phone": "+971-4-313-9999",
        "visa_portal": "https://www.gdrfad.gov.ae/en",
        "processing_time": "3-5 days",
        "tier": 1,
    },
    "Netherlands": {
        "name": "Immigration and Naturalisation Service (IND)",
        "url": "https://ind.nl/en",
        "phone": "+31-88-04-30430",
        "visa_portal": "https://ind.nl/en/apply-for-visa",
        "processing_time": "2-4 weeks",
        "tier": 3,
    },
    "Sweden": {
        "name": "Swedish Migration Agency",
        "url": "https://www.migrationsverket.se",
        "phone": "+46-771-235-235",
        "visa_portal": "https://www.migrationsverket.se/English",
        "processing_time": "2-4 weeks",
        "tier": 3,
    },
    "Norway": {
        "name": "Norwegian Directorate of Immigration (UDI)",
        "url": "https://www.udi.no/en",
        "phone": "+47-22-00-00-00",
        "visa_portal": "https://www.udi.no/en/want-to-apply",
        "processing_time": "2-6 weeks",
        "tier": 3,
    },
    "Italy": {
        "name": "Italian Ministry of Foreign Affairs",
        "url": "https://vistoperitalia.esteri.it",
        "phone": "+39-06-36911",
        "visa_portal": "https://vistoperitalia.esteri.it/home/en",
        "processing_time": "3-6 weeks",
        "tier": 3,
    },
    "Spain": {
        "name": "Spanish Ministry of Foreign Affairs",
        "url": "https://www.exteriores.gob.es",
        "phone": "+34-91-379-9700",
        "visa_portal": "https://www.exteriores.gob.es/en",
        "processing_time": "2-4 weeks",
        "tier": 3,
    },
    "Japan": {
        "name": "Japanese Ministry of Foreign Affairs",
        "url": "https://www.mofa.go.jp/j_info/visit/visa",
        "phone": "+81-3-3580-3311",
        "visa_portal": "https://www.mofa.go.jp",
        "processing_time": "1-2 weeks",
        "tier": 3,
    },
    "South Korea": {
        "name": "Korea Immigration Service",
        "url": "https://www.immigration.go.kr",
        "phone": "+82-2-6908-1345",
        "visa_portal": "https://www.visa.go.kr",
        "processing_time": "2-3 weeks",
        "tier": 3,
    },
    "Malaysia": {
        "name": "Malaysian Immigration Department",
        "url": "https://www.imi.gov.my",
        "phone": "+60-3-8000-8000",
        "visa_portal": "https://malaysiavisa.imi.gov.my",
        "processing_time": "1-2 weeks",
        "tier": 3,
    },
    "Thailand": {
        "name": "Thai Immigration Bureau",
        "url": "https://www.immigration.go.th",
        "phone": "+66-2-141-9889",
        "visa_portal": "https://www.thaievisa.go.th",
        "processing_time": "1-2 weeks",
        "tier": 3,
    },
    "Finland": {
        "name": "Finnish Immigration Service (Migri)",
        "url": "https://migri.fi/en/home",
        "phone": "+358-295-430-300",
        "visa_portal": "https://enterfinland.fi",
        "processing_time": "2-4 weeks",
        "tier": 3,
    },
    "Denmark": {
        "name": "Danish Immigration Service",
        "url": "https://www.nyidanmark.dk",
        "phone": "+45-35-30-85-75",
        "visa_portal": "https://www.nyidanmark.dk/en-GB",
        "processing_time": "2-4 weeks",
        "tier": 3,
    },
    "Switzerland": {
        "name": "State Secretariat for Migration (SEM)",
        "url": "https://www.sem.admin.ch",
        "phone": "+41-58-465-11-11",
        "visa_portal": "https://www.sem.admin.ch/sem/en/home.html",
        "processing_time": "2-6 weeks",
        "tier": 3,
    },
    "Austria": {
        "name": "Austrian Federal Ministry",
        "url": "https://www.bmeia.gv.at",
        "phone": "+43-1-901-150",
        "visa_portal": "https://www.bmeia.gv.at/en",
        "processing_time": "2-4 weeks",
        "tier": 3,
    },
}


# ============================================================
# SMS TEMPLATES — status-wise
# ============================================================
SMS_TEMPLATES = {
    "NOT_STARTED": "Aapka {country} visa process abhi start nahi hua. Documents collect karein aur apne agent {agent_name} se contact karein. Embassy: {embassy_url}",

    "DOCS_PENDING": "Aapke {country} visa ke documents pending hain. Checklist: {embassy_url}. Apne agent {agent_name} se help lein.",

    "APPLIED": "Aapka {country} visa application submit ho gaya. Status track karne ke liye: {embassy_url}. Processing time: {processing_time}.", 

    "UNDER_REVIEW": "Aapka {country} visa under review hai. Status check karein: {embassy_url}. Kuch urgent ho to embassy contact: {embassy_phone}",

    "APPROVED": "🎉 Mubarak! Aapka {country} visa approve ho gaya. Embassy se passport collect karein: {embassy_url}. Apne agent {agent_name} se next steps puchhein.",

    "REJECTED": "Aapka {country} visa reject hua. Reason: {reason}. Appeal ke liye embassy contact karein: {embassy_phone}. Apne agent {agent_name} se baat karein.",

    "EXPIRED": "⚠️ Aapka {country} visa expire ho gaya. Renewal ke liye embassy contact karein: {embassy_url}",
}


# ============================================================
# TIER 1 — FREE OFFICIAL API PLACEHOLDERS
# ============================================================
def check_usa_visa_status(case_number: str):
    """
    USA USCIS Case Status — Official API available.
    TODO: Register at developer.uscis.gov for API access.
    Currently returns 'not_configured'.
    """
    # Endpoint: https://api.uscis.gov/case-status/v1/cases/{caseNumber}
    api_key = os.getenv('USCIS_API_KEY', '')
    if not api_key:
        return {
            "status": "not_configured",
            "message": "USCIS API key not set. Register at developer.uscis.gov",
            "tier": 1,
            "country": "USA",
        }
    # Actual API call would go here
    return {
        "status": "pending",
        "message": "API key present — implementation pending",
        "tier": 1,
        "country": "USA",
    }


def check_uae_visa_status(ref_number: str):
    """
    UAE ICP File Validity — Public API.
    TODO: Endpoint integration.
    """
    return {
        "status": "not_configured",
        "message": "UAE ICP API — manual verification required",
        "tier": 1,
        "country": "UAE",
    }


# ============================================================
# TIER 2 — THIRD-PARTY PLACEHOLDERS
# ============================================================
def check_uk_visa_status(share_code: str):
    """UK eVisa share code via Trinsic/Vouchsafe (paid)."""
    return {
        "status": "not_configured",
        "message": "Contact Trinsic/Vouchsafe for UK visa verification",
        "tier": 2,
        "country": "UK",
        "provider": "Trinsic",
    }


def check_australia_visa_status(vevo_ref: str):
    """Australia VEVO via vSure (paid)."""
    return {
        "status": "not_configured",
        "message": "Contact vSure for Australia VEVO check",
        "tier": 2,
        "country": "Australia",
        "provider": "vSure",
    }


# ============================================================
# MAIN DISPATCHER
# ============================================================
class VisaTierEngine:

    @staticmethod
    def get_embassy_info(country):
        """Embassy data for any country."""
        key = country.upper().strip()
        if key not in EMBASSY_DATA:
            return {
                "name": f"{country} Embassy",
                "url": "https://www.google.com/search?q=" + country.replace(' ', '+') + "+embassy+visa",
                "phone": "Contact local embassy",
                "processing_time": "Varies",
                "tier": 3,
                "not_found": True,
            }
        return EMBASSY_DATA[key]

    @staticmethod
    def get_tier(country):
        """Tier for a country."""
        key = country.upper().strip()
        info = EMBASSY_DATA.get(key, {})
        return info.get("tier", 3)

    @staticmethod
    def generate_sms(country, status, agent_name="your agent", reason=""):
        """Personalized SMS message."""
        info = VisaTierEngine.get_embassy_info(country)
        template = SMS_TEMPLATES.get(status, SMS_TEMPLATES["APPLIED"])
        return template.format(
            country=country,
            status=status,
            agent_name=agent_name,
            embassy_url=info.get("url", "—"),
            embassy_phone=info.get("phone", "—"),
            processing_time=info.get("processing_time", "—"),
            reason=reason or "Not specified",
        )

    @staticmethod
    def auto_check(country, ref_number):
        """Dispatch to tier-specific checker."""
        tier = VisaTierEngine.get_tier(country)
        country_upper = country.upper().strip()

        if tier == 1:
            if country_upper == "USA":
                return check_usa_visa_status(ref_number)
            elif country_upper in ("UAE", "DUBAI"):
                return check_uae_visa_status(ref_number)
        elif tier == 2:
            if country_upper == "UK":
                return check_uk_visa_status(ref_number)
            elif country_upper == "AUSTRALIA":
                return check_australia_visa_status(ref_number)

        return {
            "status": "manual_required",
            "message": "Is country ke liye API available nahi. Manual verification ya SMS.",
            "tier": tier,
            "country": country,
        }


visa_tier = VisaTierEngine()