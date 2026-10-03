"""Tests for the order games appear in on a league's scores list.

ESPN returns a scoreboard in kickoff order, so a college football Saturday
mixes finals, live games and evening kickoffs together. get_scores puts games
in progress first, then upcoming, then completed, then postponed or cancelled,
matching the sections the iOS app shows.
"""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import espn_api  # noqa: E402


def event(eid, state, date, name="STATUS_X"):
    return {
        "id": eid,
        "name": f"Game {eid}",
        "date": date,
        "competitions": [{
            "status": {"type": {"state": state, "name": name, "description": state}},
            "competitors": [],
        }],
    }


def scores_for(events, league="NFL"):
    with patch.object(espn_api, "requests") as fake_requests:
        fake_requests.get.return_value.status_code = 200
        fake_requests.get.return_value.json.return_value = {"events": events}
        return espn_api.get_scores(league, week=5, season=2026)


class TestScoreOrdering:
    def test_live_then_upcoming_then_final(self):
        games = scores_for([
            event("final-noon", "post", "2026-10-03T16:00Z"),
            event("live-330", "in", "2026-10-03T19:30Z"),
            event("upcoming-7", "pre", "2026-10-03T23:00Z"),
            event("final-11", "post", "2026-10-03T15:00Z"),
            event("live-3", "in", "2026-10-03T19:00Z"),
            event("upcoming-1030", "pre", "2026-10-04T02:30Z"),
        ])
        assert [g["id"] for g in games] == [
            "live-3", "live-330", "upcoming-7", "upcoming-1030", "final-11", "final-noon",
        ]

    def test_state_and_date_are_kept_on_each_game(self):
        game = scores_for([event("1", "pre", "2026-10-03T23:00Z")])[0]
        assert game["state"] == "pre"
        assert game["date"] == "2026-10-03T23:00Z"

    def test_postponed_and_cancelled_go_last_whatever_their_state(self):
        # ESPN reports a postponed game as "pre" and a cancelled one as "post".
        games = scores_for([
            event("ppd", "pre", "2026-10-03T16:00Z", name="STATUS_POSTPONED"),
            event("final", "post", "2026-10-03T17:00Z", name="STATUS_FINAL"),
            event("canc", "post", "2026-10-03T15:00Z", name="STATUS_CANCELED"),
            event("next", "pre", "2026-10-03T23:00Z", name="STATUS_SCHEDULED"),
        ])
        assert [g["id"] for g in games] == ["next", "final", "canc", "ppd"]

    def test_suspended_game_counts_as_in_progress(self):
        game = {"state": "post", "status_name": "STATUS_SUSPENDED"}
        assert espn_api.game_section(game) == "in_progress"

    def test_missing_state_counts_as_upcoming(self):
        assert espn_api.game_section({}) == "upcoming"

    def test_same_section_and_time_keeps_espn_order(self):
        games = espn_api.sort_games_by_section([
            {"id": "x", "state": "pre", "date": "2026-10-03T16:00Z"},
            {"id": "y", "state": "pre", "date": "2026-10-03T16:00Z"},
        ])
        assert [g["id"] for g in games] == ["x", "y"]
