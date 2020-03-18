#!/usr/bin/env python3

from flask import Flask, render_template

import src.dashboard

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
    return render_template("builder.html")

if __name__ == "__main__":
    info_rm.run(debug=True)
