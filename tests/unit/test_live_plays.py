"""Tests for the current-play text a league's scores list shows for live games.

The All Scores view always fetched each live game's summary to show the
current play; a single league's view showed only the score and clock. Both now
go through live_game_update(), and the league view gets its plays from
get_live_plays(). These pin which games get a fetch, what comes back, and the
clock that travels with the play: the week-addressed football scoreboard lags
the summary by minutes, so the clock must come from the same fetch as the play.
"""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import espn_api  # noqa: E402


def scoreboard_game(game_id, state, short_detail, situation=None, description=None):
    """A get_scores()-shaped game dict with the raw competition attached."""
    comp = {
        "status": {"type": {
            "state": state,
            "shortDetail": short_detail,
            "description": description or {"in": "In Progress", "pre": "Scheduled", "post": "Final"}[state],
        }},
        "competitors": [
            {"homeAway": "home", "score": "7", "team": {"displayName": "Home Team"}},
            {"homeAway": "away", "score": "3", "team": {"displayName": "Away Team"}},
        ],
    }
    if situation is not None:
        comp["situation"] = situation
    return {"id": game_id, "name": f"Game {game_id}", "competitions": [comp]}


def summary(short_detail):
    return {"header": {"competitions": [{"status": {"type": {"shortDetail": short_detail}}}]}}


FOOTBALL_PLAY = "Away Team 3 at Home Team 7 | Shotgun pass complete\n10:00 Q2 | 2nd & 5 | HOME: 4 plays"


class TestGetLivePlays:
    def test_only_live_games_are_fetched(self):
        games = [
            scoreboard_game("1", "in", "10:05 - 2nd"),
            scoreboard_game("2", "pre", "10/17 - 7:30 PM EDT"),
            scoreboard_game("3", "post", "Final"),
        ]
        with patch.object(espn_api, "get_game_details", return_value=summary("10:00 - 2nd")) as details, \
                patch.object(espn_api, "extract_recent_play", return_value=FOOTBALL_PLAY):
            result = espn_api.get_live_plays("NCAAF", games)
        details.assert_called_once()
        assert details.call_args[0] == ("NCAAF", "1")
        assert list(result) == ["1"]

    def test_clock_comes_from_the_summary_not_the_stale_scoreboard(self):
        games = [scoreboard_game("1", "in", "0:36 - 1st")]
        with patch.object(espn_api, "get_game_details", return_value=summary("14:16 - 2nd")), \
                patch.object(espn_api, "extract_recent_play", return_value=FOOTBALL_PLAY):
            result = espn_api.get_live_plays("NCAAF", games)
        assert result["1"] == {"play": FOOTBALL_PLAY, "status": "14:16 - 2nd"}

    def test_scoreboard_clock_is_kept_when_summary_has_none(self):
        games = [scoreboard_game("1", "in", "5:00 - 3rd")]
        with patch.object(espn_api, "get_game_details", return_value={}), \
                patch.object(espn_api, "extract_recent_play", return_value="Timeout Home Team, clock 5:00"):
            result = espn_api.get_live_plays("NBA", games)
        assert result["1"]["status"] == "5:00 - 3rd"

    def test_in_progress_description_counts_as_live(self):
        # Some feeds leave state empty; All Scores also accepts "progress".
        games = [scoreboard_game("1", "in", "2:00 - 1st", description="In Progress")]
        games[0]["competitions"][0]["status"]["type"]["state"] = ""
        with patch.object(espn_api, "get_game_details", return_value={}), \
                patch.object(espn_api, "extract_recent_play", return_value="A long enough play description"):
            assert "1" in espn_api.get_live_plays("NHL", games)

    def test_play_no_more_informative_than_the_clock_is_dropped(self):
        games = [scoreboard_game("1", "in", "Halftime")]
        with patch.object(espn_api, "get_game_details", return_value=summary("Halftime")), \
                patch.object(espn_api, "extract_recent_play", return_value="Half"):
            assert espn_api.get_live_plays("NBA", games) == {}

    def test_one_failing_game_does_not_lose_the_others(self):
        games = [scoreboard_game("1", "in", "1:00 - 1st"), scoreboard_game("2", "in", "2:00 - 1st")]

        def details(league, game_id, **kwargs):
            if game_id == "1":
                raise ConnectionError("summary unavailable")
            return summary("2:00 - 1st")

        with patch.object(espn_api, "get_game_details", side_effect=details), \
                patch.object(espn_api, "extract_recent_play", return_value=FOOTBALL_PLAY):
            result = espn_api.get_live_plays("NFL", games)
        assert list(result) == ["2"]

    def test_no_games_makes_no_requests(self):
        with patch.object(espn_api, "get_game_details") as details:
            assert espn_api.get_live_plays("NFL", []) == {}
            assert espn_api.get_live_plays("NFL", None) == {}
        details.assert_not_called()

    def test_game_without_competitions_is_skipped(self):
        with patch.object(espn_api, "get_game_details") as details:
            assert espn_api.get_live_plays("NFL", [{"id": "1", "competitions": []}]) == {}
        details.assert_not_called()


