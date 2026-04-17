"""
Enhanced Disruption Trigger Engine — 5 Automated Triggers
=========================================================
Trigger 1: Heavy Rain / Flood Risk     (Weather API)
Trigger 2: Extreme Heat                (Weather API)
Trigger 3: Severe Air Pollution / AQI  (AQI API)
Trigger 4: Curfew / Civil Unrest       (Mock - rule based on time/date)
Trigger 5: Platform Outage             (Mock - simulated app downtime)

Each trigger returns:
  - is_active: bool
  - severity: low / medium / high
  - value: measured parameter
  - income_loss_pct: estimated % of income lost
  - message: human readable
"""

import requests
import random
from datetime import datetime

OPENWEATHER_API_KEY = "YOUR_FREE_API_KEY_HERE"
BASE_URL            = "http://api.openweathermap.org/data/2.5"
AQI_URL             = "http://api.openweathermap.org/data/2.5/air_pollution"

CITY_COORDS = {
    "bangalore": (12.9716, 77.5946),
    "mumbai":    (19.0760, 72.8777),
    "delhi":     (28.6139, 77.2090),
    "chennai":   (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867),
    "pune":      (18.5204, 73.8567),
    "kolkata":   (22.5726, 88.3639),
}

# ── Mock data per city ────────────────────────────────────────
MOCK_CONDITIONS = {
    "bangalore": {"temp": 36.0, "rainfall": 5.0,  "aqi": 2, "desc": "Partly cloudy"},
    "mumbai":    {"temp": 33.0, "rainfall": 48.0, "aqi": 3, "desc": "Heavy rain"},
    "delhi":     {"temp": 44.5, "rainfall": 0.0,  "aqi": 5, "desc": "Severe haze"},
    "chennai":   {"temp": 41.0, "rainfall": 60.0, "aqi": 3, "desc": "Thunderstorm"},
    "hyderabad": {"temp": 42.0, "rainfall": 3.0,  "aqi": 2, "desc": "Hot and humid"},
    "pune":      {"temp": 38.0, "rainfall": 12.0, "aqi": 2, "desc": "Warm"},
    "kolkata":   {"temp": 37.0, "rainfall": 35.0, "aqi": 4, "desc": "Heavy showers"},
    "default":   {"temp": 36.0, "rainfall": 8.0,  "aqi": 2, "desc": "Partly cloudy"},
}

def _get_weather(city: str) -> dict:
    """Fetch weather — use mock if no API key."""
    if OPENWEATHER_API_KEY == "YOUR_FREE_API_KEY_HERE":
        d = MOCK_CONDITIONS.get(city.lower(), MOCK_CONDITIONS["default"])
        return {
            "temp":     d["temp"],
            "rainfall": d["rainfall"],
            "aqi":      d["aqi"],
            "desc":     d["desc"],
            "source":   "mock"
        }
    coords = CITY_COORDS.get(city.lower())
    if not coords:
        d = MOCK_CONDITIONS["default"]
        return {"temp": d["temp"], "rainfall": d["rainfall"],
                "aqi": d["aqi"], "desc": d["desc"], "source": "mock"}
    lat, lon = coords
    try:
        wr   = requests.get(f"{BASE_URL}/weather",
                            params={"lat": lat, "lon": lon,
                                    "appid": OPENWEATHER_API_KEY, "units": "metric"},
                            timeout=5).json()
        aqir = requests.get(AQI_URL,
                            params={"lat": lat, "lon": lon,
                                    "appid": OPENWEATHER_API_KEY},
                            timeout=5).json()
        rain = wr.get("rain", {}).get("1h", 0)
        aqi  = aqir["list"][0]["main"]["aqi"] if aqir.get("list") else 1
        return {
            "temp":     wr["main"]["temp"],
            "rainfall": rain,
            "aqi":      aqi,
            "desc":     wr["weather"][0]["description"],
            "source":   "openweathermap"
        }
    except Exception:
        d = MOCK_CONDITIONS.get(city.lower(), MOCK_CONDITIONS["default"])
        return {"temp": d["temp"], "rainfall": d["rainfall"],
                "aqi": d["aqi"], "desc": d["desc"], "source": "mock"}

