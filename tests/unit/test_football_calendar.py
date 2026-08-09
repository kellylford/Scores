"""Tests for football week resolution (services/football_calendar.py).

The scoreboard calendar is faked rather than fetched. These cover the places
where a wrong answer shows the user the wrong games entirely: the week-end
boundary, resolving today's week during preseason, and stepping across a
season-type boundary.
"""

import os
import sys
from datetime import date
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services import football_calendar as fc  # noqa: E402


def entry(label, value, start, end):
    return {"label": label, "value": str(value), "startDate": start, "endDate": end}


# A trimmed 2026 NFL calendar in ESPN's exact shape, including the Pacific-midnight
# bounds (T07:00Z start, T06:59Z end) that the date maths has to account for.
NFL_CALENDAR = [
    {"label": "Preseason", "value": "1", "entries": [
        entry("Hall of Fame Weekend", 1, "2026-08-06T07:00Z", "2026-08-13T06:59Z"),
        entry("Preseason Week 1", 2, "2026-08-13T07:00Z", "2026-08-20T06:59Z"),
        entry("Preseason Week 2", 3, "2026-08-20T07:00Z", "2026-08-27T06:59Z"),
        entry("Preseason Week 3", 4, "2026-08-27T07:00Z", "2026-09-09T06:59Z"),
    ]},
    {"label": "Regular Season", "value": "2", "entries": [
        entry("Week 1", 1, "2026-09-09T07:00Z", "2026-09-16T06:59Z"),
        entry("Week 2", 2, "2026-09-16T07:00Z", "2026-09-23T06:59Z"),
    ]},
    {"label": "Postseason", "value": "3", "entries": [
        entry("Wild Card", 1, "2027-01-13T08:00Z", "2027-01-20T07:59Z"),
    ]},
    # Carries no games; must never appear in navigation.
    {"label": "Off Season", "value": "4", "entries": [
        entry("All-Star", 1, "2027-01-28T08:00Z", "2027-02-01T07:59Z"),
    ]},
]


@pytest.fixture(autouse=True)
def clear_caches():
    fc._SEASON_WEEKS_CACHE.clear()
    fc._WEEK_DATE_CACHE.clear()
    yield
    fc._SEASON_WEEKS_CACHE.clear()
    fc._WEEK_DATE_CACHE.clear()


def calendar_payload(season_year=2026):
    return {"leagues": [{"season": {"year": season_year}, "calendar": NFL_CALENDAR}]}


@pytest.fixture
def nfl_calendar():
    """ESPN serving its 2026 calendar, whatever season is asked for.

    That is the real behaviour: the scoreboard ignores `season=` and always
    answers with the season it considers current.
    """
    with patch.object(fc, "requests") as fake_requests:
        fake_requests.get.return_value.status_code = 200
        fake_requests.get.return_value.json.return_value = calendar_payload(2026)
        yield fake_requests


class TestBoundDates:
    def test_end_bound_is_the_last_day_the_week_covers(self):
        # ESPN's T06:59Z end is 23:59 Pacific the day before. Reading the UTC date
        # would give Aug 20 and pull the next week's Thursday games into this one.
        start, end = fc._bound_dates("2026-08-13T07:00Z", "2026-08-20T06:59Z")
        assert start == date(2026, 8, 13)
        assert end == date(2026, 8, 19)

    def test_holds_across_daylight_saving(self):
        # In Pacific standard time the offset moves to 08:00Z / 07:59Z.
        start, end = fc._bound_dates("2027-01-13T08:00Z", "2027-01-20T07:59Z")
        assert start == date(2027, 1, 13)
        assert end == date(2027, 1, 19)

    def test_single_day_week_does_not_invert(self):
        start, end = fc._bound_dates("2026-08-06T07:00Z", "2026-08-06T06:59Z")
        assert start == end == date(2026, 8, 6)


