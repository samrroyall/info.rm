#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for

from src.dashboard import dashboard_stats
from src.builder import default_stats, custom_stats
from src.player import player_team_data

info_rm = Flask(__name__)

CURRENT_SEASON = "2019"
SEASONS = ["2019", "2018", "2017", "2016", "2015"]
LEAGUES = ["premier-league", "serie-a", "ligue-1", "la-liga", "bundesliga", "top-5"]

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
                    query_result = dashboard_stats(league, season, False),
                    query_result_per90 = dashboard_stats(league, season, True),
                    current_league = league,
                    current_season = season,
                    seasons = SEASONS,
                )
    else:
        return redirect(url_for(
                "dashboard",
                league="top-5",
                season=CURRENT_SEASON
            ))

@info_rm.route("/player/<id>/season/<season>")
def player(id, season, per_90 = False):
    data = player_team_data(id, season, per_90)
    player_data = data[0]
    player_stats = data[1]
    team_data = data[2]
    league_data = data[3]
    return render_template(
                    "player.html",
                    player_data=player_data,
                    player_stats=player_stats,
                    team_data=team_data,
                    league_data=league_data,
                    seasons=SEASONS,
                    current_season=season,
                    per_90=per_90
                )

@info_rm.route("/player/<id>/season/<season>/per-90")
def player_per90(id, season):
    return player(id=id, season=season, per_90=True)

@info_rm.route("/builder")
def builder():
    default_query_result, leagues, clubs, nations = default_stats()
    return render_template(
                    "builder.html",
                    query_result=default_query_result,
                    leagues=leagues,
                    clubs=clubs,
                    nations=nations,
                    seasons=SEASONS,
                    current_season=CURRENT_SEASON
                )

@info_rm.route("/builder/custom-stat", methods=["POST"])
def custom_stat():
    form_data = list(request.form.items())
    query_result, leagues, clubs, nations, season = custom_stats(form_data)
    return render_template(
                    "builder.html",
                    query_result=query_result,
                    leagues=leagues,
                    clubs=clubs,
                    nations=nations,
                    seasons=SEASONS,
                    current_season=CURRENT_SEASON,
                    custom_season=season
                )

if __name__ == "__main__":
    info_rm.run(debug=True)
