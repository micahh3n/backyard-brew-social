from datetime import date
from unittest.mock import Mock, patch

import weather


def _fake_response(weathercode, high_f):
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json.return_value = {
        "daily": {"weathercode": [weathercode], "temperature_2m_max": [high_f]}
    }
    return resp


def test_forecast_blurb_formats_known_weather_code():
    with patch("weather.requests.get", return_value=_fake_response(0, 74.2)):
        result = weather.forecast_blurb(date(2026, 7, 14))
    assert result == "clear skies and 74F"


def test_forecast_blurb_falls_back_to_generic_phrase_for_unknown_code():
    with patch("weather.requests.get", return_value=_fake_response(999, 60.0)):
        result = weather.forecast_blurb(date(2026, 7, 14))
    assert result == "good weather and 60F"


def test_forecast_blurb_returns_none_on_network_failure():
    with patch("weather.requests.get", side_effect=Exception("timeout")):
        result = weather.forecast_blurb(date(2026, 7, 14))
    assert result is None


def test_forecast_blurb_returns_none_on_malformed_response():
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json.return_value = {"daily": {}}
    with patch("weather.requests.get", return_value=resp):
        result = weather.forecast_blurb(date(2026, 7, 14))
    assert result is None
