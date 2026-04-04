"""
ML-Based Dynamic Premium Calculator
Uses a trained Random Forest model to predict weekly premium
based on hyper-local risk factors.

Features used:
  - zone_risk, city_risk, season_risk, experience_risk, income_risk
  - avg_daily_income, experience_years, month
  - platform (encoded)
  - tier (encoded)

The model is trained on synthetic but realistic data and
produces premiums that are more nuanced than pure rule-based logic.
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import pickle
import os

# ── Zone risk lookup (same as risk_model.py) ─────────────────
ZONE_RISK = {
    "koramangala": 0.6, "indiranagar": 0.5, "whitefield": 0.7,
    "electronic city": 0.65, "marathahalli": 0.75, "hsr layout": 0.55,
    "jp nagar": 0.6, "jayanagar": 0.5, "btm layout": 0.65,
    "andheri": 0.8, "bandra": 0.7, "dharavi": 0.85, "kurla": 0.8,
    "borivali": 0.6, "thane": 0.75, "dadar": 0.7,
    "connaught place": 0.5, "lajpat nagar": 0.6, "rohini": 0.65,
    "dwarka": 0.7, "noida sector 18": 0.6,
    "t nagar": 0.65, "anna nagar": 0.55, "velachery": 0.8,
    "tambaram": 0.7, "adyar": 0.6,
    "hitech city": 0.55, "gachibowli": 0.6, "lb nagar": 0.75,
    "default": 0.55,
}

CITY_RISK = {
    "mumbai": 0.75, "bangalore": 0.60, "chennai": 0.65,
    "delhi": 0.55, "hyderabad": 0.50, "kolkata": 0.70,
    "pune": 0.55, "default": 0.55,
}

TIER_COVERAGE_DAYS = {"basic": 2, "standard": 3, "premium": 5}
TIER_BASE_RATE     = {"basic": 0.04, "standard": 0.055, "premium": 0.07}
PLATFORM_MULT      = {"zomato": 1.0, "swiggy": 1.05}

MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_model.pkl")

def _generate_training_data(n=2000):
    """Generate realistic synthetic training data."""
    np.random.seed(42)
    X, y = [], []

    cities     = list(CITY_RISK.keys())[:-1]
    zones      = list(ZONE_RISK.keys())[:-1]
    platforms  = ["zomato", "swiggy"]
    tiers      = ["basic", "standard", "premium"]
    months     = list(range(1, 13))

    for _ in range(n):
        city        = np.random.choice(cities)
        zone        = np.random.choice(zones)
        platform    = np.random.choice(platforms)
        tier        = np.random.choice(tiers)
        month       = np.random.choice(months)
        income      = np.random.uniform(300, 1200)
        experience  = np.random.uniform(0.5, 8)

        city_r  = CITY_RISK.get(city, 0.55)
        zone_r  = ZONE_RISK.get(zone, 0.55)
        season_r = 0.8 if month in [6,7,8,9] else (0.6 if month in [3,4,5] else 0.3)
        exp_r   = max(0.3, 0.9 - (experience * 0.08))
        inc_r   = max(0.4, 0.9 - (income / 3000))

        risk_score = (zone_r*0.30 + city_r*0.15 + season_r*0.25 +
                      exp_r*0.15 + inc_r*0.15)

        coverage    = income * TIER_COVERAGE_DAYS[tier]
        base_prem   = coverage * TIER_BASE_RATE[tier]
        risk_mult   = 0.8 + (risk_score * 0.7)
        plat_mult   = PLATFORM_MULT.get(platform, 1.0)

        # Add small realistic noise
        noise       = np.random.normal(0, 2)
        premium     = np.clip(base_prem * risk_mult * plat_mult + noise, 15, 250)

        features = [
            city_r, zone_r, season_r, exp_r, inc_r,
            income, experience, month,
            1 if platform == "swiggy" else 0,
            ["basic","standard","premium"].index(tier),
            risk_score,
            coverage,
        ]
        X.append(features)
        y.append(round(premium, 2))

    return np.array(X), np.array(y)

def train_and_save_model():
    """Train the ML model and save it."""
    print("🤖 Training ML premium model...")
    X, y = _generate_training_data(2000)

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", GradientBoostingRegressor(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        ))
    ])
    model.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"✅ ML model trained and saved to {MODEL_PATH}")
    return model

def load_model():
    """Load model from disk, train if not found."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return train_and_save_model()

