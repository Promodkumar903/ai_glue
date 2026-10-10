"""
OIE Companies Master List
Middle East + Europe + Russia/CIS
Each entry: {name, country, region, careers_url, ats, slug}
ats: greenhouse | lever | workable | smartrecruiters | custom
slug: ATS का company identifier (जहाँ लागू हो)
"""

COMPANIES = [
    # ═══════════════════════════════════════════
    # MIDDLE EAST — Saudi Arabia
    # ═══════════════════════════════════════════
    {"name": "Saudi Aramco", "country": "Saudi Arabia", "region": "Middle East",
     "careers_url": "https://careers.aramco.com", "ats": "custom", "slug": ""},
    {"name": "SABIC", "country": "Saudi Arabia", "region": "Middle East",
     "careers_url": "https://www.sabic.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "Ma'aden", "country": "Saudi Arabia", "region": "Middle East",
     "careers_url": "https://careers.maaden.com", "ats": "custom", "slug": ""},
    {"name": "STC", "country": "Saudi Arabia", "region": "Middle East",
     "careers_url": "https://www.stc.com.sa/content/stc/sa/en/personal/careers.html", "ats": "custom", "slug": ""},
    {"name": "Al Rajhi Bank", "country": "Saudi Arabia", "region": "Middle East",
     "careers_url": "https://www.alrajhibank.com.sa/en/careers", "ats": "custom", "slug": ""},
    {"name": "Saudi Electricity Company", "country": "Saudi Arabia", "region": "Middle East",
     "careers_url": "https://www.se.com.sa/en-us/Careers", "ats": "custom", "slug": ""},
    {"name": "Mobily", "country": "Saudi Arabia", "region": "Middle East",
     "careers_url": "https://www.mobily.com.sa/en/careers", "ats": "custom", "slug": ""},
    {"name": "Zain KSA", "country": "Saudi Arabia", "region": "Middle East",
     "careers_url": "https://www.sa.zain.com/en/careers", "ats": "custom", "slug": ""},

    # MIDDLE EAST — UAE
    {"name": "ADNOC", "country": "UAE", "region": "Middle East",
     "careers_url": "https://www.adnoc.ae/en/careers", "ats": "custom", "slug": ""},
    {"name": "Emirates Group", "country": "UAE", "region": "Middle East",
     "careers_url": "https://www.emiratesgroupcareers.com", "ats": "custom", "slug": ""},
    {"name": "Emaar", "country": "UAE", "region": "Middle East",
     "careers_url": "https://www.emaar.com/en/careers/", "ats": "custom", "slug": ""},
    {"name": "DP World", "country": "UAE", "region": "Middle East",
     "careers_url": "https://www.dpworld.com/careers", "ats": "custom", "slug": ""},
    {"name": "Etisalat", "country": "UAE", "region": "Middle East",
     "careers_url": "https://www.etisalat.ae/en/careers", "ats": "custom", "slug": ""},
    {"name": "First Abu Dhabi Bank", "country": "UAE", "region": "Middle East",
     "careers_url": "https://www.bankfab.com/en-ae/careers", "ats": "custom", "slug": ""},
    {"name": "Emirates NBD", "country": "UAE", "region": "Middle East",
     "careers_url": "https://www.emiratesnbd.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "Majid Al Futtaim", "country": "UAE", "region": "Middle East",
     "careers_url": "https://www.majidalfuttaim.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "Mubadala", "country": "UAE", "region": "Middle East",
     "careers_url": "https://www.mubadala.com/en/careers", "ats": "custom", "slug": ""},

    # MIDDLE EAST — Qatar
    {"name": "QatarEnergy", "country": "Qatar", "region": "Middle East",
     "careers_url": "https://www.qatarenergy.qa/en/Careers/Pages/default.aspx", "ats": "custom", "slug": ""},
    {"name": "Qatar Airways", "country": "Qatar", "region": "Middle East",
     "careers_url": "https://careers.qatarairways.com", "ats": "custom", "slug": ""},
    {"name": "Ooredoo", "country": "Qatar", "region": "Middle East",
     "careers_url": "https://www.ooredoo.qa/en/careers", "ats": "custom", "slug": ""},
    {"name": "QNB", "country": "Qatar", "region": "Middle East",
     "careers_url": "https://www.qnb.com/sites/qnb/qnbglobal/en/qnbcareers", "ats": "custom", "slug": ""},

    # MIDDLE EAST — Kuwait
    {"name": "Kuwait Oil Company", "country": "Kuwait", "region": "Middle East",
     "careers_url": "https://www.koc.com.kw/en/careers", "ats": "custom", "slug": ""},
    {"name": "KNPC", "country": "Kuwait", "region": "Middle East",
     "careers_url": "https://www.knpc.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "Agility", "country": "Kuwait", "region": "Middle East",
     "careers_url": "https://www.agility.com/en/careers/", "ats": "workable", "slug": "agility"},
    {"name": "Zain", "country": "Kuwait", "region": "Middle East",
     "careers_url": "https://www.zain.com/en/careers", "ats": "custom", "slug": ""},

    # MIDDLE EAST — Bahrain
    {"name": "Bapco", "country": "Bahrain", "region": "Middle East",
     "careers_url": "https://www.bapco.net/en/careers", "ats": "custom", "slug": ""},
    {"name": "Alba", "country": "Bahrain", "region": "Middle East",
     "careers_url": "https://www.alba.com.bh/careers", "ats": "custom", "slug": ""},
    {"name": "Batelco", "country": "Bahrain", "region": "Middle East",
     "careers_url": "https://www.batelco.com/careers/", "ats": "custom", "slug": ""},

    # MIDDLE EAST — Oman
    {"name": "PDO", "country": "Oman", "region": "Middle East",
     "careers_url": "https://www.pdo.co.om/en/careers/Pages/default.aspx", "ats": "custom", "slug": ""},
    {"name": "Oman Air", "country": "Oman", "region": "Middle East",
     "careers_url": "https://www.omanair.com/careers", "ats": "custom", "slug": ""},
    {"name": "Bank Muscat", "country": "Oman", "region": "Middle East",
     "careers_url": "https://www.bankmuscat.com/en/careers", "ats": "custom", "slug": ""},

    # ═══════════════════════════════════════════
    # EUROPE — Germany
    # ═══════════════════════════════════════════
    {"name": "Siemens", "country": "Germany", "region": "Europe",
     "careers_url": "https://jobs.siemens.com", "ats": "custom", "slug": ""},
    {"name": "Bosch", "country": "Germany", "region": "Europe",
     "careers_url": "https://www.bosch.com/careers", "ats": "custom", "slug": ""},
    {"name": "BMW", "country": "Germany", "region": "Europe",
     "careers_url": "https://www.bmwgroup.jobs", "ats": "custom", "slug": ""},
    {"name": "Mercedes-Benz", "country": "Germany", "region": "Europe",
     "careers_url": "https://group.mercedes-benz.com/careers", "ats": "custom", "slug": ""},
    {"name": "Volkswagen", "country": "Germany", "region": "Europe",
     "careers_url": "https://www.volkswagen-careers.com", "ats": "custom", "slug": ""},
    {"name": "SAP", "country": "Germany", "region": "Europe",
     "careers_url": "https://jobs.sap.com", "ats": "custom", "slug": ""},
    {"name": "Lufthansa", "country": "Germany", "region": "Europe",
     "careers_url": "https://www.be-lufthansa.com", "ats": "custom", "slug": ""},
    {"name": "Deutsche Post DHL", "country": "Germany", "region": "Europe",
     "careers_url": "https://careers.dhl.com", "ats": "custom", "slug": ""},
    {"name": "BASF", "country": "Germany", "region": "Europe",
     "careers_url": "https://www.basf.com/global/en/careers", "ats": "custom", "slug": ""},
    {"name": "Bayer", "country": "Germany", "region": "Europe",
     "careers_url": "https://career.bayer.com", "ats": "custom", "slug": ""},
    {"name": "Adidas", "country": "Germany", "region": "Europe",
     "careers_url": "https://careers.adidas-group.com", "ats": "custom", "slug": ""},
    {"name": "Zalando", "country": "Germany", "region": "Europe",
     "careers_url": "https://jobs.zalando.com", "ats": "custom", "slug": ""},

    # EUROPE — Netherlands
    {"name": "Shell", "country": "Netherlands", "region": "Europe",
     "careers_url": "https://www.shell.com/careers", "ats": "custom", "slug": ""},
    {"name": "Philips", "country": "Netherlands", "region": "Europe",
     "careers_url": "https://www.careers.philips.com", "ats": "custom", "slug": ""},
    {"name": "Unilever", "country": "Netherlands", "region": "Europe",
     "careers_url": "https://careers.unilever.com", "ats": "custom", "slug": ""},
    {"name": "Heineken", "country": "Netherlands", "region": "Europe",
     "careers_url": "https://www.theheinekencompany.com/careers", "ats": "custom", "slug": ""},
    {"name": "ASML", "country": "Netherlands", "region": "Europe",
     "careers_url": "https://www.asml.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "ING", "country": "Netherlands", "region": "Europe",
     "careers_url": "https://www.ing.jobs", "ats": "custom", "slug": ""},
    {"name": "Booking.com", "country": "Netherlands", "region": "Europe",
     "careers_url": "https://careers.booking.com", "ats": "custom", "slug": ""},

    # EUROPE — France
    {"name": "TotalEnergies", "country": "France", "region": "Europe",
     "careers_url": "https://careers.totalenergies.com", "ats": "custom", "slug": ""},
    {"name": "Airbus", "country": "France", "region": "Europe",
     "careers_url": "https://www.airbus.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "Renault", "country": "France", "region": "Europe",
     "careers_url": "https://group.renault.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "Carrefour", "country": "France", "region": "Europe",
     "careers_url": "https://carrefour-recruitment.com", "ats": "custom", "slug": ""},
    {"name": "L'Oreal", "country": "France", "region": "Europe",
     "careers_url": "https://careers.loreal.com", "ats": "custom", "slug": ""},
    {"name": "Sanofi", "country": "France", "region": "Europe",
     "careers_url": "https://www.sanofi.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "BNP Paribas", "country": "France", "region": "Europe",
     "careers_url": "https://group.bnpparibas/en/careers", "ats": "custom", "slug": ""},

    # EUROPE — Switzerland
    {"name": "Nestle", "country": "Switzerland", "region": "Europe",
     "careers_url": "https://www.nestle.com/jobs", "ats": "custom", "slug": ""},
    {"name": "Roche", "country": "Switzerland", "region": "Europe",
     "careers_url": "https://careers.roche.com", "ats": "custom", "slug": ""},
    {"name": "Novartis", "country": "Switzerland", "region": "Europe",
     "careers_url": "https://www.novartis.com/careers", "ats": "custom", "slug": ""},
    {"name": "UBS", "country": "Switzerland", "region": "Europe",
     "careers_url": "https://www.ubs.com/global/en/careers", "ats": "custom", "slug": ""},

    # EUROPE — UK
    {"name": "BP", "country": "UK", "region": "Europe",
     "careers_url": "https://www.bp.com/en/global/corporate/careers", "ats": "custom", "slug": ""},
    {"name": "AstraZeneca", "country": "UK", "region": "Europe",
     "careers_url": "https://careers.astrazeneca.com", "ats": "custom", "slug": ""},
    {"name": "HSBC", "country": "UK", "region": "Europe",
     "careers_url": "https://mycareer.hsbc.com", "ats": "custom", "slug": ""},
    {"name": "Vodafone", "country": "UK", "region": "Europe",
     "careers_url": "https://careers.vodafone.com", "ats": "custom", "slug": ""},
    {"name": "Tesco", "country": "UK", "region": "Europe",
     "careers_url": "https://www.tesco-careers.com", "ats": "custom", "slug": ""},
    {"name": "Rolls-Royce", "country": "UK", "region": "Europe",
     "careers_url": "https://careers.rolls-royce.com", "ats": "custom", "slug": ""},

    # EUROPE — Spain
    {"name": "Santander", "country": "Spain", "region": "Europe",
     "careers_url": "https://www.santander.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "Telefonica", "country": "Spain", "region": "Europe",
     "careers_url": "https://www.telefonica.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "Inditex", "country": "Spain", "region": "Europe",
     "careers_url": "https://www.inditex.com/careers", "ats": "custom", "slug": ""},
    {"name": "Iberdrola", "country": "Spain", "region": "Europe",
     "careers_url": "https://www.iberdrola.com/careers", "ats": "custom", "slug": ""},

    # EUROPE — Italy
    {"name": "Eni", "country": "Italy", "region": "Europe",
     "careers_url": "https://www.eni.com/en-IT/careers.html", "ats": "custom", "slug": ""},
    {"name": "Enel", "country": "Italy", "region": "Europe",
     "careers_url": "https://www.enel.com/careers", "ats": "custom", "slug": ""},
    {"name": "Ferrari", "country": "Italy", "region": "Europe",
     "careers_url": "https://www.ferrari.com/en-EN/careers", "ats": "custom", "slug": ""},
    {"name": "Pirelli", "country": "Italy", "region": "Europe",
     "careers_url": "https://www.pirelli.com/careers", "ats": "custom", "slug": ""},

    # EUROPE — Sweden
    {"name": "Volvo", "country": "Sweden", "region": "Europe",
     "careers_url": "https://www.volvogroup.com/en/careers.html", "ats": "custom", "slug": ""},
    {"name": "Ericsson", "country": "Sweden", "region": "Europe",
     "careers_url": "https://www.ericsson.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "IKEA", "country": "Sweden", "region": "Europe",
     "careers_url": "https://www.ikea.com/global/en/careers", "ats": "custom", "slug": ""},
    {"name": "H&M", "country": "Sweden", "region": "Europe",
     "careers_url": "https://careers.hm.com", "ats": "custom", "slug": ""},
    {"name": "Spotify", "country": "Sweden", "region": "Europe",
     "careers_url": "https://www.lifeatspotify.com", "ats": "custom", "slug": ""},

    # EUROPE — Norway
    {"name": "Equinor", "country": "Norway", "region": "Europe",
     "careers_url": "https://www.equinor.com/careers", "ats": "custom", "slug": ""},
    {"name": "Telenor", "country": "Norway", "region": "Europe",
     "careers_url": "https://www.telenor.com/careers", "ats": "custom", "slug": ""},
    {"name": "Norsk Hydro", "country": "Norway", "region": "Europe",
     "careers_url": "https://www.hydro.com/en/careers", "ats": "custom", "slug": ""},
    {"name": "Yara", "country": "Norway", "region": "Europe",
     "careers_url": "https://www.yara.com/careers", "ats": "custom", "slug": ""},

    # EUROPE — Denmark
    {"name": "Maersk", "country": "Denmark", "region": "Europe",
     "careers_url": "https://www.maersk.com/careers", "ats": "custom", "slug": ""},
    {"name": "Novo Nordisk", "country": "Denmark", "region": "Europe",
     "careers_url": "https://www.novonordisk.com/careers", "ats": "custom", "slug": ""},
    {"name": "Vestas", "country": "Denmark", "region": "Europe",
     "careers_url": "https://careers.vestas.com", "ats": "custom", "slug": ""},
    {"name": "Carlsberg", "country": "Denmark", "region": "Europe",
     "careers_url": "https://www.carlsberggroup.com/careers", "ats": "custom", "slug": ""},

    # EUROPE — Poland
    {"name": "PKN Orlen", "country": "Poland", "region": "Europe",
     "careers_url": "https://kariera.orlen.pl", "ats": "custom", "slug": ""},
    {"name": "KGHM", "country": "Poland", "region": "Europe",
     "careers_url": "https://kariera.kghm.pl", "ats": "custom", "slug": ""},
    {"name": "PKO BP", "country": "Poland", "region": "Europe",
     "careers_url": "https://kariera.pkobp.pl", "ats": "custom", "slug": ""},

    # EUROPE — Ireland
    {"name": "CRH", "country": "Ireland", "region": "Europe",
     "careers_url": "https://www.crh.com/careers", "ats": "custom", "slug": ""},
    {"name": "Ryanair", "country": "Ireland", "region": "Europe",
     "careers_url": "https://www.ryanair.com/gb/en/useful-info/about-ryanair/work-for-us", "ats": "custom", "slug": ""},
    {"name": "Kerry Group", "country": "Ireland", "region": "Europe",
     "careers_url": "https://www.kerrygroup.com/careers", "ats": "custom", "slug": ""},

    # ═══════════════════════════════════════════
    # RUSSIA / CIS
    # ═══════════════════════════════════════════
    {"name": "Gazprom", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://www.gazprom.com/careers", "ats": "custom", "slug": ""},
    {"name": "Rosneft", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://www.rosneft.com/careers", "ats": "custom", "slug": ""},
    {"name": "Lukoil", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://www.lukoil.com/careers", "ats": "custom", "slug": ""},
    {"name": "Sberbank", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://rabota.sber.ru", "ats": "custom", "slug": ""},
    {"name": "Yandex", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://yandex.com/jobs", "ats": "custom", "slug": ""},
    {"name": "VTB", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://vtb.ru/career", "ats": "custom", "slug": ""},
    {"name": "Novatek", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://www.novatek.ru/en/career", "ats": "custom", "slug": ""},
    {"name": "Norilsk Nickel", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://www.nornickel.com/careers", "ats": "custom", "slug": ""},
    {"name": "Severstal", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://severstal.com/rus/career", "ats": "custom", "slug": ""},
    {"name": "Magnit", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://magnit.ru/career", "ats": "custom", "slug": ""},
    {"name": "Aeroflot", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://www.aeroflot.ru/ru-en/career", "ats": "custom", "slug": ""},
    {"name": "Russian Railways", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://team.rzd.ru", "ats": "custom", "slug": ""},
    {"name": "Rosatom", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://rosatom-career.ru", "ats": "custom", "slug": ""},
    {"name": "MTS", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://job.mts.ru", "ats": "custom", "slug": ""},
    {"name": "Megafon", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://megafon.ru/career", "ats": "custom", "slug": ""},
    {"name": "Wildberries", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://careers.wildberries.ru", "ats": "custom", "slug": ""},
    {"name": "Ozon", "country": "Russia", "region": "Russia/CIS",
     "careers_url": "https://job.ozon.ru", "ats": "custom", "slug": ""},

    # RUSSIA/CIS — Kazakhstan
    {"name": "KazMunayGas", "country": "Kazakhstan", "region": "Russia/CIS",
     "careers_url": "https://www.kmg.kz/en/career", "ats": "custom", "slug": ""},
    {"name": "Kazatomprom", "country": "Kazakhstan", "region": "Russia/CIS",
     "careers_url": "https://www.kazatomprom.kz/en/careers", "ats": "custom", "slug": ""},
    {"name": "Air Astana", "country": "Kazakhstan", "region": "Russia/CIS",
     "careers_url": "https://airastana.com/global/en-us/careers", "ats": "custom", "slug": ""},
    {"name": "Halyk Bank", "country": "Kazakhstan", "region": "Russia/CIS",
     "careers_url": "https://www.halykbank.kz/en/career", "ats": "custom", "slug": ""},
    {"name": "Kaspi Bank", "country": "Kazakhstan", "region": "Russia/CIS",
     "careers_url": "https://kaspi.kz/karera", "ats": "custom", "slug": ""},

    # RUSSIA/CIS — Uzbekistan
    {"name": "Uzbekneftegaz", "country": "Uzbekistan", "region": "Russia/CIS",
     "careers_url": "https://www.ung.uz/en/careers", "ats": "custom", "slug": ""},
    {"name": "UzAuto Motors", "country": "Uzbekistan", "region": "Russia/CIS",
     "careers_url": "https://uzautomotors.com/careers", "ats": "custom", "slug": ""},

    # RUSSIA/CIS — Azerbaijan
    {"name": "SOCAR", "country": "Azerbaijan", "region": "Russia/CIS",
     "careers_url": "https://www.socar.az/en/careers", "ats": "custom", "slug": ""},
    {"name": "Azercell", "country": "Azerbaijan", "region": "Russia/CIS",
     "careers_url": "https://www.azercell.com/en/about-us/career", "ats": "custom", "slug": ""},

    # RUSSIA/CIS — Belarus
    {"name": "Belaruskali", "country": "Belarus", "region": "Russia/CIS",
     "careers_url": "https://kali.by/en/careers", "ats": "custom", "slug": ""},
    {"name": "MAZ", "country": "Belarus", "region": "Russia/CIS",
     "careers_url": "https://maz.by/en/career", "ats": "custom", "slug": ""},
]

def get_companies_by_region(region):
    return [c for c in COMPANIES if c["region"] == region]

def get_all_regions():
    return ["Middle East", "Europe", "Russia/CIS"]

if __name__ == "__main__":
    print(f"Total companies: {len(COMPANIES)}")
    for r in get_all_regions():
        print(f"  {r}: {len(get_companies_by_region(r))}")