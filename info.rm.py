#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for

from src.dashboard import dashboard_stats 
from src.builder import default_stats, custom_stats
from src.player import player_team_data

info_rm = Flask(__name__)

leagues = ["premier-league", "serie-a", "ligue-1", "la-liga", "bundesliga", "top-5"]

@info_rm.route("/")
def home():
    return redirect(url_for("dashboard", league="top-5"))

@info_rm.route("/league/<league>")
def dashboard(league, per_90 = False):
    if league in leagues:
        return render_template(
                    "dashboard_content.html", 
                    query_result = dashboard_stats(league, per_90), 
                    current_league = league, 
                    current_per90 = per_90
                )
    else:
        return redirect(url_for("home"))

@info_rm.route("/league/<league>/per-90")
def dashboard_per90(league):
    if league in leagues:
        return dashboard(league=league, per_90=True)
    else:
        return redirect(url_for("home"))

@info_rm.route("/player/<id>")
def player(id):
    data = player_team_data(id)
    player_data = data[0]
    team_data = data[1]
    league_data = data[2]
    return render_template(
                    "player_info.html", 
                    player_data=player_data, 
                    team_data=team_data,
                    league_data=league_data
                )

@info_rm.route("/builder")
def builder():
    default_query_result, leagues, clubs, nations = default_stats()
    return render_template("customize.html", query_result=default_query_result, leagues=leagues, clubs=clubs, nations=nations)

@info_rm.route("/builder/custom-stat", methods=["POST"])
def custom_stat():
    form_data = list(request.form.items())
    query_result, leagues, clubs, nations = custom_stats(form_data)
    return render_template("customize.html", query_result=query_result, leagues=leagues, clubs=clubs, nations=nations)

if __name__ == "__main__":
    info_rm.run(debug=True)
