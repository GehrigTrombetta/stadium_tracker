# You can put tests for your package here. The test_should_pass is provided as
# an example.

# You can import functions from your finalproject package by using:
# from finalproject import module_name
# where module_name is the name of the module you want to test. For example, if
# you have a module called data_processing.py, you would use:
# from finalproject import data_processing
# To test functions in module_name, you would then run
# module_name.function_name()
# (passing in any needed arguments) in your test functions here.
# Note: You will need to have installed your finalproject package in order to
# import it here. You can do this by running
# pip install -e .
# See instructions.md for more details.

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

def test_should_pass():
    assert True

from finalproject.stadiumfinder import (
    haversine_vectorized,
    format_location,
    with_emoji,
    strip_emoji,
    google_geocode,
    LEAGUE_COLORS,
    LEAGUE_EMOJI,
    LEAGUE_ORDER,
    OTHER_LEAGUE_ORDER,
)

# haversine_vectorized

class TestHaversine:
    def test_same_location_is_zero(self):
        result = haversine_vectorized(40.0, -74.0, 40.0, -74.0)
        assert result == 0.0

    def test_known_distance_nyc_to_boston(self):
        result = haversine_vectorized(40.7128, -74.0060, 42.3601, -71.0589)
        assert 185 < result < 195

    def test_known_distance_nyc_to_la(self):
        result = haversine_vectorized(40.7128, -74.0060, 34.0522, -118.2437)
        assert 2400 < result < 2500

    def test_vectorized_with_series(self):
        lats = pd.Series([42.3601, 34.0522])
        lons = pd.Series([-71.0589, -118.2437])
        results = haversine_vectorized(40.7128, -74.0060, lats, lons)
        assert len(results) == 2
        assert results.iloc[0] < results.iloc[1]

    def test_returns_rounded_to_3_decimals(self):
        result = haversine_vectorized(40.7128, -74.0060, 42.3601, -71.0589)
        assert result == round(result, 3)


# format_location

class TestFormatLocation:
    def test_state_abbreviated(self):
        assert format_location("New York, New York") == "New York, NY"

    def test_texas_abbreviated(self):
        assert format_location("Houston, Texas") == "Houston, TX"

    def test_washington_dc_replaced(self):
        assert format_location("Washington, District of Columbia") == "Washington, D.C."

    def test_canadian_province_abbreviated(self):
        assert format_location("Toronto, Ontario") == "Toronto, ON"

    def test_british_columbia_abbreviated(self):
        assert format_location("Vancouver, British Columbia") == "Vancouver, BC"

    def test_unknown_state_unchanged(self):
        assert format_location("Springfield, Unknownstate") == "Springfield, Unknownstate"

    def test_empty_string(self):
        assert format_location("") == ""

# with_emoji / strip_emoji

class TestEmojiHelpers:
    def test_with_emoji_nba(self):
        assert with_emoji("NBA") == "🏀 NBA"

    def test_with_emoji_nfl(self):
        assert with_emoji("NFL") == "🏈 NFL"

    def test_with_emoji_mlb(self):
        assert with_emoji("MLB") == "⚾ MLB"

    def test_with_emoji_nhl(self):
        assert with_emoji("NHL") == "🏒 NHL"

    def test_with_emoji_mls(self):
        assert with_emoji("MLS") == "⚽ MLS"

    def test_with_emoji_wnba(self):
        assert with_emoji("WNBA") == "🏀 WNBA"

    def test_strip_emoji_nba(self):
        assert strip_emoji("🏀 NBA") == "NBA"

    def test_strip_emoji_wnba(self):
        assert strip_emoji("🏀 WNBA") == "WNBA"

    def test_strip_emoji_nfl(self):
        assert strip_emoji("🏈 NFL") == "NFL"

    def test_strip_emoji_mlb(self):
        assert strip_emoji("⚾ MLB") == "MLB"

    def test_strip_emoji_nhl(self):
        assert strip_emoji("🏒 NHL") == "NHL"

    def test_strip_emoji_mls(self):
        assert strip_emoji("⚽ MLS") == "MLS"

    def test_strip_then_with_roundtrip(self):
        for league in LEAGUE_EMOJI:
            assert strip_emoji(with_emoji(league)) == league

# google_geocode

class TestGoogleGeocode:
    def test_successful_response(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{
                "geometry": {
                    "location": {"lat": 43.0382, "lng": -76.1335}
                }
            }],
            "status": "OK"
        }
        with patch("finalproject.stadiumfinder.rq.get", return_value=mock_response):
            lat, lng = google_geocode("110 Smith Drive, Syracuse, NY 13210")
            assert lat == 43.0382
            assert lng == -76.1335

    def test_empty_results_returns_none(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [], "status": "ZERO_RESULTS"}
        with patch("finalproject.stadiumfinder.rq.get", return_value=mock_response):
            lat, lng = google_geocode("nowhere land")
            assert lat is None
            assert lng is None

    def test_request_exception_returns_none(self):
        with patch("finalproject.stadiumfinder.rq.get", side_effect=Exception("Network error")):
            lat, lng = google_geocode("some address")
            assert lat is None
            assert lng is None

    def test_correct_api_url_called(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [], "status": "ZERO_RESULTS"}
        with patch("finalproject.stadiumfinder.rq.get", return_value=mock_response) as mock_get:
            google_geocode("test address")
            call_args = mock_get.call_args
            assert "cent.ischool-iot.net/api/google/geocode" in call_args[0][0]

    def test_api_key_header_sent(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [], "status": "ZERO_RESULTS"}
        with patch("finalproject.stadiumfinder.rq.get", return_value=mock_response) as mock_get:
            google_geocode("test address")
            call_kwargs = mock_get.call_args[1]
            assert "X-API-KEY" in call_kwargs["headers"]


# League constants

class TestLeagueConstants:
    def test_all_leagues_have_colors(self):
        for league in OTHER_LEAGUE_ORDER:
            assert league in LEAGUE_COLORS

    def test_all_leagues_have_emojis(self):
        for league in OTHER_LEAGUE_ORDER:
            assert league in LEAGUE_EMOJI

    def test_league_order_contains_all_leagues(self):
        assert set(LEAGUE_ORDER) == set(OTHER_LEAGUE_ORDER)

    def test_league_order_has_no_duplicates(self):
        assert len(LEAGUE_ORDER) == len(set(LEAGUE_ORDER))

    def test_other_league_order_has_no_duplicates(self):
        assert len(OTHER_LEAGUE_ORDER) == len(set(OTHER_LEAGUE_ORDER))