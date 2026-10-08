"""
Country → Region mapping for visa tracking filters
"""

REGIONS = {
    "SOUTH_ASIA": {
        "label": "🌏 South Asia",
        "countries": [
            "India", "Pakistan", "Bangladesh", "Nepal", "Sri Lanka",
            "Bhutan", "Maldives", "Afghanistan"
        ],
    },
    "SOUTHEAST_ASIA": {
        "label": "🌏 Southeast Asia",
        "countries": [
            "Singapore", "Malaysia", "Thailand", "Vietnam", "Indonesia",
            "Philippines", "Myanmar", "Cambodia", "Laos", "Brunei",
        ],
    },
    "EAST_ASIA": {
        "label": "🌏 East Asia",
        "countries": ["China", "Japan", "South Korea", "Taiwan", "Hong Kong", "Mongolia"],
    },
    "MIDDLE_EAST": {
        "label": "🕌 Middle East",
        "countries": [
            "UAE", "Dubai", "Saudi Arabia", "Qatar", "Kuwait", "Bahrain",
            "Oman", "Jordan", "Lebanon", "Israel", "Turkey", "Iran", "Iraq",
        ],
    },
    "CENTRAL_ASIA": {
        "label": "🌏 Central Asia",
        "countries": ["Kazakhstan", "Uzbekistan", "Kyrgyzstan", "Tajikistan", "Turkmenistan"],
    },
    "CIS_RUSSIA": {
        "label": "🐻 CIS / Russia",
        "countries": [
            "Russia", "Belarus", "Ukraine", "Georgia", "Armenia",
            "Azerbaijan", "Moldova",
        ],
    },
    "EUROPE": {
        "label": "🇪🇺 Europe",
        "countries": [
            # Western
            "UK", "Ireland", "France", "Germany", "Netherlands", "Belgium",
            "Luxembourg", "Switzerland", "Austria",
            # Southern
            "Spain", "Portugal", "Italy", "Greece", "Malta", "Cyprus",
            # Northern
            "Sweden", "Norway", "Denmark", "Finland", "Iceland",
            # Central/Eastern
            "Poland", "Czech Republic", "Slovakia", "Hungary", "Romania",
            "Bulgaria", "Croatia", "Slovenia", "Serbia", "Bosnia",
            "Estonia", "Latvia", "Lithuania",
        ],
    },
    "NORTH_AMERICA": {
        "label": "🌎 North America",
        "countries": ["USA", "Canada", "Mexico"],
    },
    "LATIN_AMERICA": {
        "label": "🌴 Latin America",
        "countries": [
            "Brazil", "Argentina", "Chile", "Colombia", "Peru", "Venezuela",
            "Ecuador", "Bolivia", "Paraguay", "Uruguay", "Costa Rica",
            "Panama", "Guatemala", "Cuba", "Dominican Republic",
        ],
    },
    "AFRICA": {
        "label": "🌍 Africa",
        "countries": [
            "Nigeria", "Kenya", "South Africa", "Egypt", "Morocco",
            "Ghana", "Ethiopia", "Tanzania", "Uganda", "Rwanda",
            "Senegal", "Ivory Coast", "Tunisia", "Algeria", "Libya",
            "Zimbabwe", "Zambia", "Botswana", "Namibia", "Mozambique",
        ],
    },
    "OCEANIA": {
        "label": "🏝️ Oceania",
        "countries": ["Australia", "New Zealand", "Fiji", "Samoa", "Papua New Guinea"],
    },
}


def get_all_regions():
    """Return list of {code, label, countries}"""
    return [
        {"code": code, "label": info["label"], "countries": info["countries"]}
        for code, info in REGIONS.items()
    ]


def get_country_region(country_name):
    """Get region code for a country."""
    if not country_name:
        return None
    c = country_name.strip().lower()
    for code, info in REGIONS.items():
        for country in info["countries"]:
            if country.lower() == c:
                return code
    return None


def get_countries_by_region(region_code):
    """All countries in a region."""
    return REGIONS.get(region_code, {}).get("countries", [])


def is_valid_region(region_code):
    return region_code in REGIONS