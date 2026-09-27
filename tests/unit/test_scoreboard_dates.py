"""Tests for how scoreboard requests scope themselves by date.

ESPN began answering every dates=YYYYMMDD-YYYYMMDD range with a 400 in
September 2026, which emptied every football week. These pin the query shapes
that still work: week= plus a bare season year for football, and one request
per month (dates=YYYYMM) wherever a span of days is needed.
"""

import os
import sys
from datetime import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import espn_api  # noqa: E402


def requested_url(league, **kwargs):
    with patch.object(espn_api, "requests") as fake_requests:
        fake_requests.get.return_value.status_code = 200
        fake_requests.get.return_value.json.return_value = {"events": []}
        espn_api.get_scores(league, **kwargs)
        return fake_requests.get.call_args[0][0]


class TestFootballWeekQuery:
    def test_week_is_scoped_by_season_year_not_a_date_range(self):
        url = requested_url("NFL", week=3, season=2026, seasontype=2)
        assert "week=3" in url
        assert "dates=2026&" in url or url.endswith("dates=2026")
        assert "seasontype=2" in url
        assert "-" not in url.split("?", 1)[1]

    def test_season_type_defaults_to_regular_season(self):
        assert "seasontype=2" in requested_url("NFL", week=1, season=2026)

    def test_preseason_week_keeps_its_season_type(self):
        # Week numbers restart per season type: preseason week 1 is the
        # Hall of Fame game, not the September opener.
        assert "seasontype=1" in requested_url("NFL", week=1, season=2026, seasontype=1)

    def test_ncaaf_keeps_its_division_filter(self):
        url = requested_url("NCAAF", week=4, season=2026, seasontype=2)
        assert "groups=" in url
        assert "dates=2026" in url


class TestScoreboardMonths:
    def test_single_month(self):
        assert espn_api.scoreboard_months(datetime(2026, 9, 1), datetime(2026, 9, 30)) == ["202609"]

    def test_spans_a_year_boundary(self):
        assert espn_api.scoreboard_months(datetime(2026, 11, 20), datetime(2027, 2, 3)) == [
            "202611", "202612", "202701", "202702"]
