#!/usr/bin/env python3

from flask import Flask, render_template

#####################
### QUERY HELPERS ###
#####################

info_rm = Flask(__name__)

@info_rm.route("/")
def all_leagues():
    return render_template("index.html")

@info_rm.route("/bundesliga")
def bundesliga():
    return render_template("index.html")

@info_rm.route("/ligue-1")
def ligue_1():
    return render_template("index.html")

@info_rm.route("/la-liga")
def la_liga():
    return render_template("index.html")

@info_rm.route("/premier-league")
def premier_league():
    return render_template("index.html")

@info_rm.route("/serie-a")
def serie_a():
    return render_template("index.html")

if __name__ == "__main__":
    info_rm.run(debug=True)
