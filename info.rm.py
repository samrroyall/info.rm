#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for

from src.builder import default_stats, custom_stats
from src.dashboard import dashboard_stats
from src.player import player_team_data
from src.query import get_current_season, get_seasons, get_leagues, get_top_five
from src.search import generate_tree, search_tree

info_rm = Flask(__name__)

CURRENT_SEASON = str(get_current_season())
SEASONS = get_seasons()
LEAGUES = get_leagues()
TOP_5 = get_top_five()
generate_tree()

@info_rm.route("/")
def home():
    print("season:", CURRENT_SEASON)
    return redirect(url_for(
                "dashboard",
                league="Top-5",
                season=CURRENT_SEASON
            ))

@info_rm.route("/league/<league>/season/<season>/search/")
def no_search(league="Top-5", season=CURRENT_SEASON):
    return redirect(url_for(
                "dashboard",
                league=league,
                season=season
            ))

@info_rm.route("/league/<league>/season/<season>")
def dashboard(league="Top-5", season=CURRENT_SEASON):
    if ((league.replace("-", " ") in LEAGUES or league == "Top-5") and 
        season in SEASONS):
        return render_template(
                    "dashboard.html",
                    query_result = dashboard_stats(
                                        league, 
                                        season, 
                                        False
                                    ),
                    query_result_per90 = dashboard_stats(
                                                league, 
                                                season, 
                                                True
                                            ),
                    current_league = league,
                    current_season = season,
                    seasons=SEASONS,
                    search=True
                )
    else:
        return redirect(url_for(
                "dashboard",
                league="Top-5",
                season=CURRENT_SEASON
            ))

@info_rm.route("/league/<league>/season/<season>/search/<search_query>")
def dashboard_search(league="Top-5", search_query=None, season = CURRENT_SEASON):
    if ((league.replace("-", " ") in LEAGUES or league == "Top-5") and 
        season in SEASONS and search_query):
        search_result = search_tree(search_query.strip().lower().replace(" ",""))[:10]
        return render_template(
                    "dashboard.html",
                    query_result = dashboard_stats(
                                        league, 
                                        season, 
                                        False
                                    ),
                    query_result_per90 = dashboard_stats(
                                                league, 
                                                season, 
                                                True
                                            ),
                    current_league = league,
                    current_season = season,
                    seasons = SEASONS,
                    search_result = search_result,
                    search_query = search_query,
                    search=True
                )
    else:
        return redirect(url_for(
                "dashboard",
                league="Top-5",
                season=CURRENT_SEASON
            )) 

@info_rm.route("/player/<id>")
def player(id):
    data = player_team_data(id, False)
    temp_season = str(max([int(season) for season in data.get("stats").keys()]))
    per90_data = player_team_data(id, True)
    if data and per90_data:
        return render_template(
                    "player.html",
                    data=data,
                    per90_data=per90_data,
                    current_season=temp_season,
                )
    else:
        return redirect(url_for("home"))

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