# ══════════════════════════════════════════════════════════════
# TRIGGER 1 — Heavy Rain / Flood Risk
# ══════════════════════════════════════════════════════════════
def check_rain_trigger(weather: dict) -> dict:
    rain = weather["rainfall"]
    if rain >= 50:
        return {
            "type":     "flood_risk",
            "is_active":        True,
            "severity":         "high",
            "value":            f"{rain} mm/hr",
            "income_loss_pct":  100,
            "message":          "Flood risk — deliveries completely halted",
            "icon":             "🌊"
        }
    elif rain >= 20:
        return {
            "type":     "heavy_rain",
            "is_active":        True,
            "severity":         "medium",
            "value":            f"{rain} mm/hr",
            "income_loss_pct":  60,
            "message":          "Heavy rain — delivery capacity severely reduced",
            "icon":             "🌧️"
        }
    return {"type": "rain", "is_active": False, "severity": "none",
            "value": f"{rain} mm/hr", "income_loss_pct": 0, "message": "", "icon": "🌦️"}

# ══════════════════════════════════════════════════════════════
# TRIGGER 2 — Extreme Heat
# ══════════════════════════════════════════════════════════════
def check_heat_trigger(weather: dict) -> dict:
    temp = weather["temp"]
    if temp >= 45:
        return {
            "type":     "extreme_heat",
            "is_active":        True,
            "severity":         "high",
            "value":            f"{temp}°C",
            "income_loss_pct":  80,
            "message":          "Dangerous heat — outdoor work life-threatening",
            "icon":             "🌡️"
        }
    elif temp >= 42:
        return {
            "type":     "extreme_heat",
            "is_active":        True,
            "severity":         "medium",
            "value":            f"{temp}°C",
            "income_loss_pct":  40,
            "message":          "Extreme heat — reduced working hours advised",
            "icon":             "☀️"
        }
    return {"type": "heat", "is_active": False, "severity": "none",
            "value": f"{temp}°C", "income_loss_pct": 0, "message": "", "icon": "🌤️"}

# ══════════════════════════════════════════════════════════════
# TRIGGER 3 — Severe Air Pollution / AQI
# ══════════════════════════════════════════════════════════════
def check_aqi_trigger(weather: dict) -> dict:
    aqi = weather["aqi"]  # 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
    if aqi == 5:
        return {
            "type":     "severe_pollution",
            "is_active":        True,
            "severity":         "high",
            "value":            f"AQI Index {aqi}/5 (Severe)",
            "income_loss_pct":  70,
            "message":          "Hazardous air quality — outdoor work dangerous",
            "icon":             "😷"
        }
    elif aqi == 4:
        return {
            "type":     "poor_aqi",
            "is_active":        True,
            "severity":         "medium",
            "value":            f"AQI Index {aqi}/5 (Poor)",
            "income_loss_pct":  30,
            "message":          "Poor air quality — limited outdoor working advised",
            "icon":             "🌫️"
        }
    return {"type": "aqi", "is_active": False, "severity": "none",
            "value": f"AQI Index {aqi}/5", "income_loss_pct": 0, "message": "", "icon": "✅"}

# ══════════════════════════════════════════════════════════════
# TRIGGER 4 — Curfew / Civil Unrest (Mock)
# ══════════════════════════════════════════════════════════════
CURFEW_CITIES = {
    # city: (start_hour, end_hour, reason)
    # In real system this comes from govt API / news API
    # Using mock data for demonstration
}

MOCK_CURFEW_EVENTS = {
    # Simulate occasional curfews for demo purposes
    # In production: integrate with news API or govt alerts
}

