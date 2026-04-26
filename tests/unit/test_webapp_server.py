"""
Unit and integration tests for webapp/server.py.
Run with: pytest tests/unit/test_webapp_server.py -v
"""
import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Ensure the project root is on the path so server.py can find espn_api
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def client():
    """Flask test client with espn_api stubbed out."""
    # Patch espn_api before importing server so the sys.path trick doesn't
    # attempt a real network call at import time.
    mock_espn = MagicMock()
    with patch.dict(sys.modules, {"espn_api": mock_espn}):
        # Import fresh so the patched module is used
        import importlib
        import webapp.server as srv
        importlib.reload(srv)
        srv.app.config["TESTING"] = True
        with srv.app.test_client() as c:
            yield c, mock_espn


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_raw_game(away_score="3", home_score="5", status="Final", start_time="7:00 PM ET",
                  away_name="Visitors", home_name="Home Team",
                  away_id="10", home_id="20"):
    """Build a minimal raw game dict as returned by espn_api.get_scores()."""
    return {
        "id": "401234",
        "name": f"{away_name} at {home_name}",
        "start_time": start_time,
        "status": status,
        "teams": [
            {"name": away_name, "abbreviation": "VIS", "score": away_score, "record": "10-5", "home_away": "away"},
            {"name": home_name, "abbreviation": "HME", "score": home_score, "record": "8-7",  "home_away": "home"},
        ],
        "competitions": [
            {
                "broadcasts": [{"names": ["ESPN", "ABC"]}],
                "competitors": [
                    {"homeAway": "away", "team": {"id": away_id}},
                    {"homeAway": "home", "team": {"id": home_id}},
                ],
            }
        ],
    }


# ── normalize_game tests ──────────────────────────────────────────────────────

class TestNormalizeGame:
    """Tests for the normalize_game() helper in server.py."""

    def setup_method(self):
        mock_espn = MagicMock()
        with patch.dict(sys.modules, {"espn_api": mock_espn}):
            import importlib
            import webapp.server as srv
            importlib.reload(srv)
            self.normalize = srv.normalize_game

    def test_extracts_away_home_names(self):
        raw = make_raw_game(away_name="Jets", home_name="Patriots")
        result = self.normalize(raw)
        assert result["away_team"] == "Jets"
        assert result["home_team"] == "Patriots"

    def test_extracts_scores(self):
        raw = make_raw_game(away_score="14", home_score="21")
        result = self.normalize(raw)
        assert result["away_score"] == "14"
        assert result["home_score"] == "21"

    def test_extracts_status(self):
        raw = make_raw_game(status="In Progress")
        result = self.normalize(raw)
        assert result["status"] == "In Progress"

    def test_extracts_broadcast(self):
        raw = make_raw_game()
        result = self.normalize(raw)
        assert "ESPN" in result["broadcast"]
        assert "ABC" in result["broadcast"]

    def test_extracts_team_ids(self):
        raw = make_raw_game(away_id="42", home_id="77")
        result = self.normalize(raw)
        assert result["away_team_id"] == "42"
        assert result["home_team_id"] == "77"

    def test_handles_missing_teams(self):
        raw = {"id": "1", "name": "", "start_time": "", "status": "", "teams": [], "competitions": []}
        result = self.normalize(raw)
        assert result["away_team"] == ""
        assert result["home_team"] == ""

    def test_handles_missing_broadcast(self):
        raw = make_raw_game()
        raw["competitions"][0].pop("broadcasts")
        result = self.normalize(raw)
        assert result["broadcast"] == ""

    def test_fallback_when_no_home_away_flag(self):
        """If home_away is missing, first team is away and last is home."""
        raw = make_raw_game()
        for t in raw["teams"]:
            del t["home_away"]
        result = self.normalize(raw)
        # Should not crash; away defaults to teams[0]
        assert "away_team" in result


# ── normalize_soccer_event tests ─────────────────────────────────────────────

