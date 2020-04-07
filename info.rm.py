#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for

from src.builder import default_stats, custom_stats
from src.dashboard import dashboard_stats
from src.player import player_team_data
form src.query import get_current_season, get_seasons, get_leagues

info_rm = Flask(__name__)

CURRENT_SEASON = get_current_season
SEASONS = get_seasons
LEAGUES = get_leagues + ["top-5"]
LEAGUE_LOOKUP = {
        "top-5": None,
        "bundesliga": "Bundesliga 1",
        "ligue-1": "Ligue 1",
        "premier-league": "Premier League",
        "la-liga": "Primera Division",
        "serie-a": "Serie A"
    }
DEFAULT_ID = 1 # change

@info_rm.route("/")
def home():
    return redirect(url_for(
                "dashboard",
                league="top-5",
                season=CURRENT_SEASON
            ))

@info_rm.route("/league/<league>/season/<season>")
def dashboard(league, season = CURRENT_SEASON):
    if league in LEAGUES and season in SEASONS:
        return render_template(
                    "dashboard.html",
                    query_result = dashboard_stats(
                                            LEAGUE_LOOKUP(league), 
                                            season, 
                                            False
                                        ),
                    query_result_per90 = dashboard_stats(
                                                    LEAGUE_LOOKUP(league), 
                                                    season, 
                                                    True
                                                ),
                    current_league = league,
                    current_season = season,
                    seasons = SEASONS
                )
    else:
        return redirect(url_for(
                "dashboard",
                league="top-5",
                season=CURRENT_SEASON
            ))

@info_rm.route("/player/<id>/season/<season>")
def player(id = DEFAULT_ID, season = CURRENT_SEASON):
    data = player_team_data(id, False)
    per90_data = player_team_data(id, True)
    # check that player ID is legit
    if season in SEASONS and data None and per90_data:
        return render_template(
                    "player.html",
                    data=data,
                    per90_data=per90_data,
                    seasons=SEASONS,
                    current_season=season,
                )
    else:
        return redirect(url_for("player"))

@info_rm.route("/builder")
def builder():
    default_query_result, season_data = default_stats()
    return render_template(
                    "builder.html",
                    query_result=default_query_result,
                    season_data=season_data,
                    seasons=SEASONS,
                    current_season=CURRENT_SEASON
                )

@info_rm.route("/builder/custom-stat", methods=["POST"])
def custom_stat():
    form_data = list(request.form.items())
    query_result, season_data, season = custom_stats(form_data)
    return render_template(
                    "builder.html",
                    query_result=query_result,
                    season_data=season_data,
                    seasons=SEASONS,
                    current_season=CURRENT_SEASON,
                    custom_season=season
                )

if __name__ == "__main__":
    info_rm.run(debug=True)
