"""Tests for live games in a single league's scores list.

Live Scores showed the current play for a live game; the league's own list
showed only the score and clock. The league list now reads the same play from
the scoreboard it already loaded, and a football week swaps its live games for
today's scoreboard, which the week-addressed one runs minutes behind.
"""

import os
import sys
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import espn_api  # noqa: E402


def game(game_id, state, home_score="0", away_score="0", status_name=""):
    return {
        "id": game_id,
        "state": state,
        "status_name": status_name,
        "date": "2026-10-09T23:00Z",
        "teams": [
            {"name": "Home", "score": home_score, "home_away": "home"},
            {"name": "Away", "score": away_score, "home_away": "away"},
        ],
    }


class TestFreshenLiveGames:
    def test_week_without_live_games_makes_no_request(self):
        week = [game("1", "pre"), game("2", "post")]
        with patch.object(espn_api, "get_scores") as get_scores:
            assert espn_api.freshen_live_games("NCAAF", week) is week
        get_scores.assert_not_called()

    def test_live_games_come_from_todays_scoreboard(self):
        week = [game("1", "in", home_score="6"), game("2", "pre"), game("3", "post")]
        today = [game("1", "in", home_score="9")]
        with patch.object(espn_api, "get_scores", return_value=today) as get_scores:
            result = espn_api.freshen_live_games("NCAAF", week, today=date(2026, 10, 9))
        get_scores.assert_called_once_with("NCAAF", date=date(2026, 10, 9))
        by_id = {g["id"]: g for g in result}
        assert by_id["1"]["teams"][0]["score"] == "9"
        assert by_id["2"] is week[1] and by_id["3"] is week[2]

    def test_game_that_finished_moves_to_completed(self):
        week = [game("1", "in"), game("2", "post")]
        today = [game("1", "post")]
        with patch.object(espn_api, "get_scores", return_value=today):
            result = espn_api.freshen_live_games("NFL", week, today=date(2026, 10, 9))
        assert [espn_api.game_section(g) for g in result] == ["completed", "completed"]

    def test_failure_keeps_the_week(self):
        week = [game("1", "in")]
        with patch.object(espn_api, "get_scores", side_effect=ConnectionError("down")):
            assert espn_api.freshen_live_games("NFL", week) is week

    def test_live_game_missing_from_today_keeps_its_week_version(self):
        # A late game ESPN files under tomorrow's date, say.
        week = [game("1", "in")]
        with patch.object(espn_api, "get_scores", return_value=[]):
            assert espn_api.freshen_live_games("NFL", week)[0] is week[0]


class TestLeagueViewLiveText:
    """LeagueView._live_game_text, called with a stand-in for the view."""

    @pytest.fixture(autouse=True)
    def scores_module(self):
        pytest.importorskip("PyQt6")
        import scores
        self.scores = scores

    def text(self, league, game_raw):
        return self.scores.LeagueView._live_game_text(SimpleNamespace(league=league), game_raw)

    def football_game(self, situation):
        comp = {
            "status": {"displayClock": "8:30", "period": 4},
            "competitors": [
                {"homeAway": "home", "score": "20",
                 "team": {"id": "97", "displayName": "Louisville Cardinals", "abbreviation": "LOU"}},
                {"homeAway": "away", "score": "35",
                 "team": {"id": "52", "displayName": "Florida State Seminoles", "abbreviation": "FSU"}},
            ],
            "situation": situation,
        }
        return {
            "id": "1", "name": "FSU at LOU", "state": "in", "status": "In Progress",
            "start_time": "8:30 - 4th",
            "teams": [
                {"name": "Louisville Cardinals", "score": "20", "home_away": "home"},
                {"name": "Florida State Seminoles", "score": "35", "home_away": "away"},
            ],
            "competitions": [comp],
        }

    def test_football_gets_play_and_situation_with_the_clock_once(self):
        raw = self.football_game({
            "lastPlay": {"text": "J.Smith pass complete to K.Jones for 12 yards"},
            "possession": "52", "downDistanceText": "1st & 10 at LOU 40",
        })
        lines = self.text("NCAAF", raw).split("\n")
        assert lines[0] == ("Florida State Seminoles 35 at Louisville Cardinals 20"
                            " | J.Smith pass complete to K.Jones for 12 yards")
        assert lines[1] == "8:30 Q4 | FSU ball | 1st & 10 at LOU 40"

    def test_no_situation_leaves_the_usual_text(self):
        assert self.text("NCAAF", self.football_game({})) is None

    def test_nfl_uses_the_lists_short_team_names(self):
        raw = self.football_game({"lastPlay": {"text": "Kickoff"}, "possession": "52"})
        raw["teams"][0]["name"], raw["teams"][1]["name"] = "Cardinals", "Seminoles"
        first = self.text("NFL", raw).split("\n")[0]
        assert first.startswith("Seminoles 35 at Cardinals 20")

    def test_other_leagues_add_the_last_play(self):
        raw = {
            "id": "2", "name": "Ducks at Jets", "state": "in", "status": "In Progress",
            "start_time": "18:11 - 3rd",
            "teams": [{"name": "Jets", "score": "0", "home_away": "home"},
                      {"name": "Ducks", "score": "2", "home_away": "away"}],
            "competitions": [{"situation": {"lastPlay": {"text": "Shot on goal by Someone"}}}],
        }
        assert self.text("NHL", raw).endswith(" | Shot on goal by Someone")

    def test_game_without_competitions_leaves_the_usual_text(self):
        raw = {"id": "3", "state": "in", "teams": [], "competitions": []}
        assert self.text("NBA", raw) is None