class TestMlbUsesScoreboardSituation:
    SITUATION = {
        "onFirst": True, "onSecond": False, "onThird": True,
        "balls": 2, "strikes": 1, "outs": 1,
        "batter": {"athlete": {"displayName": "Some Batter"}},
        "lastPlay": {"text": "Single to left"},
    }

    def test_situation_on_the_event_needs_no_summary_fetch(self):
        games = [scoreboard_game("1", "in", "Top 5th", situation=self.SITUATION)]
        with patch.object(espn_api, "get_game_details") as details:
            result = espn_api.get_live_plays("MLB", games)
        details.assert_not_called()
        lines = result["1"]["play"].split("\n")
        assert lines[0] == "Away Team 3 at Home Team 7"
        assert lines[1] == "Runners on 1st and 3rd | 2-1 count, 1 out | At bat: Some Batter"
        assert lines[2] == "Last: Single to left"
        assert result["1"]["status"] == "Top 5th"

    def test_missing_situation_falls_back_to_the_summary(self):
        games = [scoreboard_game("1", "in", "Top 5th")]
        with patch.object(espn_api, "get_game_details", return_value=summary("Mid 5th")) as details, \
                patch.object(espn_api, "_extract_generic_recent_play", return_value="P: Pitcher | AB: Batter | Count: 0-0"):
            result = espn_api.get_live_plays("MLB", games)
        details.assert_called_once()
        assert result["1"]["status"] == "Mid 5th"


class TestAllScoresPath:
    def test_live_game_update_returns_no_play_when_detail_adds_nothing(self):
        game = scoreboard_game("1", "in", "End of 2nd Period")
        with patch.object(espn_api, "get_game_details", return_value={}), \
                patch.object(espn_api, "extract_recent_play", return_value=None):
            assert espn_api.live_game_update("NHL", game, "End of 2nd Period") == (None, "End of 2nd Period")

    def test_summary_is_fetched_without_the_hockey_web_page_and_with_a_timeout(self):
        game = scoreboard_game("1", "in", "5:00 - 2nd")
        with patch.object(espn_api, "get_game_details", return_value={}) as details, \
                patch.object(espn_api, "extract_recent_play", return_value="Goal scored by somebody"):
            espn_api.live_game_update("NHL", game, "5:00 - 2nd")
        details.assert_called_once_with("NHL", "1", include_web_plays=False,
                                        timeout=espn_api.LIVE_PLAY_TIMEOUT)

    def test_mlb_fallback_does_not_refetch_the_scoreboard(self):
        game = scoreboard_game("1", "in", "Top 5th")  # no situation on the event
        with patch.object(espn_api, "get_game_details", return_value={}), \
                patch.object(espn_api, "requests") as fake_requests:
            espn_api.live_game_update("MLB", game, "Top 5th")
        fake_requests.get.assert_not_called()


def all_scores_board(*events):
    return {"events": list(events)}


class TestGetLiveScoresAllSports:
    """The All Scores path, which now shares live_game_update with the league view."""

    def run(self, update):
        event = scoreboard_game("1", "in", "3:00 - 1st")
        event["competitions"][0]["competitors"][0]["team"]["displayName"] = "Home Team"

        def fake_get(url, **kwargs):
            class Resp:
                status_code = 200
                def json(self):
                    return all_scores_board(event) if "football/nfl" in url else {"events": []}
            return Resp()

        with patch.object(espn_api, "requests") as fake_requests, \
                patch.object(espn_api, "live_game_update", side_effect=update):
            fake_requests.get.side_effect = fake_get
            return [g for g in espn_api.get_live_scores_all_sports() if g["league"] == "NFL"]

    def test_play_and_summary_clock_are_used(self):
        games = self.run(lambda league, event, status: (FOOTBALL_PLAY, "2:40 - 1st"))
        assert games[0]["recent_play"] == FOOTBALL_PLAY
        assert games[0]["status"] == "2:40 - 1st"

    def test_no_play_falls_back_to_the_clock(self):
        games = self.run(lambda league, event, status: (None, status))
        assert games[0]["recent_play"] == "3:00 - 1st"

    def test_failed_detail_fetch_falls_back_to_the_scoreboard_clock(self):
        def boom(league, event, status):
            raise TimeoutError("summary timed out")
        games = self.run(boom)
        assert games[0]["recent_play"] == "3:00 - 1st"
        assert games[0]["status"] == "3:00 - 1st"

    def test_teams_carry_home_and_away(self):
        games = self.run(lambda league, event, status: (None, status))
        assert {t["home_away"] for t in games[0]["teams"]} == {"home", "away"}


class TestIsLiveGame:
    def test_missing_or_null_status_is_not_live(self):
        assert not espn_api.is_live_game({"competitions": [{"status": None}]})
        assert not espn_api.is_live_game({"competitions": [{"status": {"type": None}}]})
        assert not espn_api.is_live_game({"competitions": [{"status": {"type": {"state": None}}}]})
        assert not espn_api.is_live_game({})
