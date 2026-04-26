import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests as http_requests
import espn_api

app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)))
CORS(app)

SOCCER_LEAGUES = {
    "epl":       "soccer/eng.1",
    "mls":       "soccer/usa.1",
    "nwsl":      "soccer/usa.nwsl",
    "laliga":    "soccer/esp.1",
    "bundesliga":"soccer/ger.1",
    "seriea":    "soccer/ita.1",
    "ligue1":    "soccer/fra.1",
    "ucl":       "soccer/uefa.champions",
    "uel":       "soccer/uefa.europa",
    "ligamx":    "soccer/mex.1",
    "concacaf":  "soccer/concacaf.leagues.cup",
}

GOLF_TOURS = {
    "pga":  "golf/pga",
    "lpga": "golf/lpga",
}

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports"


def normalize_game(game):
    """Normalize get_scores() game dict to flat structure for frontend."""
    teams = game.get("teams", [])
    away = next((t for t in teams if t.get("home_away") == "away"), teams[0] if teams else {})
    home = next((t for t in teams if t.get("home_away") == "home"), teams[-1] if len(teams) > 1 else {})

    broadcast = ""
    away_team_id = ""
    home_team_id = ""

    comps = game.get("competitions", [])
    if comps:
        comp = comps[0]
        broadcast_list = []
        for b in comp.get("broadcasts", []):
            broadcast_list.extend(b.get("names", []))
        broadcast = ", ".join(broadcast_list)

        for competitor in comp.get("competitors", []):
            ha = competitor.get("homeAway", "")
            tid = competitor.get("team", {}).get("id", "")
            if ha == "away":
                away_team_id = tid
            elif ha == "home":
                home_team_id = tid

    return {
        "id": game.get("id", ""),
        "name": game.get("name", ""),
        "away_team": away.get("name", ""),
        "away_abbr": away.get("abbreviation", ""),
        "away_score": away.get("score", ""),
        "away_record": away.get("record", ""),
        "away_team_id": away_team_id,
        "home_team": home.get("name", ""),
        "home_abbr": home.get("abbreviation", ""),
        "home_score": home.get("score", ""),
        "home_record": home.get("record", ""),
        "home_team_id": home_team_id,
        "status": game.get("status", ""),
        "start_time": game.get("start_time", ""),
        "broadcast": broadcast,
    }


def normalize_soccer_event(event):
    """Normalize a raw ESPN soccer scoreboard event."""
    comps = event.get("competitions", [])
    if not comps:
        return None
    comp = comps[0]
    competitors = comp.get("competitors", [])
    away = next((c for c in competitors if c.get("homeAway") == "away"), {})
    home = next((c for c in competitors if c.get("homeAway") == "home"), {})

    status_type = comp.get("status", {}).get("type", {})
    broadcast_list = []
    for b in comp.get("broadcasts", []):
        broadcast_list.extend(b.get("names", []))

    return {
        "id": event.get("id", ""),
        "name": event.get("name", ""),
        "away_team": away.get("team", {}).get("name", ""),
        "away_team_id": away.get("team", {}).get("id", ""),
        "away_score": away.get("score", ""),
        "home_team": home.get("team", {}).get("name", ""),
        "home_team_id": home.get("team", {}).get("id", ""),
        "home_score": home.get("score", ""),
        "status": status_type.get("description", ""),
        "start_time": status_type.get("shortDetail", status_type.get("detail", "")),
        "broadcast": ", ".join(broadcast_list),
    }


# ── Static file serving ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    # Security: prevent path traversal
    safe_path = os.path.realpath(os.path.join(app.static_folder, filename))
    if not safe_path.startswith(os.path.realpath(app.static_folder)):
        return "", 403
    return send_from_directory(app.static_folder, filename)


# ── API endpoints ─────────────────────────────────────────────────────────────

@app.route("/api/scores/<sport>")
def scores(sport):
    date_str = request.args.get("date", "")
    week = request.args.get("week")
    seasontype = request.args.get("seasontype")

    date = None
    if date_str:
        from datetime import datetime
        try:
            date = datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            pass

    week_int = int(week) if week and week.isdigit() else None
    seasontype_int = int(seasontype) if seasontype and seasontype.isdigit() else None

    try:
        raw = espn_api.get_scores(
            sport.upper(),
            date=date,
            week=week_int,
            seasontype=seasontype_int,
        )
        return jsonify([normalize_game(g) for g in raw])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/game/<sport>/<game_id>")
def game_detail(sport, game_id):
    try:
        data = espn_api.get_game_details(sport.upper(), game_id)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/standings/<sport>")
def standings(sport):
    try:
        data = espn_api.get_standings(sport.upper())
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/schedule/<sport>/<team_id>")
def schedule(sport, team_id):
    season = request.args.get("season")
    season_int = int(season) if season and season.isdigit() else None
    try:
        data = espn_api.get_team_schedule(sport.upper(), team_id, season=season_int)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/news/<sport>")
def news(sport):
    limit_str = request.args.get("limit", "10")
    limit = int(limit_str) if limit_str.isdigit() else 10
    limit = min(limit, 50)  # cap to prevent abuse
    try:
        data = espn_api.get_news(sport.upper(), limit=limit)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/statistics/<sport>")
def statistics(sport):
    try:
        data = espn_api.get_statistics(sport.upper())
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/live")
def live_scores():
    try:
        data = espn_api.get_live_scores_all_sports()
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/soccer/<league>")
def soccer(league):
    soccer_path = SOCCER_LEAGUES.get(league)
    if not soccer_path:
        return jsonify({"error": "Unknown league"}), 404

    date_str = request.args.get("date", "")
    url = f"{ESPN_BASE}/{soccer_path}/scoreboard"
    if date_str:
        url += f"?dates={date_str}"

    try:
        resp = http_requests.get(url, timeout=10)
        if resp.status_code != 200:
            return jsonify([])
        data = resp.json()
        events = data.get("events", [])
        games = [normalize_soccer_event(e) for e in events]
        games = [g for g in games if g is not None]
        return jsonify(games)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/golf/<tour>")
def golf(tour):
    golf_path = GOLF_TOURS.get(tour)
    if not golf_path:
        return jsonify({"error": "Unknown tour"}), 404

    url = f"{ESPN_BASE}/{golf_path}/scoreboard"
    try:
        resp = http_requests.get(url, timeout=10)
        if resp.status_code != 200:
            return jsonify({})
        return jsonify(resp.json())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
