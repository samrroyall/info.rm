#!/usr/bin/env python3

from flask import Flask, render_template

import src.dashboard

info_rm = Flask(__name__)

@info_rm.route("/")
def all_leagues():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats(), per_90=False)

@info_rm.route("/per-90")
def all_leagues_per_ninety():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats(None, True), per_90=True)

@info_rm.route("/bundesliga/")
def bundesliga():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats("Bundesliga 1"), per_90=False)

@info_rm.route("/bundesliga/per-90")
def bundesliga_per_ninety():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats("Bundesliga 1", True), per_90=True)

@info_rm.route("/ligue-1/")
def ligue_1():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats("Ligue 1"), per_90=False)

@info_rm.route("/ligue-1/per-90")
def ligue_1_per_ninety():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats("Ligue 1", True), per_90=True)

@info_rm.route("/la-liga/")
def la_liga():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats("Primera Division"), per_90=False)

@info_rm.route("/la-liga/per-90")
def la_liga_per_ninety():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats("Primera Division", True), per_90=True)

@info_rm.route("/premier-league/")
def premier_league():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats("Premier League"), per_90=False)

@info_rm.route("/premier-league/per-90")
def premier_league_per_ninety():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats("Premier League", True), per_90=True)

@info_rm.route("/serie-a/")
def serie_a():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats("Serie A"), per_90=False)

@info_rm.route("/serie-a/per-90")
def serie_a_per_ninety():
    return render_template("dashboard_content.html", query_result=src.dashboard.dashboard_stats("Serie A", True), per_90=True)

if __name__ == "__main__":
    info_rm.run(debug=True)
