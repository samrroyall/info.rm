#!/usr/bin/env python3

import os
import pathlib

from flask import Flask, render_template
import src.query

#####################
### QUERY HELPERS ###
#####################

file_path = pathlib.Path(__file__).parent.absolute()
DB_PATH = os.path.join(str(file_path), "db/info.rm.db")

def dashboard_stmt(stat, league, desc = True, additional_filter = None):
    filter_list = [("players.minutes_played", ">", "900.0")]
    if league is not None:
        filter_list.append(("players.league_name", "=", league))
    if additional_filter is not None:
        filter_list.append(additional_filter)
    filter_list = [(filter_list, "AND")]
    stmt = src.query.Statement(
        table_names = [("players", "team_id"), ("teams", "id")], 
        select_fields = ["players.name", f"players.{stat}", "teams.name", "teams.logo"],
        filter_fields = filter_list,
        order_fields = ([f"players.{stat}"], desc)
    )
    return stmt

def rank_result(query_result):
    count = 0
    rank = 0
    prev_result = float("inf") 
    for idx in range(len(query_result)):
        tup = query_result[idx]
        name = tup[0]
        stat = float(tup[1])
        team_name = tup[2]
        team_logo = tup[3]
        count += 1
        if stat < prev_result:
            rank = count
        prev_result = stat
        ranked_tup = {
            "rank": rank,
            "name": name,
            "stat": stat,
            "team_name": team_name,
            "team_logo": team_logo
        }
        query_result[idx] = ranked_tup
    return query_result

def attacking_stats(league = None):
    query_result = dict()
    for stat in ["goals", "assists", "shots_on"]:
        stmt = dashboard_stmt(stat, league)
        query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db())
    return query_result

def creation_stats(league = None):
    query_result = dict()
    for stat in ["passes_key", "dribbles_succeeded", "passes"]:
        stmt = dashboard_stmt(stat, league)
        query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db())
    return query_result

def defending_stats(league = None):
    query_result = dict()
    for stat in ["tackles", "interceptions", "blocks"]:
        stmt = dashboard_stmt(stat, league)
        query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db())
    return query_result

def goalkeeping_stats(league = None):
    query_result = dict()
    for stat in ["goals_conceded", "penalties_saved"]:
        if stat == "goals_conceded":
            stmt = dashboard_stmt(stat, league, False, ("players.position", "=", "Goalkeeper"))
        else:
            stmt = dashboard_stmt(stat, league, True, ("players.position", "=", "Goalkeeper"))
        query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db())
    return query_result

def dashboard_stats(league = None):
    query_result = dict()
    query_result["attacking"] = attacking_stats(league)
    query_result["creation"] = creation_stats(league)
    query_result["defending"] = defending_stats(league)
    query_result["goalkeeping"] = goalkeeping_stats(league)
    return query_result

DASHBOARD_PAGES = {
    "attacking": {
        "goals": 1,
        "assists": 1,
        "shots_on": 1
    }
}


info_rm = Flask(__name__)

@info_rm.route("/")
def all_leagues():
    return render_template("dashboard.html", query_result=dashboard_stats(), pages=DASHBOARD_PAGES)

@info_rm.route("/bundesliga")
def bundesliga():
    return render_template("dashboard.html", query_result=dashboard_stats("Bundesliga 1"))

@info_rm.route("/ligue-1")
def ligue_1():
    return render_template("dashboard.html", query_result=dashboard_stats("Ligue 1"))

@info_rm.route("/la-liga")
def la_liga():
    return render_template("dashboard.html", query_result=dashboard_stats("Primera Division"))

@info_rm.route("/premier-league")
def premier_league():
    return render_template("dashboard.html", query_result=dashboard_stats("Premier League"))

@info_rm.route("/serie-a")
def serie_a():
    return render_template("dashboard.html", query_result=dashboard_stats("Serie A"))

if __name__ == "__main__":
    info_rm.run(debug=True)