# Load model at import time
_model = None

def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model

def ml_calculate_premium(
    city: str,
    zone: str,
    experience_years: float,
    avg_daily_income: float,
    platform: str,
    tier: str = "standard",
    month: int = None,
) -> dict:
    """
    Use ML model to calculate weekly premium.
    Falls back to rule-based if model fails.
    """
    import datetime
    if month is None:
        month = datetime.datetime.now().month

    tier = tier.lower()
    if tier not in TIER_COVERAGE_DAYS:
        tier = "standard"

    city_r   = CITY_RISK.get(city.lower().strip(), 0.55)
    zone_r   = ZONE_RISK.get(zone.lower().strip(), 0.55)
    season_r = 0.8 if month in [6,7,8,9] else (0.6 if month in [3,4,5] else 0.3)
    exp_r    = max(0.3, 0.9 - (experience_years * 0.08))
    inc_r    = max(0.4, 0.9 - (avg_daily_income / 3000))

    risk_score   = (zone_r*0.30 + city_r*0.15 + season_r*0.25 +
                    exp_r*0.15 + inc_r*0.15)
    risk_score   = round(min(max(risk_score, 0.0), 1.0), 4)

    coverage     = avg_daily_income * TIER_COVERAGE_DAYS[tier]
    plat_encoded = 1 if platform.lower() == "swiggy" else 0
    tier_encoded = ["basic","standard","premium"].index(tier)

    features = np.array([[
        city_r, zone_r, season_r, exp_r, inc_r,
        avg_daily_income, experience_years, month,
        plat_encoded, tier_encoded,
        risk_score, coverage,
    ]])

    try:
        model          = get_model()
        ml_premium     = float(model.predict(features)[0])
        ml_premium     = round(max(15.0, min(ml_premium, 250.0)), 2)
        model_used     = "GradientBoosting ML"
    except Exception as e:
        # Fallback to rule-based
        base_prem  = coverage * TIER_BASE_RATE[tier]
        risk_mult  = 0.8 + (risk_score * 0.7)
        plat_mult  = PLATFORM_MULT.get(platform.lower(), 1.0)
        ml_premium = round(max(15.0, min(base_prem * risk_mult * plat_mult, 250.0)), 2)
        model_used = "rule-based (fallback)"

    if risk_score >= 0.70:
        risk_level = "High"
    elif risk_score >= 0.45:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    tier_labels = {
        "basic":    {"label": "Basic",    "days": 2, "desc": "Covers 2 days of lost income per week"},
        "standard": {"label": "Standard", "days": 3, "desc": "Covers 3 days of lost income per week"},
        "premium":  {"label": "Premium",  "days": 5, "desc": "Covers up to 5 days of lost income per week"},
    }

    return {
        "weekly_premium":   ml_premium,
        "coverage_amount":  round(coverage, 2),
        "tier":             tier_labels[tier]["label"],
        "coverage_days":    tier_labels[tier]["days"],
        "description":      tier_labels[tier]["desc"],
        "risk_score":       risk_score,
        "risk_level":       risk_level,
        "model_used":       model_used,
        "risk_breakdown": {
            "zone_risk":       round(zone_r, 3),
            "city_risk":       round(city_r, 3),
            "season_risk":     round(season_r, 3),
            "experience_risk": round(exp_r, 3),
            "income_risk":     round(inc_r, 3),
        },
        "multipliers": {
            "risk_multiplier":     round(0.8 + risk_score * 0.7, 3),
            "platform_multiplier": PLATFORM_MULT.get(platform.lower(), 1.0),
        },
        "available_tiers": {
            k: {"label": v["label"], "coverage_days": v["days"], "description": v["desc"]}
            for k, v in tier_labels.items()
        }
    }

# Pre-train on startup
if __name__ == "__main__":
    train_and_save_model()
    result = ml_calculate_premium("bangalore", "koramangala", 2, 650, "zomato", "standard")
    print(f"Test premium: ₹{result['weekly_premium']} | Model: {result['model_used']}")