class TestSeasonWeeks:
    def test_orders_preseason_before_regular_before_post(self, nfl_calendar):
        weeks = fc.get_season_weeks("NFL", 2026)
        assert [(w["season_type"], w["week"]) for w in weeks] == [
            (1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (2, 2), (3, 1)]

    def test_keeps_espn_labels(self, nfl_calendar):
        labels = [w["label"] for w in fc.get_season_weeks("NFL", 2026)]
        assert labels[:2] == ["Hall of Fame Weekend", "Preseason Week 1"]
        assert "Wild Card" in labels

    def test_off_season_is_not_navigable(self, nfl_calendar):
        assert all(w["season_type"] != 4 for w in fc.get_season_weeks("NFL", 2026))

    def test_seeds_the_week_date_cache(self, nfl_calendar):
        fc.get_season_weeks("NFL", 2026)
        # Preseason Week 1 is week 2 of season type 1.
        assert fc._WEEK_DATE_CACHE[("NFL", 2026, 1, 2)] == ("20260813", "20260819")

    def test_is_cached_so_navigation_makes_one_request(self, nfl_calendar):
        fc.get_season_weeks("NFL", 2026)
        fc.get_season_weeks("NFL", 2026)
        assert nfl_calendar.get.call_count == 1

    def test_unknown_league_returns_empty(self):
        assert fc.get_season_weeks("MLB", 2026) == []

    def test_a_season_espn_does_not_serve_returns_empty(self, nfl_calendar):
        # ESPN ignores season= and answers with 2026 regardless. Handing those
        # weeks back as if they were 2025's would mean showing 2026 dates for a
        # 2025 week; callers must fall through to the season-aware Core API.
        assert fc.get_season_weeks("NFL", 2025) == []

    def test_the_season_espn_did_serve_is_cached_under_its_real_year(self, nfl_calendar):
        fc.get_season_weeks("NFL", 2025)          # asked 2025, got 2026
        assert nfl_calendar.get.call_count == 1
        assert len(fc.get_season_weeks("NFL", 2026)) == 7   # served from cache
        assert nfl_calendar.get.call_count == 1

    def test_week_bounds_are_seeded_under_the_real_year_only(self, nfl_calendar):
        fc.get_season_weeks("NFL", 2025)
        assert ("NFL", 2026, 1, 2) in fc._WEEK_DATE_CACHE
        assert ("NFL", 2025, 1, 2) not in fc._WEEK_DATE_CACHE


class TestCurrentSeasonWeekAndType:
    def test_takes_the_season_from_espn_not_the_calendar_year(self, nfl_calendar):
        # get_football_season_year rolls over on 1 March, but ESPN keeps serving
        # the previous season until about late July. Trusting the heuristic in
        # that window puts every date past the end of the season, landing the
        # view on the last Super Bowl.
        season, season_type, week = fc.get_current_season_week_and_type(
            "NFL", today=date(2027, 4, 1))
        assert season == 2026
        assert (season_type, week) == (3, 1)   # the last week ESPN knows about

    def test_resolves_the_live_preseason_week(self, nfl_calendar):
        assert fc.get_current_season_week_and_type("NFL", today=date(2026, 8, 15)) == (2026, 1, 2)

    def test_falls_back_when_the_calendar_is_unavailable(self):
        with patch.object(fc, "requests") as fake_requests:
            fake_requests.get.return_value.status_code = 503
            season, season_type, week = fc.get_current_season_week_and_type(
                "NFL", today=date(2026, 8, 15))
        assert (season_type, week) == (2, 1)
        assert season == 2026   # falls back to the calendar-year heuristic


class TestCurrentWeek:
    def test_preseason_date_resolves_to_a_preseason_week(self, nfl_calendar):
        # The bug this fixes: ESPN's week.number is 1 here, which read as the
        # regular season opener a month away.
        assert fc.get_current_week_and_type("NFL", 2026, today=date(2026, 8, 9)) == (1, 1)
        assert fc.get_current_week_and_type("NFL", 2026, today=date(2026, 8, 15)) == (1, 2)

    def test_regular_season_date(self, nfl_calendar):
        assert fc.get_current_week_and_type("NFL", 2026, today=date(2026, 9, 12)) == (2, 1)

    def test_last_day_of_a_week_still_belongs_to_it(self, nfl_calendar):
        assert fc.get_current_week_and_type("NFL", 2026, today=date(2026, 8, 19)) == (1, 2)
        assert fc.get_current_week_and_type("NFL", 2026, today=date(2026, 8, 20)) == (1, 3)

    def test_before_the_season_picks_the_first_week(self, nfl_calendar):
        assert fc.get_current_week_and_type("NFL", 2026, today=date(2026, 5, 1)) == (1, 1)

    def test_after_the_season_picks_the_last_week(self, nfl_calendar):
        assert fc.get_current_week_and_type("NFL", 2026, today=date(2027, 6, 1)) == (3, 1)

    def test_falls_back_to_regular_week_one_without_a_calendar(self):
        with patch.object(fc, "requests") as fake_requests:
            fake_requests.get.return_value.status_code = 503
            assert fc.get_current_week_and_type("NFL", 2026, today=date(2026, 8, 9)) == (2, 1)

    def test_bare_week_number_helper_agrees(self, nfl_calendar):
        assert fc.get_current_football_week("NFL", 2026, today=date(2026, 8, 15)) == 2
        assert fc.get_current_football_week("MLB", 2026) is None


class TestStepWeek:
    def test_forward_within_a_season_type(self, nfl_calendar):
        assert fc.step_week("NFL", 2026, 1, 1, +1) == (1, 2)

    def test_forward_rolls_into_the_regular_season(self, nfl_calendar):
        assert fc.step_week("NFL", 2026, 1, 4, +1) == (2, 1)

    def test_back_rolls_into_the_preseason(self, nfl_calendar):
        # Without this there is no route to preseason at all once the regular
        # season is the default view.
        assert fc.step_week("NFL", 2026, 2, 1, -1) == (1, 4)

    def test_stops_at_the_first_week(self, nfl_calendar):
        assert fc.step_week("NFL", 2026, 1, 1, -1) == (1, 1)

    def test_stops_at_the_last_week(self, nfl_calendar):
        assert fc.step_week("NFL", 2026, 3, 1, +1) == (3, 1)

    def test_unknown_week_is_left_alone(self, nfl_calendar):
        assert fc.step_week("NFL", 2026, 2, 99, +1) == (2, 99)


class TestWeekLabel:
    def test_preseason_labels_are_not_bare_week_numbers(self, nfl_calendar):
        assert fc.get_week_label("NFL", 2026, 1, 1) == "Hall of Fame Weekend"
        assert fc.get_week_label("NFL", 2026, 1, 2) == "Preseason Week 1"

    def test_regular_and_post_labels(self, nfl_calendar):
        assert fc.get_week_label("NFL", 2026, 2, 1) == "Week 1"
        assert fc.get_week_label("NFL", 2026, 3, 1) == "Wild Card"

    def test_unknown_week_falls_back(self, nfl_calendar):
        assert fc.get_week_label("NFL", 2026, 2, 99) == "Week 99"


class TestWeekDates:
    def test_uses_the_calendar_without_a_core_api_call(self, nfl_calendar):
        assert fc.get_week_dates("NFL", 2, 2026, season_type=1) == ("20260813", "20260819")
        assert nfl_calendar.get.call_count == 1  # the calendar only

    def test_season_type_selects_between_same_numbered_weeks(self, nfl_calendar):
        preseason = fc.get_week_dates("NFL", 1, 2026, season_type=1)
        regular = fc.get_week_dates("NFL", 1, 2026, season_type=2)
        assert preseason != regular
        assert preseason[0].startswith("202608")
        assert regular[0].startswith("202609")

    def test_a_past_season_is_not_answered_from_the_live_calendar(self, nfl_calendar):
        # The calendar only ever describes the current season, so a 2025 week must
        # reach the Core API rather than being handed 2026 dates. Here the Core
        # API call also fails, and (None, None) is the honest answer.
        assert fc.get_week_dates("NFL", 1, 2025, season_type=2) == (None, None)

    def test_failures_are_not_cached(self):
        # A single timeout must not degrade a week for the rest of the session.
        with patch.object(fc, "requests") as fake_requests:
            fake_requests.get.return_value.status_code = 503
            assert fc.get_week_dates("NFL", 1, 2026, season_type=2) == (None, None)
            assert ("NFL", 2026, 2, 1) not in fc._WEEK_DATE_CACHE
