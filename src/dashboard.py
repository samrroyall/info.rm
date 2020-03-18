import os
import pathlib

from .query import Query, Statement, get_max

file_path = pathlib.Path(__file__).parent.absolute()
DB_PATH = os.path.join(str(file_path), "../db/info.rm.db")

#################################
##### Query Result Helpers  #####
#################################

def dashboard_stmt(stat, league, desc = True, additional_filter = None):
    filter_list = []
    if league is not None:
        filter_list.append(("players.league_name", "=", league))
    if additional_filter is not None:
        for filter in additional_filter:
            filter_list.append(filter)
    if len(filter_list) > 0:
        filter_list = [(filter_list, "AND")]
        stmt = Statement(
            table_names = [("players", "team_id"), ("teams", "id")], 
            select_fields = ["players.name", stat, "teams.name", "teams.logo"],
            filter_fields = filter_list,
            order_fields = ([stat], desc)
        )
    else:
        stmt = Statement(
            table_names = [("players", "team_id"), ("teams", "id")], 
            select_fields = ["players.name", stat, "teams.name", "teams.logo"],
            order_fields = ([stat], desc)
        )
    return stmt

def rank_result(query_result, desc=True, stat_type="int"):
    count = 0
    rank = 0
    prev_result = float("inf") if desc == True else -1.0 * float("inf")
    for idx in range(len(query_result)):
        tup = query_result[idx]
        split_name = tup[0].split(" ")
        if len(split_name) == 2 and len(split_name[0]) > 2:
            name = split_name[0][0] + ". " + split_name[1]
        else:
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

##########################
##### Query Helpers  #####
##########################

def goals_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    for stat in ["goals", "assists", "goal_contributions"]:
        newstat = "players.goals+players.assists" if stat == "goal_contributions" else f"players.{stat}"
        if per_90:
            stmt = dashboard_stmt(f"({newstat})/(players.minutes_played/90.0)", league, True,
                   [("players.minutes_played", ">", str(max_minutes_played/3))]
               )
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db(), True, "float")
        else:
            stmt = dashboard_stmt(newstat, league)
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db())
    return query_result

def shots_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    max_shots = get_max(DB_PATH,"players.shots")
    for stat in ["shots", "shots_on", "goals_per_shot"]:
        newstat = "players.goals/players.shots" if stat == "goals_per_shot" else f"players.{stat}"
        if per_90 and stat != "goals_per_shot":
            stmt = dashboard_stmt(f"({newstat})/(players.minutes_played/90.0)", league, True,
                   [("players.minutes_played", ">", str(max_minutes_played/3))]
               )
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db(), True, "float")
        else:
            if stat == "goals_per_shot":
                stmt = dashboard_stmt(newstat, league, True,
                        [("players.shots", ">", str(max_shots/3))]
                )
                query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db(), True, "float")
            else:
                stmt = dashboard_stmt(newstat, league)
                query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db())
    return query_result

def passes_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    max_passes = get_max(DB_PATH,"players.passes")
    for stat in ["passes_key", "passes", "passes_accuracy"]:
        if per_90 and stat != "passes_accuracy":
            stmt = dashboard_stmt(f"players.{stat}/(players.minutes_played/90.0)", league, True,
                   [("players.minutes_played", ">", str(max_minutes_played/3))]
               )
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db(), True, "float")
        else:
            if stat == "passes_accuracy":
                stmt = dashboard_stmt(f"players.{stat}", league, True,
                        [("players.passes", ">", str(max_passes/3))]
                )
            else:
                stmt = dashboard_stmt(f"players.{stat}", league)
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db())
    return query_result

def dribbles_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    max_dribbles_attempted = get_max(DB_PATH,"players.dribbles_attempted")
    for stat in ["dribbles_succeeded", "dribbles_attempted", "dribbles_succeeded_pct"]:
        if per_90 and stat != "dribbles_succeeded_pct":
            stmt = dashboard_stmt(f"players.{stat}/(players.minutes_played/90.0)", league, True,
                       [("players.minutes_played", ">", str(max_minutes_played/3))]
                   )
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db(), True, "float")
        else:
            if stat == "dribbles_succeeded_pct":
                stmt = dashboard_stmt(f"players.{stat}", league, True,
                        [("players.dribbles_attempted", ">", str(max_dribbles_attempted/3))]
                    )
            else:
                stmt = dashboard_stmt(f"players.{stat}", league)
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db())
    return query_result

def defending_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    for stat in ["tackles", "interceptions", "blocks"]:
        if per_90:
            stmt = dashboard_stmt(f"players.{stat}/(players.minutes_played/90.0)", league, True,
                   [("players.minutes_played", ">", str(max_minutes_played/3))]
               )
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db(), True, "float")
        else:
            stmt = dashboard_stmt(f"players.{stat}", league)
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db())
    return query_result

def other_stats(league):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    for stat in ["rating", "goals_conceded", "penalties_saved"]:
        if stat == "goals_conceded":
            stmt = dashboard_stmt(f"players.{stat}/(players.minutes_played/90.0)", league, False, [
                ("players.minutes_played", ">", str(max_minutes_played/3)),
                ("players.position", "=", "Goalkeeper")
            ])
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db(), False, "float")
        elif stat == "rating":
            stmt = dashboard_stmt(f"players.{stat}", league, True, 
                   [("players.minutes_played", ">", str(max_minutes_played/3))]
               )
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db(), True, "float")
        else:
            stmt = dashboard_stmt(f"players.{stat}", league, True, [("players.position", "=", "Goalkeeper")])
            query_result[stat] = rank_result(Query(DB_PATH, stmt).query_db())
    return query_result

##########################
##########################
##########################

LEAGUE_LOOKUP = {
        "top-5": None,
        "bundesliga": "Bundesliga 1",
        "ligue-1": "Ligue 1",
        "premier-league": "Premier League",
        "la-liga": "Primera Division",
        "serie-a": "Serie A"
    }

def dashboard_stats(league, per_90):
    league = LEAGUE_LOOKUP.get(league)
    query_result = dict()
    query_result["goal"] = goals_stats(league, per_90)
    query_result["shot"] = shots_stats(league, per_90)
    query_result["pass"] = passes_stats(league, per_90)
    query_result["dribbling"] = dribbles_stats(league, per_90)
    query_result["defensive"] = defending_stats(league, per_90)
    query_result["other"] = other_stats(league)
    return query_result
