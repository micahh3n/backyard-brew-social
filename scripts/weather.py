"""
weather.py - Free, no-key weather lookup for the "Weather Vibes" evergreen
post (see config.EVERGREEN_LABELS). Uses Open-Meteo's public forecast API --
no signup, no API key, no cost. Any failure degrades to None so a
weather-tied post can gracefully fall back to a generic vibe post instead of
blocking Sunday generation.
"""

from __future__ import annotations

from datetime import date

import requests

import config

WEATHER_CODES = {
    0: "clear skies", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "foggy", 51: "light drizzle", 53: "drizzle",
    55: "heavy drizzle", 61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 80: "rain showers",
    81: "rain showers", 82: "heavy rain showers", 95: "thunderstorms",
}


def forecast_blurb(for_date: date) -> str | None:
    """Return a short human phrase like 'sunny and 74F' for for_date, or
    None on any failure (network error, bad response, unsupported date)."""
    try:
        b = config.BUSINESS
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": b["latitude"],
                "longitude": b["longitude"],
                "daily": "weathercode,temperature_2m_max",
                "temperature_unit": "fahrenheit",
                "timezone": "America/Chicago",
                "start_date": for_date.isoformat(),
                "end_date": for_date.isoformat(),
            },
            timeout=15,
        )
        resp.raise_for_status()
        daily = resp.json()["daily"]
        code = daily["weathercode"][0]
        high = round(daily["temperature_2m_max"][0])
        desc = WEATHER_CODES.get(code, "good weather")
        return f"{desc} and {high}F"
    except Exception as exc:
        print(f"[weather] forecast lookup failed for {for_date}: {exc}")
        return None
