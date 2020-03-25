#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for

import src.dashboard
import src.builder

info_rm = Flask(__name__)

leagues = ["premier-league", "serie-a", "ligue-1", "la-liga", "bundesliga", "top-5"]

@info_rm.route("/")
def home():
    return redirect(url_for("dashboard", league="top-5"))


@info_rm.route("/<league>")
def dashboard(league, per_90 = False):
    if league in leagues:
        return render_template(
                    "dashboard_content.html", 
                    query_result = src.dashboard.dashboard_stats(league, per_90), 
                    current_league = league, 
                    current_per90 = per_90
                )
    else:
        return redirect(url_for("home"))

@info_rm.route("/<league>/per-90")
def dashboard_per90(league):
    if league in leagues:
        return dashboard(league=league, per_90=True)
    else:
        return redirect(url_for("home"))

@info_rm.route("/builder")
def builder():
    default_query_result, leagues, clubs, nations = src.builder.default_stats()
    return render_template("customize.html", query_result=default_query_result, leagues=leagues, clubs=clubs, nations=nations)

@info_rm.route("/builder/custom-stat", methods=["POST"])
def custom_stat():
    form_data = list(request.form.items())
    query_result, leagues, clubs, nations = src.builder.custom_stats(form_data)
    return render_template("customize.html", query_result=query_result, leagues=leagues, clubs=clubs, nations=nations)

if __name__ == "__main__":
    info_rm.run(debug=True)
