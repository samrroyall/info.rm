#!/usr/bin/env python3

from flask import Flask, render_template

#####################
### QUERY HELPERS ###
#####################

def generate_player_card(rank, player_name, team_name, logo_url, value):
    return f"""<li class="list-group-item">
          <div class="row h-100 justify-content-center align-items-center">
            <div class="col-3 text-left float-left">
              <img src="{logo_url}" height="30px"/>
            </div>
            <div class="col-6 text-left float-center">
              <div class="row">
                <strong>{rank}. {player_name}</strong>
              </div>
              <div class="row">
                {team_name}
              </div>
            </div>
            <div class="col-3 text-right float-right">
              <strong>{value}</strong>
            </div>
          </div>
        </li>
    """

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