def check_curfew_trigger(city: str) -> dict:
    """
    Check for curfew or civil unrest.
    In production: integrate with news APIs, govt alert APIs.
    Currently uses mock simulation.
    """
    now  = datetime.now()
    hour = now.hour

    # Mock: simulate curfew in certain cities on certain days
    # This would be replaced with real API in production
    city_lower = city.lower()

    # Simulate a mock curfew scenario for demonstration
    # Real implementation would call: https://newsapi.org or govt APIs
    curfew_active = False
    curfew_reason = ""

    # Example: If it's a weekend and specific city (mock scenario)
    if city_lower in CURFEW_CITIES:
        start, end, reason = CURFEW_CITIES[city_lower]
        if start <= hour <= end:
            curfew_active = True
            curfew_reason = reason

    if curfew_active:
        return {
            "type":     "curfew",
            "is_active":        True,
            "severity":         "high",
            "value":            f"Curfew active {hour}:00",
            "income_loss_pct":  100,
            "message":          f"Curfew in effect — {curfew_reason}. No deliveries possible.",
            "icon":             "🚫"
        }

    return {
        "type":    "curfew",
        "is_active":       False,
        "severity":        "none",
        "value":           "No curfew",
        "income_loss_pct": 0,
        "message":         "",
        "icon":            "✅"
    }

# ══════════════════════════════════════════════════════════════
# TRIGGER 5 — Platform / App Outage (Mock)
# ══════════════════════════════════════════════════════════════
PLATFORM_STATUS = {
    # In production: ping Zomato/Swiggy status pages
    # or use StatusPage APIs
    "zomato": "operational",
    "swiggy": "operational",
}

def check_platform_outage_trigger(platform: str) -> dict:
    """
    Check if the delivery platform app is down.
    In production: integrate with platform status APIs.
    """
    status = PLATFORM_STATUS.get(platform.lower(), "operational")

    # Simulate occasional outages for demo
    # In production this checks real platform uptime
    if status == "down":
        return {
            "type":     "platform_outage",
            "is_active":        True,
            "severity":         "high",
            "value":            f"{platform.title()} app DOWN",
            "income_loss_pct":  100,
            "message":          f"{platform.title()} app is experiencing outage — no orders possible",
            "icon":             "📵"
        }
    elif status == "degraded":
        return {
            "type":     "platform_outage",
            "is_active":        True,
            "severity":         "medium",
            "value":            f"{platform.title()} app DEGRADED",
            "income_loss_pct":  50,
            "message":          f"{platform.title()} app is slow — order volume significantly reduced",
            "icon":             "⚠️"
        }

    return {
        "type":    "platform_outage",
        "is_active":       False,
        "severity":        "none",
        "value":           f"{platform.title()} operational",
        "income_loss_pct": 0,
        "message":         "",
        "icon":            "✅"
    }

# ══════════════════════════════════════════════════════════════
# MAIN — Run All 5 Triggers
# ══════════════════════════════════════════════════════════════
def detect_all_disruptions(city: str, platform: str = "zomato") -> dict:
    """
    Run all 5 triggers and return combined disruption status.
    This is the main function called by the claims engine.
    """
    weather    = _get_weather(city)
    conditions = {
        "city":           city,
        "temp_celsius":   weather["temp"],
        "rainfall_mm_hr": weather["rainfall"],
        "aqi_index":      weather["aqi"],
        "description":    weather["desc"],
        "source":         weather["source"],
        "timestamp":      datetime.utcnow().isoformat(),
    }

    # Run all 5 triggers
    triggers = [
        check_rain_trigger(weather),
        check_heat_trigger(weather),
        check_aqi_trigger(weather),
        check_curfew_trigger(city),
        check_platform_outage_trigger(platform),
    ]

    # Filter only active ones
    active = [t for t in triggers if t["is_active"]]

    # Calculate overall income loss (take worst case)
    max_loss = max([t["income_loss_pct"] for t in active], default=0)

    # Overall severity
    severities = [t["severity"] for t in active]
    if "high" in severities:
        overall_severity = "high"
    elif "medium" in severities:
        overall_severity = "medium"
    elif "low" in severities:
        overall_severity = "low"
    else:
        overall_severity = "none"

    return {
        "city":              city,
        "platform":          platform,
        "is_disrupted":      len(active) > 0,
        "overall_severity":  overall_severity,
        "disruptions":       active,
        "all_triggers":      triggers,
        "conditions":        conditions,
        "max_income_loss_pct": max_loss,
        "checked_at":        datetime.utcnow().isoformat(),
    }

# Backwards compatible alias for old weather.py calls
def detect_disruptions(city: str) -> dict:
    return detect_all_disruptions(city)