"""Tests for the MLB wild card standings (espn_api.get_mlb_wildcard_standings).

The statsapi response is faked rather than fetched. These cover the parts where
a wrong answer misrepresents the playoff picture: which teams are shown as
already in, the order of the race, and the fact that MLB's published
`wildCardRank` is preserved rather than re-derived from win percentage.
"""

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import espn_api  # noqa: E402


def team_record(name, abbr, wins, losses, pct, division,
                wc_rank=None, wc_gb="-", streak="W1"):
    return {
        "team": {
            "id": abs(hash(name)) % 1000,
            "name": name,
            "teamName": name.split()[-1],
            "abbreviation": abbr,
            "division": {"name": division},
        },
        "leagueRecord": {"wins": wins, "losses": losses, "pct": pct},
        "streak": {"streakCode": streak},
        "wildCardRank": wc_rank,
        "wildCardGamesBack": wc_gb,
    }


# One league's worth of statsapi's `wildCardWithLeaders` shape: a wildCard record
# holding the race, plus one divisionLeaders record per division.
AL_RESPONSE = {
    "records": [
        {
            "standingsType": "wildCard",
            "league": {"id": 103},
            "teamRecords": [
                # Deliberately out of rank order, and with a tie on win
                # percentage between ranks 2 and 3, so the test fails if the
                # code re-sorts by record instead of honouring wildCardRank.
                team_record("Boston Red Sox", "BOS", 75, 63, ".543", "American League East",
                            wc_rank="3", wc_gb="0.5"),
                team_record("New York Yankees", "NYY", 78, 60, ".565", "American League East",
                            wc_rank="1", wc_gb="+8.5"),
                team_record("Seattle Mariners", "SEA", 75, 63, ".543", "American League West",
                            wc_rank="2", wc_gb="-"),
                team_record("Detroit Tigers", "DET", 63, 74, ".460", "American League Central",
                            wc_rank="4", wc_gb="6.0"),
            ],
        },
        {
            "standingsType": "divisionLeaders",
            "league": {"id": 103},
            "teamRecords": [team_record("Tampa Bay Rays", "TB", 82, 55, ".599",
                                        "American League East")],
        },
        {
            "standingsType": "divisionLeaders",
            "league": {"id": 103},
            "teamRecords": [team_record("Houston Astros", "HOU", 70, 68, ".507",
                                        "American League West")],
        },
    ]
}


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


def fetch(payload, status_code=200):
    with patch("espn_api.requests.get", return_value=FakeResponse(payload, status_code)):
        return espn_api.get_mlb_wildcard_standings()


def test_division_leaders_come_first_and_are_labelled():
    al = fetch(AL_RESPONSE)["AL"]
    leaders = [t for t in al if t["wc_position"] == "-"]

    assert [t["team_name"] for t in leaders] == ["Tampa Bay Rays", "Houston Astros"]
    assert al[:2] == leaders, "leaders must sort ahead of the race"
    assert leaders[0]["wc_status"] == "AL East leader"
    assert leaders[1]["wc_status"] == "AL West leader"


def test_race_keeps_mlb_rank_not_win_percentage():
    """Ranks 2 and 3 are tied on record; MLB's order must survive."""
    race = [t for t in fetch(AL_RESPONSE)["AL"] if t["wc_position"] != "-"]

    assert [t["wc_position"] for t in race] == ["1", "2", "3", "4"]
    assert [t["team_name"] for t in race] == [
        "New York Yankees", "Seattle Mariners", "Boston Red Sox", "Detroit Tigers",
    ]


def test_only_the_top_three_are_marked_as_holding_a_spot():
    race = [t for t in fetch(AL_RESPONSE)["AL"] if t["wc_position"] != "-"]

    assert [t["wc_status"] for t in race[:3]] == ["Wild card 1", "Wild card 2", "Wild card 3"]
    assert race[3]["wc_status"] == "", "4th place must not read as being in"


def test_wildcard_games_back_is_used_not_division_games_back():
    race = {t["team_name"]: t for t in fetch(AL_RESPONSE)["AL"] if t["wc_position"] != "-"}

    assert race["New York Yankees"]["games_back"] == "+8.5"
    assert race["Seattle Mariners"]["games_back"] == "-"
    # Division leaders have no wild card deficit to show.
    leaders = [t for t in fetch(AL_RESPONSE)["AL"] if t["wc_position"] == "-"]
    assert all(t["games_back"] == "-" for t in leaders)


def test_row_carries_the_fields_the_standings_table_reads():
    row = fetch(AL_RESPONSE)["AL"][0]

    for key in ("team_name", "wins", "losses", "win_percentage", "games_back",
                "streak", "division", "wc_position", "wc_status"):
        assert key in row, f"missing {key}"
    assert row["wins"] == 82 and row["losses"] == 55
    assert row["division"] == "AL East"
    assert row["streak"] == "W1"


def test_league_with_no_records_is_omitted():
    result = fetch(AL_RESPONSE)
    assert "AL" in result
    assert "NL" not in result, "an empty league should not produce an empty tab"


@pytest.mark.parametrize("payload,status", [
    ({"records": []}, 200),
    ({}, 200),
    ({"records": []}, 500),
])
def test_failures_return_empty_rather_than_raising(payload, status):
    assert fetch(payload, status) == {}


def test_network_error_returns_empty():
    with patch("espn_api.requests.get", side_effect=OSError("no network")):
        assert espn_api.get_mlb_wildcard_standings() == {}


def test_unknown_league_id_is_ignored():
    payload = {"records": [dict(AL_RESPONSE["records"][0], league={"id": 999})]}
    assert fetch(payload) == {}
