"""Tests for how GameData renders a game in the scores list.

The rule these all circle: ESPN sends score "0" for both teams on any game
that never got underway, so the score is only worth showing once the game has
actually been played. Getting that wrong has produced two separate bugs — a
slate of "0 at 0" scheduled games, and postponed games that read as though
they had finished nil-nil.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.game import GameData


TEAMS = [
    {"name": "Guardians", "score": "0", "record": "59-62", "home_away": "away"},
    {"name": "Tigers", "score": "0", "record": "59-61", "home_away": "home"},
]


def make_game(status_name, status, teams=None, start_time=None):
    return GameData({
        "name": "Guardians at Tigers",
        "status": status,
        "status_name": status_name,
        "start_time": start_time if start_time is not None else status,
        "teams": teams if teams is not None else TEAMS,
    }, "MLB")


class TestNeverPlayedGames(unittest.TestCase):
    """Scheduled, postponed and cancelled games show records, not 0-0."""

    def test_scheduled_shows_records(self):
        text = make_game("STATUS_SCHEDULED", "Scheduled", start_time="7:05 PM").get_display_text()
        self.assertIn("Guardians (59-62)", text)
        self.assertIn("Tigers (59-61)", text)

    def test_postponed_shows_records_not_a_score(self):
        text = make_game("STATUS_POSTPONED", "Postponed").get_display_text()
        self.assertIn("Guardians (59-62)", text)
        self.assertNotIn("Guardians 0", text)
        self.assertIn("Postponed", text)

    def test_cancelled_shows_records_not_a_score(self):
        for name in ("STATUS_CANCELED", "STATUS_CANCELLED"):
            with self.subTest(status_name=name):
                text = make_game(name, "Canceled").get_display_text()
                self.assertNotIn("Guardians 0", text)
                self.assertIn("(59-62)", text)

    def test_team_name_alone_when_no_record(self):
        """Season openers have no record yet; don't show an empty parenthetical."""
        teams = [dict(t, record="") for t in TEAMS]
        text = make_game("STATUS_SCHEDULED", "Scheduled", teams=teams).get_display_text()
        self.assertIn("Guardians at Tigers", text)
        self.assertNotIn("()", text)
        self.assertNotIn("Guardians 0", text)


class TestPlayedGames(unittest.TestCase):
    """Games that were actually played keep their scores."""

    def test_final_keeps_score(self):
        teams = [dict(TEAMS[0], score="5"), dict(TEAMS[1], score="3")]
        text = make_game("STATUS_FINAL", "Final", teams=teams).get_display_text()
        self.assertIn("Guardians 5", text)
        self.assertIn("Tigers 3", text)

    def test_suspended_keeps_partial_score(self):
        """A suspended game was halted mid-play — its score is real."""
        teams = [dict(TEAMS[0], score="3"), dict(TEAMS[1], score="2")]
        text = make_game("STATUS_SUSPENDED", "Suspended", teams=teams).get_display_text()
        self.assertIn("Guardians 3", text)
        self.assertIn("Tigers 2", text)
        self.assertNotIn("(59-62)", text)


class TestStatusNameFallback(unittest.TestCase):
    """status_name is preferred, but callers predating it still work."""

    def test_falls_back_to_description(self):
        game = GameData({
            "name": "x", "status": "Postponed", "start_time": "Postponed", "teams": TEAMS,
        }, "MLB")
        self.assertTrue(game.was_never_played)
        self.assertNotIn("Guardians 0", game.get_display_text())

    def test_status_name_wins_over_description(self):
        """ESPN's stable name is authoritative when the two disagree."""
        game = make_game("STATUS_FINAL", "Postponed",
                         teams=[dict(TEAMS[0], score="5"), dict(TEAMS[1], score="3")])
        self.assertFalse(game.was_never_played)
        self.assertIn("Guardians 5", game.get_display_text())

    def test_unknown_status_is_treated_as_played(self):
        game = make_game("STATUS_RAIN_DELAY", "Rain Delay")
        self.assertFalse(game.was_never_played)


if __name__ == '__main__':
    unittest.main()
