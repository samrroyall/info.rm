#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for

from builder import default_stats, custom_stats
from dashboard import dashboard_stats
from query_utils import get_player_data, get_current_season, get_seasons, get_leagues, get_top_five, get_flags
from search_players import generate_tree, search_tree

info_rm = Flask(__name__)

CURRENT_SEASON = str(get_current_season())
SEASONS = get_seasons()
LEAGUES_DICT = get_leagues()
FLAGS_DICT = get_flags()
TOP_5 = get_top_five()
generate_tree()

@info_rm.route("/")
def home():
    return redirect(url_for(
                "dashboard",
                league="Top-5",
                season=CURRENT_SEASON
            ))

@info_rm.route("/league/<league>/season/<season>")
def dashboard(league="Top-5", season=CURRENT_SEASON):
    if ((league in LEAGUES_DICT.keys() or league == "Top-5") and 
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
                    current_league_flag = FLAGS_DICT.get(league),
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
    if search_query == "''":
        return redirect(url_for(
                "dashboard",
                league=league,
                season=CURRENT_SEASON
            ))
    elif ((league in LEAGUES_DICT.keys() or league == "Top-5") and
      season in SEASONS):
        search_query = search_query[1:-1]
        search_result = search_tree(search_query.lower())[:20]
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
                    current_league_name = LEAGUES_DICT.get(league),
                    current_season = season,
                    seasons = SEASONS,
                    search_result = search_result,
                    search_query = search_query,
                )
    else:
        return redirect(url_for(
                "dashboard",
                league="Top-5",
                season=CURRENT_SEASON
            )) 

@info_rm.route("/player/<id>")
def player(id):
    data = get_player_data(id, False)
    per90_data = get_player_data(id, True)
    if data and per90_data:
        temp_season = str(max([int(season) for season in data.get("stats").keys()]))
        return render_template(
                    "player.html",
                    data=data,
                    per90_data=per90_data,
                    current_season=temp_season,
                    search = True
                )
    else:
        return redirect(url_for("home"))

@info_rm.route("/player/<id>/search/<search_query>")
def player_search(id, search_query = None):
    if search_query == "''":
        return redirect(url_for(
                   "player",
                   id=id,
               ))
    else:
        data = get_player_data(id, False)
        per90_data = get_player_data(id, True)
        if data and per90_data:
            temp_season = str(max([int(season) for season in data.get("stats").keys()]))
            search_query = search_query[1:-1]
            search_result = search_tree(search_query.lower())[:20]
            return render_template(
                       "player.html",
                       data=data,
                       per90_data=per90_data,
                       current_season=temp_season,
                       search_result = search_result,
                       search_query = search_query
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