class TestNormalizeSoccerEvent:
    def setup_method(self):
        mock_espn = MagicMock()
        with patch.dict(sys.modules, {"espn_api": mock_espn}):
            import importlib
            import webapp.server as srv
            importlib.reload(srv)
            self.normalize = srv.normalize_soccer_event

    def _make_event(self):
        return {
            "id": "999",
            "name": "Arsenal vs Chelsea",
            "competitions": [{
                "status": {"type": {"description": "Final", "shortDetail": "FT"}},
                "broadcasts": [{"names": ["Peacock"]}],
                "competitors": [
                    {"homeAway": "away", "team": {"name": "Arsenal",  "id": "359"}, "score": "2"},
                    {"homeAway": "home", "team": {"name": "Chelsea",  "id": "363"}, "score": "1"},
                ],
            }]
        }

    def test_extracts_team_names(self):
        result = self.normalize(self._make_event())
        assert result["away_team"] == "Arsenal"
        assert result["home_team"] == "Chelsea"

    def test_extracts_scores(self):
        result = self.normalize(self._make_event())
        assert result["away_score"] == "2"
        assert result["home_score"] == "1"

    def test_extracts_status(self):
        result = self.normalize(self._make_event())
        assert result["status"] == "Final"

    def test_returns_none_on_empty_competitions(self):
        event = {"id": "1", "name": "", "competitions": []}
        assert self.normalize(event) is None


# ── Flask endpoint tests ─────────────────────────────────────────────────────

class TestScoresEndpoint:
    def test_scores_returns_normalized_list(self, client):
        flask_client, mock_espn = client
        mock_espn.get_scores.return_value = [make_raw_game()]
        resp = flask_client.get("/api/scores/MLB?date=20250426")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)
        assert len(data) == 1
        game = data[0]
        assert "away_team" in game
        assert "home_team" in game
        assert "away_score" in game
        assert "broadcast" in game

    def test_scores_calls_espn_with_uppercase_key(self, client):
        flask_client, mock_espn = client
        mock_espn.get_scores.return_value = []
        flask_client.get("/api/scores/nba")
        mock_espn.get_scores.assert_called_once()
        call_args = mock_espn.get_scores.call_args
        assert call_args[0][0] == "NBA"

    def test_scores_passes_date_param(self, client):
        flask_client, mock_espn = client
        mock_espn.get_scores.return_value = []
        flask_client.get("/api/scores/MLB?date=20251001")
        call_args = mock_espn.get_scores.call_args
        assert call_args[1].get("date") is not None

    def test_scores_invalid_date_returns_empty(self, client):
        flask_client, mock_espn = client
        mock_espn.get_scores.return_value = []
        resp = flask_client.get("/api/scores/MLB?date=notadate")
        assert resp.status_code == 200

    def test_scores_exception_returns_500(self, client):
        flask_client, mock_espn = client
        mock_espn.get_scores.side_effect = RuntimeError("ESPN down")
        resp = flask_client.get("/api/scores/MLB")
        assert resp.status_code == 500


class TestStandingsEndpoint:
    def test_standings_returns_list(self, client):
        flask_client, mock_espn = client
        mock_espn.get_standings.return_value = [
            {"team_name": "Yankees", "wins": 90, "losses": 72, "division": "AL East", "win_percentage": ".556"}
        ]
        resp = flask_client.get("/api/standings/MLB")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)
        assert data[0]["team_name"] == "Yankees"

    def test_standings_uppercase_key(self, client):
        flask_client, mock_espn = client
        mock_espn.get_standings.return_value = []
        flask_client.get("/api/standings/nfl")
        mock_espn.get_standings.assert_called_with("NFL")


