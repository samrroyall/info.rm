#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for

from builder import default_stats, custom_stats
from dashboard import dashboard_stats
from query_utils import get_leagues, get_flags, get_players, get_player_data, get_seasons, get_top_five

info_rm = Flask(__name__)

SEASONS = get_seasons()
CURRENT_SEASON = str(max(SEASONS))
LEAGUES_DICT = get_leagues()
FLAGS_DICT = get_flags()
PLAYERS = get_players()
TOP_5 = get_top_five()

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
            "players": PLAYERS,
            "seasons": SEASONS
        }

        return render_template("dashboard.html", **params)
    elif season in SEASONS:
        return redirect(url_for("dashboard", league="Top-5", season=season))
    else:
        return redirect(url_for("dashboard", league="Top-5", season=CURRENT_SEASON))

@info_rm.route("/player/<id>")
def player(id):
    data = get_player_data(id, False)
    per90_data = get_player_data(id, True)
    if data and per90_data:
        temp_season = str(max([int(season) for season in data.get("stats").keys()]))

        params = {
            "data": data,
            "per90_data": per90_data,
            "players": PLAYERS,
            "current_season": temp_season
        }

        return render_template("player.html", **params)
    else:
        return redirect(url_for("home"))

@info_rm.route("/builder")
def builder():
    default_query_result, season_data = default_stats()

    params = {
        "query_result": default_query_result,
        "players": PLAYERS,
        "season_data": season_data,
        "seasons": SEASONS
    }

    return render_template("builder.html",**params)

@info_rm.route("/builder/custom-stat", methods=["POST"])
def custom_stat():
    form_data = list(request.form.items())
    query_result, season_data, season = custom_stats(form_data)

    params = {
        "query_result": query_result,
        "players": PLAYERS,
        "season_data": season_data,
        "seasons": SEASONS,
        "custom_season": season
    } 

    return render_template("builder.html", **params)

if __name__ == "__main__":
    info_rm.run(debug=True)
