"""Tests for live games in a single league's scores list.

Live Scores showed the current play for a live game; the league's own list
showed only the score and clock. The league list now reads the same play from
the scoreboard it already loaded, and a football week swaps its live games for
today's scoreboard, which the week-addressed one runs minutes behind.
"""

import os
import sys
from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import espn_api  # noqa: E402


def game(game_id, state, home_score="0", away_score="0", status_name="",
         start="2026-10-09T23:00Z"):
    return {
        "id": game_id,
        "state": state,
        "status_name": status_name,
        "date": start,
        "teams": [
            {"name": "Home", "score": home_score, "home_away": "home"},
            {"name": "Away", "score": away_score, "home_away": "away"},
        ],
    }


NOW = datetime(2026, 10, 10, 1, 0, tzinfo=timezone.utc)  # 9 pm ET on Friday the 9th


class TestFreshenLiveGames:
    def test_week_without_started_games_makes_no_request(self):
        week = [game("1", "pre", start="2026-10-10T23:00Z"), game("2", "post")]
        with patch.object(espn_api, "get_scores") as get_scores:
            assert espn_api.freshen_live_games("NCAAF", week, now=NOW) is week
        get_scores.assert_not_called()

    def test_games_under_way_come_from_their_days_board(self):
        week = [game("1", "in", home_score="6"), game("2", "pre", start="2026-10-10T23:00Z"),
                game("3", "post")]
        today = [game("1", "in", home_score="9")]
        with patch.object(espn_api, "get_scores", return_value=today) as get_scores:
            result = espn_api.freshen_live_games("NCAAF", week, now=NOW)
        get_scores.assert_called_once_with("NCAAF", date=date(2026, 10, 9))
        by_id = {g["id"]: g for g in result}
        assert by_id["1"]["teams"][0]["score"] == "9"
        assert by_id["2"] is week[1] and by_id["3"] is week[2]

    def test_late_game_after_midnight_uses_its_eastern_date(self):
        # 10:30 pm ET Saturday kickoff, still going at 1 am Sunday ET: ESPN
        # files it under Saturday, not the day it now is.
        week = [game("1", "in", start="2026-10-11T02:30Z")]
        now = datetime(2026, 10, 11, 5, 0, tzinfo=timezone.utc)
        with patch.object(espn_api, "get_scores", return_value=[]) as get_scores:
            espn_api.freshen_live_games("NCAAF", week, now=now)
        get_scores.assert_called_once_with("NCAAF", date=date(2026, 10, 10))

    def test_kicked_off_game_the_stale_board_calls_upcoming_is_freshened(self):
        week = [game("1", "pre", start="2026-10-09T23:30Z")]
        today = [game("1", "in", home_score="7")]
        with patch.object(espn_api, "get_scores", return_value=today):
            result = espn_api.freshen_live_games("NCAAF", week, now=NOW)
        assert espn_api.game_section(result[0]) == "in_progress"

    def test_games_on_two_days_fetch_each_day_once(self):
        week = [game("1", "in", start="2026-10-10T02:30Z"),  # Friday ET
                game("2", "in", start="2026-10-10T03:00Z"),  # Friday ET
                game("3", "in", start="2026-10-10T16:00Z")]  # Saturday ET
        now = datetime(2026, 10, 10, 17, 0, tzinfo=timezone.utc)
        with patch.object(espn_api, "get_scores", return_value=[]) as get_scores:
            espn_api.freshen_live_games("NCAAF", week, now=now)
        assert [c.kwargs["date"] for c in get_scores.call_args_list] == [
            date(2026, 10, 9), date(2026, 10, 10)]

    def test_game_that_finished_moves_to_completed(self):
        week = [game("1", "in"), game("2", "post")]
        with patch.object(espn_api, "get_scores", return_value=[game("1", "post")]):
            result = espn_api.freshen_live_games("NFL", week, now=NOW)
        assert [espn_api.game_section(g) for g in result] == ["completed", "completed"]

    def test_failure_keeps_the_week(self):
        week = [game("1", "in")]
        with patch.object(espn_api, "get_scores", side_effect=ConnectionError("down")):
            assert espn_api.freshen_live_games("NFL", week, now=NOW) is week

    def test_game_missing_from_its_days_board_keeps_its_week_version(self):
        week = [game("1", "in"), game("2", "in")]
        with patch.object(espn_api, "get_scores", return_value=[game("2", "in", home_score="3")]):
            result = {g["id"]: g for g in espn_api.freshen_live_games("NFL", week, now=NOW)}
        assert result["1"] is week[0]
        assert result["2"]["teams"][0]["score"] == "3"

    def test_unreadable_start_is_skipped(self):
        week = [game("1", "in", start="")]
        with patch.object(espn_api, "get_scores") as get_scores:
            assert espn_api.freshen_live_games("NFL", week, now=NOW) is week
        get_scores.assert_not_called()


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

    def test_mlb_gets_three_lines_with_short_names(self):
        comp = {"competitors": [
            {"homeAway": "home", "score": "2", "team": {"displayName": "Boston Red Sox"}},
            {"homeAway": "away", "score": "3", "team": {"displayName": "New York Yankees"}},
        ], "situation": {
            "onFirst": True, "balls": 1, "strikes": 2, "outs": 2,
            "batter": {"athlete": {"displayName": "Some Batter"}},
            "lastPlay": {"text": "Pitching change"},
        }}
        raw = {"id": "4", "state": "in", "status": "In Progress", "start_time": "Top 5th",
               "teams": [{"name": "Red Sox", "score": "2", "home_away": "home"},
                         {"name": "Yankees", "score": "3", "home_away": "away"}],
               "competitions": [comp]}
        lines = self.text("MLB", raw).split("\n")
        assert lines[0] == "Yankees 3 at Red Sox 2 (Top 5th)"
        assert lines[1] == "Runner on 1st | 1-2 count, 2 outs | At bat: Some Batter"
        assert lines[2] == "Last: Pitching change"