class TestNewsEndpoint:
    def test_news_default_limit(self, client):
        flask_client, mock_espn = client
        mock_espn.get_news.return_value = []
        flask_client.get("/api/news/MLB")
        call_kwargs = mock_espn.get_news.call_args[1]
        assert call_kwargs.get("limit") == 10

    def test_news_custom_limit_capped_at_50(self, client):
        flask_client, mock_espn = client
        mock_espn.get_news.return_value = []
        flask_client.get("/api/news/MLB?limit=999")
        call_kwargs = mock_espn.get_news.call_args[1]
        assert call_kwargs.get("limit") <= 50


class TestGameDetailEndpoint:
    def test_game_detail_returns_raw_data(self, client):
        flask_client, mock_espn = client
        mock_espn.get_game_details.return_value = {"header": {"id": "401234"}}
        resp = flask_client.get("/api/game/MLB/401234")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["header"]["id"] == "401234"


class TestScheduleEndpoint:
    def test_schedule_passes_season(self, client):
        flask_client, mock_espn = client
        mock_espn.get_team_schedule.return_value = []
        flask_client.get("/api/schedule/MLB/10?season=2025")
        call_kwargs = mock_espn.get_team_schedule.call_args[1]
        assert call_kwargs.get("season") == 2025


class TestSoccerEndpoint:
    def test_unknown_league_404(self, client):
        flask_client, _ = client
        resp = flask_client.get("/api/soccer/fake_league")
        assert resp.status_code == 404

    @patch("webapp.server.http_requests.get")
    def test_known_league_calls_espn(self, mock_get, client):
        flask_client, _ = client
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"events": []}
        mock_get.return_value = mock_resp
        resp = flask_client.get("/api/soccer/epl")
        assert resp.status_code == 200
        assert mock_get.called
        url_called = mock_get.call_args[0][0]
        assert "eng.1" in url_called

    @patch("webapp.server.http_requests.get")
    def test_soccer_returns_normalized_games(self, mock_get, client):
        flask_client, _ = client
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"events": [
            {
                "id": "abc",
                "name": "Arsenal vs Chelsea",
                "competitions": [{
                    "status": {"type": {"description": "Final", "shortDetail": "FT"}},
                    "broadcasts": [],
                    "competitors": [
                        {"homeAway": "away", "team": {"name": "Arsenal", "id": "1"}, "score": "2"},
                        {"homeAway": "home", "team": {"name": "Chelsea", "id": "2"}, "score": "1"},
                    ],
                }]
            }
        ]}
        mock_get.return_value = mock_resp
        resp = flask_client.get("/api/soccer/epl")
        data = json.loads(resp.data)
        assert data[0]["away_team"] == "Arsenal"
        assert data[0]["home_score"] == "1"


class TestGolfEndpoint:
    def test_unknown_tour_404(self, client):
        flask_client, _ = client
        resp = flask_client.get("/api/golf/xleague")
        assert resp.status_code == 404

    @patch("webapp.server.http_requests.get")
    def test_pga_calls_espn(self, mock_get, client):
        flask_client, _ = client
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"events": []}
        mock_get.return_value = mock_resp
        resp = flask_client.get("/api/golf/pga")
        assert resp.status_code == 200
        url_called = mock_get.call_args[0][0]
        assert "golf/pga" in url_called


class TestStaticFiles:
    def test_index_returns_html(self, client):
        flask_client, _ = client
        resp = flask_client.get("/")
        assert resp.status_code == 200
        assert b"<!DOCTYPE html>" in resp.data or b"<!doctype html>" in resp.data.lower()

    def test_path_traversal_blocked(self, client):
        flask_client, _ = client
        resp = flask_client.get("/../server.py")
        # Should be 403 or 404 — never serve files outside static folder
        assert resp.status_code in (403, 404)


class TestLiveEndpoint:
    def test_live_returns_list(self, client):
        flask_client, mock_espn = client
        mock_espn.get_live_scores_all_sports.return_value = [
            {"id": "1", "name": "Jets at Patriots", "league": "NFL", "status": "Q3 8:45", "teams": [], "recent_play": ""}
        ]
        resp = flask_client.get("/api/live")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)
        assert data[0]["league"] == "NFL"
