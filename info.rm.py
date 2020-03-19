#!/usr/bin/env python3

from flask import Flask, render_template, request

import src.dashboard
import src.builder

info_rm = Flask(__name__)

@info_rm.route("/")
def home():
    return dashboard(league="top-5")


@info_rm.route("/<league>")
def dashboard(league, per_90 = False):
    return render_template(
                    "dashboard_content.html", 
                    query_result = src.dashboard.dashboard_stats(league, per_90), 
                    current_league = league, 
                    current_per90 = per_90
                )

@info_rm.route("/<league>/per-90")
def dashboard_per90(league):
    return dashboard(league=league, per_90=True)

@info_rm.route("/builder")
def builder():
    default_query_result, leagues, clubs, nations = src.builder.default_stats()
    return render_template("builder.html", query_result=default_query_result, leagues=leagues, clubs=clubs, nations=nations)

@info_rm.route("/builder/custom-stat", methods=["POST"])
def custom_stat():
    query_result, leagues, clubs, nations = src.builder.custom_stats(request.form)
    return render_template("builder.html", query_result=query_result, leagues=leagues, clubs=clubs, nations=nations)

if __name__ == "__main__":
    info_rm.run(debug=True)
