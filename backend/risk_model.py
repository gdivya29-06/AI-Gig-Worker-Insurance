from datetime import datetime

# ── Zone risk lookup (historical disruption frequency) ───────
# Higher = more floods/heat events historically
ZONE_RISK = {
    # Bangalore
    "koramangala": 0.6, "indiranagar": 0.5, "whitefield": 0.7,
    "electronic city": 0.65, "marathahalli": 0.75, "hsr layout": 0.55,
    "jp nagar": 0.6, "jayanagar": 0.5, "btm layout": 0.65,
    # Mumbai
    "andheri": 0.8, "bandra": 0.7, "dharavi": 0.85, "kurla": 0.8,
    "borivali": 0.6, "thane": 0.75, "dadar": 0.7,
    # Delhi
    "connaught place": 0.5, "lajpat nagar": 0.6, "rohini": 0.65,
    "dwarka": 0.7, "noida sector 18": 0.6,
    # Chennai
    "t nagar": 0.65, "anna nagar": 0.55, "velachery": 0.8,
    "tambaram": 0.7, "adyar": 0.6,
    # Hyderabad
    "hitech city": 0.55, "gachibowli": 0.6, "lb nagar": 0.75,
    "secunderabad": 0.65,
    # Default
    "default": 0.55,
}

CITY_BASE_RISK = {
    "mumbai": 0.75,
    "bangalore": 0.60,
    "chennai": 0.65,
    "delhi": 0.55,
    "hyderabad": 0.50,
    "kolkata": 0.70,
    "pune": 0.55,
    "default": 0.55,
}

# Months with highest disruption probability in India
HIGH_RISK_MONTHS = [6, 7, 8, 9]   # June–September (monsoon)
MODERATE_RISK_MONTHS = [3, 4, 5]  # March–May (extreme heat)

def get_season_risk(month: int = None) -> float:
    if month is None:
        month = datetime.now().month
    if month in HIGH_RISK_MONTHS:
        return 0.8
    if month in MODERATE_RISK_MONTHS:
        return 0.6
    return 0.3

def get_zone_risk(zone: str) -> float:
    return ZONE_RISK.get(zone.lower().strip(), ZONE_RISK["default"])

def get_city_risk(city: str) -> float:
    return CITY_BASE_RISK.get(city.lower().strip(), CITY_BASE_RISK["default"])

def get_experience_risk(years: float) -> float:
    """Less experience = higher risk (less prepared for disruptions)"""
    if years < 0.5:
        return 0.9
    if years < 1:
        return 0.75
    if years < 2:
        return 0.6
    if years < 4:
        return 0.45
    return 0.3

def get_income_risk(avg_daily_income: float) -> float:
    """Lower income = depends more on each working day"""
    if avg_daily_income < 400:
        return 0.9
    if avg_daily_income < 600:
        return 0.7
    if avg_daily_income < 800:
        return 0.55
    return 0.4

def calculate_risk_score(
    city: str,
    zone: str,
    experience_years: float,
    avg_daily_income: float,
    month: int = None,
) -> dict:
    """
    Returns a risk score (0–1) and breakdown.
    Weights: zone 30%, city 15%, season 25%, experience 15%, income 15%
    """
    zone_r       = get_zone_risk(zone)
    city_r       = get_city_risk(city)
    season_r     = get_season_risk(month)
    experience_r = get_experience_risk(experience_years)
    income_r     = get_income_risk(avg_daily_income)

    score = (
        zone_r       * 0.30 +
        city_r       * 0.15 +
        season_r     * 0.25 +
        experience_r * 0.15 +
        income_r     * 0.15
    )
    score = round(min(max(score, 0.0), 1.0), 4)

    if score >= 0.70:
        risk_level = "High"
    elif score >= 0.45:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "breakdown": {
            "zone_risk":        round(zone_r, 3),
            "city_risk":        round(city_r, 3),
            "season_risk":      round(season_r, 3),
            "experience_risk":  round(experience_r, 3),
            "income_risk":      round(income_r, 3),
        }
    }