class TestRefreshKeepsTheGame:
    """F5 in a league list lands back on the selected game."""

    GAMES = [game(str(i), "post") for i in range(1, 5)]

    @pytest.fixture(autouse=True)
    def view(self):
        pytest.importorskip("PyQt6")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        self.app = QApplication.instance() or QApplication([])
        self.role = Qt.ItemDataRole.UserRole
        import scores
        with patch.object(scores, "_start_detached_thread"):
            self.view = scores.LeagueView(None, "NBA")
            yield

    def land(self, games=None):
        self.view._on_scores_loaded(self.view._scores_generation, None,
                                    self.GAMES if games is None else games, [])
        return self.view.scores_list.currentItem().data(self.role)

    def select(self, game_id):
        lst = self.view.scores_list
        row = next(i for i in range(lst.count()) if lst.item(i).data(self.role) == game_id)
        lst.setCurrentRow(row)

    def test_first_load_lands_on_the_first_row(self):
        assert self.land() is None  # the "Completed, 4 games" header

    def test_refresh_lands_on_the_selected_game(self):
        self.land()
        self.select("3")
        self.view.refresh()
        assert self.land() == "3"

    def test_game_gone_after_refresh_falls_back_to_the_top(self):
        self.land()
        self.select("3")
        self.view.refresh()
        assert self.land([g for g in self.GAMES if g["id"] != "3"]) is None

    def test_double_refresh_still_lands_on_the_game(self):
        self.land()
        self.select("3")
        self.view.refresh()
        self.view.refresh()  # the list now shows "Loading scores..."
        assert self.land() == "3"

    def test_failed_refresh_does_not_carry_to_the_next_day(self):
        self.land()
        self.select("3")
        self.view.refresh()
        import scores
        with patch.object(scores.QMessageBox, "warning"):  # modal; would block the test
            self.view._on_scores_error(self.view._scores_generation, "network down")
        self.view.load_scores()  # next day
        assert self.land() is None

    def test_day_change_during_refresh_lands_on_the_top(self):
        self.land()
        self.select("3")
        self.view.refresh()
        self.view.load_scores()
        assert self.land() is None


class TestLoaderFreshensFootballWeeksOnly:
    @pytest.fixture(autouse=True)
    def scores_module(self):
        pytest.importorskip("PyQt6")
        import scores
        self.scores = scores

    def run_loader(self, request):
        loader = self.scores.LeagueScoresLoader(1, "NFL", request)
        api = self.scores.ApiService
        with patch.object(api, "get_scores", return_value=[]), \
                patch.object(api, "get_news", return_value=[]), \
                patch.object(api, "freshen_live_games", return_value=[]) as freshen:
            loader.run()
        return freshen

    def test_week_request_is_freshened(self):
        self.run_loader(dict(week=6, season=2026, seasontype=2)).assert_called_once()

    def test_date_request_is_not(self):
        self.run_loader(dict(date=date(2026, 10, 9))).assert_not_called()
