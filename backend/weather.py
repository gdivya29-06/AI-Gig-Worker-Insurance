"""
Weather & Disruption Trigger Engine
Uses OpenWeatherMap free API to detect:
  - Heavy rain (rainfall > 20mm/hr)
  - Extreme heat (temp > 42°C)
  - Poor AQI / severe pollution (AQI > 300)
  - Flood risk (sustained heavy rain)

Falls back to mock data if API key not set.
"""

import requests
from datetime import datetime

# ── Get a FREE key at https://openweathermap.org/api ─────────
OPENWEATHER_API_KEY = "YOUR_FREE_API_KEY_HERE"   # replace this
BASE_URL   = "https://api.openweathermap.org/data/2.5"
AQI_URL    = "http://api.openweathermap.org/data/2.5/air_pollution"

# ── Disruption thresholds ─────────────────────────────────────
THRESHOLDS = {
    "heavy_rain":   {"param": "rainfall_mm_hr", "value": 20,  "unit": "mm/hr"},
    "extreme_heat": {"param": "temp_celsius",   "value": 42,  "unit": "°C"},
    "poor_aqi":     {"param": "aqi_index",      "value": 4,   "unit": "AQI index (1-5)"},
    "flood_risk":   {"param": "rainfall_mm_hr", "value": 50,  "unit": "mm/hr"},
}

CITY_COORDINATES = {
    "bangalore": (12.9716, 77.5946),
    "mumbai":    (19.0760, 72.8777),
    "delhi":     (28.6139, 77.2090),
    "chennai":   (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867),
    "pune":      (18.5204, 73.8567),
    "kolkata":   (22.5726, 88.3639),
}

# ── Mock data fallback ────────────────────────────────────────
MOCK_DATA = {
    "bangalore": {"temp": 38.5, "rainfall": 0,    "aqi": 2, "description": "Partly cloudy"},
    "mumbai":    {"temp": 34.0, "rainfall": 45.0, "aqi": 3, "description": "Heavy rain"},
    "delhi":     {"temp": 44.0, "rainfall": 0,    "aqi": 5, "description": "Severe haze"},
    "chennai":   {"temp": 40.0, "rainfall": 25.0, "aqi": 3, "description": "Thunderstorm"},
    "hyderabad": {"temp": 41.5, "rainfall": 5.0,  "aqi": 2, "description": "Hot and humid"},
    "default":   {"temp": 36.0, "rainfall": 10.0, "aqi": 2, "description": "Partly cloudy"},
}

def _get_mock_conditions(city: str) -> dict:
    data = MOCK_DATA.get(city.lower(), MOCK_DATA["default"])
    return {
        "city":        city,
        "temp_celsius": data["temp"],
        "rainfall_mm_hr": data["rainfall"],
        "aqi_index":   data["aqi"],
        "description": data["description"],
        "source":      "mock",
        "timestamp":   datetime.utcnow().isoformat(),
    }

def get_weather_conditions(city: str) -> dict:
    """Fetch live weather; fall back to mock if API key missing."""
    if OPENWEATHER_API_KEY == "YOUR_FREE_API_KEY_HERE":
        return _get_mock_conditions(city)

    coords = CITY_COORDINATES.get(city.lower())
    if not coords:
        return _get_mock_conditions(city)

    lat, lon = coords
    try:
        # Current weather
        weather_resp = requests.get(
            f"{BASE_URL}/weather",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"},
            timeout=5
        )
        weather_data = weather_resp.json()

        # AQI
        aqi_resp = requests.get(
            AQI_URL,
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY},
            timeout=5
        )
        aqi_data = aqi_resp.json()

        rainfall = 0
        if "rain" in weather_data:
            rainfall = weather_data["rain"].get("1h", 0)

        return {
            "city":           city,
            "temp_celsius":   weather_data["main"]["temp"],
            "rainfall_mm_hr": rainfall,
            "aqi_index":      aqi_data["list"][0]["main"]["aqi"] if aqi_data.get("list") else 1,
            "description":    weather_data["weather"][0]["description"],
            "source":         "openweathermap",
            "timestamp":      datetime.utcnow().isoformat(),
        }
    except Exception:
        return _get_mock_conditions(city)

def detect_disruptions(city: str) -> dict:
    """
    Check current conditions against thresholds.
    Returns active disruptions and severity.
    """
    conditions   = get_weather_conditions(city)
    disruptions  = []
    is_disrupted = False

    # Heavy rain check
    if conditions["rainfall_mm_hr"] >= THRESHOLDS["flood_risk"]["value"]:
        disruptions.append({
            "type":     "flood_risk",
            "severity": "high",
            "value":    f"{conditions['rainfall_mm_hr']} mm/hr",
            "message":  "Flood risk — deliveries halted"
        })
        is_disrupted = True
    elif conditions["rainfall_mm_hr"] >= THRESHOLDS["heavy_rain"]["value"]:
        disruptions.append({
            "type":     "heavy_rain",
            "severity": "medium",
            "value":    f"{conditions['rainfall_mm_hr']} mm/hr",
            "message":  "Heavy rain — reduced delivery capacity"
        })
        is_disrupted = True

    # Extreme heat check
    if conditions["temp_celsius"] >= THRESHOLDS["extreme_heat"]["value"]:
        disruptions.append({
            "type":     "extreme_heat",
            "severity": "high",
            "value":    f"{conditions['temp_celsius']}°C",
            "message":  "Extreme heat — unsafe working conditions"
        })
        is_disrupted = True

    # AQI check (index 4 = Very Poor, 5 = Severe)
    if conditions["aqi_index"] >= THRESHOLDS["poor_aqi"]["value"]:
        severity = "high" if conditions["aqi_index"] == 5 else "medium"
        disruptions.append({
            "type":     "poor_aqi",
            "severity": severity,
            "value":    f"AQI index {conditions['aqi_index']}",
            "message":  "Severe pollution — outdoor work hazardous"
        })
        is_disrupted = True

    return {
        "city":          city,
        "is_disrupted":  is_disrupted,
        "disruptions":   disruptions,
        "conditions":    conditions,
        "checked_at":    datetime.utcnow().isoformat(),
    }