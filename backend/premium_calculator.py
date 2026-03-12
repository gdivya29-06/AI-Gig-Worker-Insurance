"""
Weekly Premium Calculator for Food Delivery Workers
Premium is based on:
  - Worker's risk score
  - Average daily income (coverage amount = 3 days income)
  - Platform (Zomato vs Swiggy)
  - Chosen coverage tier
"""

from risk_model import calculate_risk_score

# ── Coverage tiers ────────────────────────────────────────────
COVERAGE_TIERS = {
    "basic": {
        "label": "Basic",
        "coverage_days": 2,         # pays for 2 lost days per week
        "base_rate": 0.04,          # 4% of coverage amount
        "description": "Covers 2 days of lost income per week"
    },
    "standard": {
        "label": "Standard",
        "coverage_days": 3,
        "base_rate": 0.055,
        "description": "Covers 3 days of lost income per week"
    },
    "premium": {
        "label": "Premium",
        "coverage_days": 5,
        "base_rate": 0.07,
        "description": "Covers up to 5 days of lost income per week"
    },
}

# Platform multiplier — Swiggy zones tend to have more density/competition
PLATFORM_MULTIPLIER = {
    "zomato": 1.0,
    "swiggy": 1.05,
    "default": 1.0,
}

def calculate_weekly_premium(
    city: str,
    zone: str,
    experience_years: float,
    avg_daily_income: float,
    platform: str,
    tier: str = "standard",
    month: int = None,
) -> dict:
    """
    Returns weekly premium, coverage amount, and full breakdown.
    """
    tier = tier.lower()
    if tier not in COVERAGE_TIERS:
        tier = "standard"

    tier_config = COVERAGE_TIERS[tier]

    # Step 1 — Risk score
    risk_data    = calculate_risk_score(city, zone, experience_years, avg_daily_income, month)
    risk_score   = risk_data["risk_score"]

    # Step 2 — Coverage amount (income protected per week)
    coverage_amount = round(avg_daily_income * tier_config["coverage_days"], 2)

    # Step 3 — Base premium
    base_premium = coverage_amount * tier_config["base_rate"]

    # Step 4 — Apply risk multiplier (risk score maps to 0.8x – 1.5x)
    risk_multiplier = 0.8 + (risk_score * 0.7)

    # Step 5 — Platform multiplier
    platform_mult = PLATFORM_MULTIPLIER.get(platform.lower(), PLATFORM_MULTIPLIER["default"])

    # Step 6 — Final weekly premium
    weekly_premium = round(base_premium * risk_multiplier * platform_mult, 2)

    # Clamp: min ₹15, max ₹250 per week
    weekly_premium = max(15.0, min(weekly_premium, 250.0))

    return {
        "weekly_premium":   weekly_premium,
        "coverage_amount":  coverage_amount,
        "tier":             tier_config["label"],
        "coverage_days":    tier_config["coverage_days"],
        "description":      tier_config["description"],
        "risk_score":       risk_score,
        "risk_level":       risk_data["risk_level"],
        "risk_breakdown":   risk_data["breakdown"],
        "multipliers": {
            "risk_multiplier":     round(risk_multiplier, 3),
            "platform_multiplier": platform_mult,
        },
        "available_tiers": {
            k: {
                "label":         v["label"],
                "coverage_days": v["coverage_days"],
                "description":   v["description"],
            }
            for k, v in COVERAGE_TIERS.items()
        }
    }