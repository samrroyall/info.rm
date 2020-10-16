#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for

from builder import default_stats, custom_stats
from dashboard import dashboard_stats
import query_utils

info_rm = Flask(__name__)

SEASONS = query_utils.get_seasons()
CURRENT_SEASON = max(SEASONS)
LEAGUES = query_utils.get_leagues()
LEAGUES_DICT = query_utils.get_leagues_dict()
FLAGS_DICT = query_utils.get_flags()
PLAYERS = query_utils.get_players() # player search data
TEAMS = query_utils.get_teams() # team search data
TOP_5 = query_utils.get_top_five()

@info_rm.route("/")
def home():
    return redirect(url_for("dashboard", league="Top-5", season=CURRENT_SEASON))

@info_rm.route("/league/<league>/season/<season>")
def dashboard(league="Top-5", season=CURRENT_SEASON):
    if ((league in LEAGUES_DICT.keys() or league == "Top-5") and 
        season in SEASONS):
        params = {
            "query_result": dashboard_stats(league, season, False),
            "query_result_per90": dashboard_stats(league, season, True),
            "current_league": league,
            "current_league_flag": FLAGS_DICT.get(league),
            "current_season": season,
            "leagues": LEAGUES,
            "players": PLAYERS,
            "seasons": SEASONS,
            "teams": TEAMS
        }
        return render_template("dashboard.html", **params)
    elif season in SEASONS:
        return redirect(url_for("dashboard", league="Top-5", season=season))
    else:
        return redirect(url_for("dashboard", league="Top-5", season=CURRENT_SEASON))

@info_rm.route("/team/<id>/season/<season>")
def team(id, season=CURRENT_SEASON):
    team_seasons = query_utils.get_team_seasons(id)
    data = query_utils.get_team_players(id, season)
    if season not in team_seasons:
        season = max(team_seasons)
    if data:
        params = {
            "current_season": season,
            "leagues": LEAGUES,
            "players": PLAYERS,
            "seasons": team_seasons,
            "teams": TEAMS,
            "team_players": data
        }
        return render_template("team.html", **params)
    else:
        return redirect(url_for("home"))

@info_rm.route("/player/<id>")
def player(id):
    data = query_utils.get_player_data(id, False)
    per90_data = query_utils.get_player_data(id, True)
    if data and per90_data:
        curr_seasons = [int(s) for s in list(data.get("stats").keys())]
        params = {
            "current_season": str(max(curr_seasons)),
            "data": data,
            "leagues": LEAGUES,
            "per90_data": per90_data,
            "players": PLAYERS,
            "teams": TEAMS
        }
        return render_template("player.html", **params)
    else:
        return redirect(url_for("home"))

@info_rm.route("/builder")
def builder():
    default_query_result, season_data = default_stats()
    params = {
        "current_season": CURRENT_SEASON,
        "leagues": LEAGUES,
        "query_result": default_query_result,
        "players": PLAYERS,
        "season_data": season_data,
        "seasons": SEASONS,
        "teams": TEAMS
    }
    return render_template("builder.html",**params)

@info_rm.route("/builder/custom-stat", methods=["POST"])
def custom_stat():
    form_data = list(request.form.items())
    query_result, season_data, season = custom_stats(form_data)
    params = {
        "current_season": CURRENT_SEASON,
        "custom_season": season,
        "leagues": LEAGUES,
        "query_result": query_result,
        "players": PLAYERS,
        "season_data": season_data,
        "seasons": SEASONS,
        "teams": TEAMS
    } 
    return render_template("builder.html", **params)

if __name__ == "__main__":
    info_rm.run(debug=True)
