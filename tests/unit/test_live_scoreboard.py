"""Tests for what Live Scores reads straight from ESPN scoreboards.

Live Scores used to fetch a full game summary per live game for its latest
play. It now builds that line from the scoreboard's situation block, and shows
golf as tournaments with leaders rather than as two-team games.
"""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import espn_api  # noqa: E402


def rounds(*values):
    return [{"period": i + 1, "displayValue": v} for i, v in enumerate(values)]


class TestGolfTotalToPar:
    def test_round_in_progress_is_included(self):
        # ESPN's score field said -3 here: it leaves out the round being played.
        golfer = {"score": "-3", "linescores": rounds("+1", "-4", "-8")}
        assert espn_api.golf_total_to_par(golfer) == "-11"

    def test_unstarted_round_counts_as_nothing(self):
        assert espn_api.golf_total_to_par({"linescores": rounds("-5", "-7", "-")}) == "-12"

    def test_even_par(self):
        assert espn_api.golf_total_to_par({"linescores": rounds("+2", "E", "-2")}) == "E"

    def test_over_par_keeps_its_sign(self):
        assert espn_api.golf_total_to_par({"linescores": rounds("+3", "+1")}) == "+4"

    def test_cut_and_withdrawn_are_kept(self):
        for status in ("CUT", "WD", "DQ"):
            golfer = {"score": status, "linescores": rounds("+3", "+2")}
            assert espn_api.golf_total_to_par(golfer) == status

    def test_falls_back_to_score_without_rounds(self):
        assert espn_api.golf_total_to_par({"score": "-6"}) == "-6"


def golf_scoreboard(state, golfers):
    return {"events": [{
        "name": "Bank of Utah Championship",
        "competitions": [{
            "status": {"type": {"state": state, "detail": "Round 3 - In Progress"}},
            "competitors": [
                {"order": i + 1, "athlete": {"displayName": name}, "linescores": rounds(*r)}
                for i, (name, r) in enumerate(golfers)
            ],
        }],
    }]}


def live_golf(board):
    with patch.object(espn_api, "requests") as fake_requests:
        fake_requests.get.return_value.status_code = 200
        fake_requests.get.return_value.json.return_value = board
        return espn_api.get_live_golf_tournament("PGA")


class TestLiveGolfTournament:
    def test_leaders_share_tied_positions(self):
        t = live_golf(golf_scoreboard("in", [
            ("Kevin Streelman", ("-7", "-6", "-6")),
            ("Austin Smotherman", ("-6", "-7", "-6")),
            ("Doug Ghim", ("-6", "-6", "-6")),
        ]))
        assert t["name"] == "Bank of Utah Championship"
        assert t["tour_name"] == "PGA Tour"
        assert t["leaders"] == [
            ("T1", "Kevin Streelman", "-19"),
            ("T1", "Austin Smotherman", "-19"),
            ("3", "Doug Ghim", "-18"),
        ]

    def test_no_tournament_unless_in_progress(self):
        assert live_golf(golf_scoreboard("post", [("A", ("-1",))])) is None


def football_comp(situation):
    return {
        "status": {"displayClock": "8:02", "period": 4},
        "situation": situation,
        "competitors": [
            {"homeAway": "home", "score": "13",
             "team": {"id": "2", "displayName": "Hampton Pirates", "abbreviation": "HAMP"}},
            {"homeAway": "away", "score": "27",
             "team": {"id": "1", "displayName": "Howard Bison", "abbreviation": "HOW"}},
        ],
    }


class TestFootballScoreboardDetail:
    def test_two_lines_from_the_situation(self):
        text = espn_api.scoreboard_live_detail("NCAAF", football_comp({
            "possession": "1", "isRedZone": True,
            "downDistanceText": "1st & Goal at HAMP 4",
            "lastPlay": {"text": "E.James rush right for 17 yards"},
        }))
        line1, line2 = text.split("\n")
        assert line1 == "Howard Bison 27 (RZ) at Hampton Pirates 13 | E.James rush right for 17 yards"
        assert line2 == "8:02 Q4 | HOW ball | 1st & Goal at HAMP 4"

    def test_no_situation_means_no_detail(self):
        # Halftime: the caller falls back to the status text.
        assert espn_api.scoreboard_live_detail("NFL", football_comp({})) is None
