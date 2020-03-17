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
    filter_list = []
    if league is not None:
        filter_list.append(("players.league_name", "=", league))
    if additional_filter is not None:
        for filter in additional_filter:
            filter_list.append(filter)
    if len(filter_list) > 0:
        filter_list = [(filter_list, "AND")]
        stmt = src.query.Statement(
            table_names = [("players", "team_id"), ("teams", "id")], 
            select_fields = ["players.name", f"players.{stat}", "teams.name", "teams.logo"],
            filter_fields = filter_list,
            order_fields = ([f"players.{stat}"], desc)
        )
    else:
        stmt = src.query.Statement(
            table_names = [("players", "team_id"), ("teams", "id")], 
            select_fields = ["players.name", f"players.{stat}", "teams.name", "teams.logo"],
            order_fields = ([f"players.{stat}"], desc)
        )
    return stmt

def rank_result(query_result, desc=True, stat_type="int"):
    count = 0
    rank = 0
    prev_result = float("inf") if desc == True else -1.0 * float("inf")
    for idx in range(len(query_result)):
        tup = query_result[idx]
        name = tup[0]
        stat = float(tup[1])
        team_name = tup[2]
        team_logo = tup[3]
        count += 1
        if desc == True and round(stat, 3) < prev_result:
            rank = count
        elif desc == False and round(stat, 3) > prev_result:
            rank = count
        prev_result = round(stat, 3)
        ranked_tup = {
            "rank": rank,
            "name": name,
            "stat": round(stat) if stat_type == "int" else round(stat, 2),
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

def attacking_stats_per_90(league = None):
    query_result = dict()
    max_minutes_played = src.query.get_max_minutes_played(DB_PATH)
    for stat in ["goals", "assists", "shots_on"]:
        stmt = dashboard_stmt(f"{stat}/(players.minutes_played/90.0)", league, True,
                   [("players.minutes_played", ">", str(max_minutes_played/3))]
               )
        query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db(), True, "float")
    return query_result

def creation_stats(league = None):
    query_result = dict()
    for stat in ["passes_key", "dribbles_succeeded", "passes"]:
        stmt = dashboard_stmt(stat, league)
        query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db())
    return query_result

def creation_stats_per_90(league = None):
    query_result = dict()
    max_minutes_played = src.query.get_max_minutes_played(DB_PATH)
    for stat in ["passes_key", "dribbles_succeeded", "passes"]:
        stmt = dashboard_stmt(f"{stat}/(players.minutes_played/90.0)", league, True,
                   [("players.minutes_played", ">", str(max_minutes_played/3))]
               )
        query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db(), True, "float")
    return query_result

def defending_stats(league = None):
    query_result = dict()
    for stat in ["tackles", "interceptions", "blocks"]:
        stmt = dashboard_stmt(stat, league)
        query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db())
    return query_result

def defending_stats_per_90(league = None):
    query_result = dict()
    max_minutes_played = src.query.get_max_minutes_played(DB_PATH)
    for stat in ["tackles", "interceptions", "blocks"]:
        stmt = dashboard_stmt(f"{stat}/(players.minutes_played/90.0)", league, True, 
                   [("players.minutes_played", ">", str(max_minutes_played/3))]
               )
        query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db(), True, "float")
    return query_result

def other_stats(league = None):
    query_result = dict()
    max_minutes_played = src.query.get_max_minutes_played(DB_PATH)
    for stat in ["rating", "goals_conceded", "penalties_saved"]:
        if stat == "goals_conceded":
            stmt = dashboard_stmt(f"{stat}/(players.minutes_played/90.0)", league, False, [
                ("players.minutes_played", ">", str(max_minutes_played/3)),
                ("players.position", "=", "Goalkeeper")
            ])
            query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db(), False, "float")
        elif stat == "rating":
            stmt = dashboard_stmt(stat, league, True, 
                   [("players.minutes_played", ">", str(max_minutes_played/3))]
               )
            query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db(), True, "float")
        else:
            stmt = dashboard_stmt(stat, league, True, [("players.position", "=", "Goalkeeper")])
            query_result[stat] = rank_result(src.query.Query(DB_PATH, stmt).query_db())
    return query_result

def dashboard_stats(league = None):
    query_result = dict()
    query_result["attacking"] = attacking_stats(league)
    query_result["creation"] = creation_stats(league)
    query_result["defending"] = defending_stats(league)
    query_result["other"] = other_stats(league)
    return query_result

def dashboard_stats_per_90(league = None):
    query_result = dict()
    query_result["attacking"] = attacking_stats_per_90(league)
    query_result["creation"] = creation_stats_per_90(league)
    query_result["defending"] = defending_stats_per_90(league)
    query_result["other"] = other_stats(league)
    return query_result

info_rm = Flask(__name__)

@info_rm.route("/")
def all_leagues():
    return render_template("dashboard.html", query_result=dashboard_stats(), per_90=False)

@info_rm.route("/per-90")
def all_leagues_per_ninety():
    return render_template("dashboard.html", query_result=dashboard_stats_per_90(), per_90=True)

@info_rm.route("/bundesliga/")
def bundesliga():
    return render_template("dashboard.html", query_result=dashboard_stats("Bundesliga 1"), per_90=False)

@info_rm.route("/bundesliga/per-90")
def bundesliga_per_ninety():
    return render_template("dashboard.html", query_result=dashboard_stats_per_90("Bundesliga 1"), per_90=True)

@info_rm.route("/ligue-1/")
def ligue_1():
    return render_template("dashboard.html", query_result=dashboard_stats("Ligue 1"), per_90=False)

@info_rm.route("/ligue-1/per-90")
def ligue_1_per_ninety():
    return render_template("dashboard.html", query_result=dashboard_stats_per_90("Ligue 1"), per_90=True)

@info_rm.route("/la-liga/")
def la_liga():
    return render_template("dashboard.html", query_result=dashboard_stats("Primera Division"), per_90=False)

@info_rm.route("/la-liga/per-90")
def la_liga_per_ninety():
    return render_template("dashboard.html", query_result=dashboard_stats_per_90("Primera Division"), per_90=True)

@info_rm.route("/premier-league/")
def premier_league():
    return render_template("dashboard.html", query_result=dashboard_stats("Premier League"), per_90=False)

@info_rm.route("/premier-league/per-90")
def premier_league_per_ninety():
    return render_template("dashboard.html", query_result=dashboard_stats_per_90("Premier League"), per_90=True)

@info_rm.route("/serie-a/")
def serie_a():
    return render_template("dashboard.html", query_result=dashboard_stats("Serie A"), per_90=False)

@info_rm.route("/serie-a/per-90")
def serie_a_per_ninety():
    return render_template("dashboard.html", query_result=dashboard_stats_per_90("Serie A"), per_90=True)

if __name__ == "__main__":
    info_rm.run(debug=True)
