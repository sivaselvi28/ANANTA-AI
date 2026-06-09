"""
api_service.py - Integrates with free external APIs (OpenWeatherMap + Exchange Rates).
"""
import requests
from datetime import datetime

# Free tier API keys (use env vars or replace with your own)
WEATHER_API_KEY = "demo"  # Replace with real key from openweathermap.org
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
EXCHANGE_BASE_URL = "https://open.er-api.com/v6/latest/USD"  # Free, no key required


def get_weather(city: str = "New York") -> dict:
    """Fetch current weather for a city using OpenWeatherMap API."""
    try:
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric",
        }
        r = requests.get(WEATHER_BASE_URL, params=params, timeout=10)

        if r.status_code == 401:
            # Fallback: use wttr.in which is free with no key
            return _get_weather_fallback(city)

        if r.status_code == 200:
            data = r.json()
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"].title(),
                "wind_speed": data["wind"]["speed"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "OpenWeatherMap",
            }
        return _get_weather_fallback(city)

    except Exception as e:
        return _get_weather_fallback(city)


def _get_weather_fallback(city: str) -> dict:
    """Fallback: use wttr.in free weather API (no key needed)."""
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=j1"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            current = data["current_condition"][0]
            return {
                "city": city,
                "country": data["nearest_area"][0]["country"][0]["value"] if data.get("nearest_area") else "Unknown",
                "temperature": float(current["temp_C"]),
                "feels_like": float(current["FeelsLikeC"]),
                "humidity": int(current["humidity"]),
                "description": current["weatherDesc"][0]["value"],
                "wind_speed": float(current["windspeedKmph"]) / 3.6,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "wttr.in",
            }
    except Exception:
        pass

    # Final fallback: mock data
    return {
        "city": city,
        "country": "N/A",
        "temperature": 28.5,
        "feels_like": 30.0,
        "humidity": 65,
        "description": "Partly Cloudy (Demo)",
        "wind_speed": 4.2,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "Demo (API unavailable)",
    }


def get_exchange_rates(base: str = "USD") -> dict:
    """Fetch current exchange rates (free API, no key needed)."""
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            rates = data.get("rates", {})
            # Return key currencies
            key_currencies = ["INR", "EUR", "GBP", "JPY", "AUD", "CAD", "SGD", "AED"]
            filtered = {k: v for k, v in rates.items() if k in key_currencies}
            return {
                "base": base,
                "rates": filtered,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "ExchangeRate-API",
            }
    except Exception:
        pass

    # Fallback demo data
    return {
        "base": "USD",
        "rates": {"INR": 83.5, "EUR": 0.92, "GBP": 0.79, "JPY": 149.5, "AUD": 1.53},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "Demo (API unavailable)",
    }


def detect_api_intent(question: str) -> tuple[str, str]:
    """
    Detect if the question requires external API data.
    Returns (api_type, extracted_param) or ("none", "")
    """
    q = question.lower()

    # Weather detection
    weather_keywords = ["weather", "temperature", "rain", "sunny", "cloudy", "forecast", "climate"]
    if any(kw in q for kw in weather_keywords):
        # Try to extract city name
        city = "New York"  # default
        city_hints = ["in ", "at ", "for ", "of "]
        for hint in city_hints:
            if hint in q:
                parts = q.split(hint)
                if len(parts) > 1:
                    candidate = parts[-1].strip().split()[0].capitalize()
                    if len(candidate) > 2:
                        city = candidate
                        break
        return "weather", city

    # Currency detection
    currency_keywords = ["exchange rate", "currency", "dollar", "rupee", "euro", "usd", "inr", "convert"]
    if any(kw in q for kw in currency_keywords):
        return "currency", "USD"

    return "none", ""
