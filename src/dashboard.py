import os
import pathlib

from .query import Query, get_max, get_column, get_by, grab_columns
from .web_query import stmt, rank

file_path = pathlib.Path(__file__).parent.absolute()
DB_PATH = os.path.join(str(file_path), "../db/info.rm.db")

def scoring_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    for stat in ["goals", "assists", "goal_contributions"]:
        select_fields = (["players.goals+players.assists"]
                             if stat == "goal_contributions" 
                             else [f"players.{stat}"])
        select_fields = (select_fields if per_90 is False
                         else [f"({select_fields[0]})/(players.minutes_played/90)"])
        filter_fields = (None if per_90 is False 
                         else [ ("players.minutes_played", ">", str(max_minutes_played/3)) ])
        if league is not None:
            if filter_fields is not None:
                filter_fields.append( ("teams.league_name", "=", league) )
            else:
                filter_fields = [ ("teams.league_name", "=", league) ]
        if filter_fields is not None:
            filter_fields = [(filter_fields, "AND")]
        order_by_stat = select_fields[0]
        order_field = ([order_by_stat], True)
        result = Query(
                  DB_PATH, 
                  stmt(select_fields, filter_fields, order_field)
              ).query_db()
        ranked_result = rank(result, select_fields, order_by_stat)
        query_result[stat] = ranked_result
    return query_result

def shooting_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    max_shots = get_max(DB_PATH,"players.shots")
    for stat in ["shots", "shots_on", "goals_per_shot"]:
        select_fields = (["players.goals/players.shots"]
                             if stat == "goals_per_shot" 
                             else [f"players.{stat}"])
        select_fields = ([f"({select_fields[0]})/(players.minutes_played/90)"]
                             if per_90 is True and stat != "goals_per_shot"
                             else select_fields)
        filter_fields = (None if stat != "goals_per_shot" 
                             else [("players.shots", ">", str(max_shots/3))])
        if per_90 is True and stat != "goals_per_shot":
            if filter_fields is not None:
                filter_fields.append( ("players.minutes_played", ">", str(max_minutes_played/3)) )
            else:
                filter_fields = [ ("players.minutes_played", ">", str(max_minutes_played/3)) ]
        if league is not None:
            if filter_fields is not None:
                filter_fields.append( ("teams.league_name", "=", league) )
            else:
                filter_fields = [ ("teams.league_name", "=", league) ]
        if filter_fields is not None:
            filter_fields = [(filter_fields, "AND")]
        order_by_stat = select_fields[0]
        order_field = ([order_by_stat], True)
        result = Query(
                  DB_PATH, 
                  stmt(select_fields, filter_fields, order_field)
              ).query_db()
        ranked_result = rank(result, select_fields, order_by_stat)
        query_result[stat] = ranked_result
    return query_result

def passing_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    max_passes = get_max(DB_PATH,"players.passes")
    for stat in ["passes_key", "passes", "passes_accuracy"]:
        select_fields = [f"players.{stat}"]
        select_fields = ([f"({select_fields[0]})/(players.minutes_played/90)"]
                             if per_90 is True and stat != "passes_accuracy"
                             else select_fields)
        filter_fields = (None if stat != "passes_accuracy" 
                             else [("players.passes", ">", str(max_passes/3))])
        if per_90 is True and stat != "passes_accuracy":
            if filter_fields is not None:
                filter_fields.append( ("players.minutes_played", ">", str(max_minutes_played/3)) )
            else:
                filter_fields = [ ("players.minutes_played", ">", str(max_minutes_played/3)) ]
        if league is not None:
            if filter_fields is not None:
                filter_fields.append( ("teams.league_name", "=", league) )
            else:
                filter_fields = [ ("teams.league_name", "=", league) ]
        if filter_fields is not None:
            filter_fields = [(filter_fields, "AND")]
        order_by_stat = select_fields[0]
        order_field = ([order_by_stat], True)
        result = Query(
                  DB_PATH, 
                  stmt(select_fields, filter_fields, order_field)
              ).query_db()
        ranked_result = rank(result, select_fields, order_by_stat)
        query_result[stat] = ranked_result
    return query_result

def dribbling_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    max_dribbles_attempted = get_max(DB_PATH,"players.dribbles_attempted")
    for stat in ["dribbles_succeeded", "dribbles_attempted", "dribbles_succeeded_pct"]:
        select_fields = [f"players.{stat}"]
        select_fields = ([f"({select_fields[0]})/(players.minutes_played/90)"]
                             if per_90 is True and stat != "dribbles_succeeded_pct"
                             else select_fields)
        filter_fields = (None if stat != "dribbles_succeeded_pct" 
                             else [("players.dribbles_attempted", ">", str(max_dribbles_attempted/3))])
        if per_90 is True and stat != "dribbles_succeeded_pct":
            if filter_fields is not None:
                filter_fields.append( ("players.minutes_played", ">", str(max_minutes_played/3)) )
            else:
                filter_fields = [ ("players.minutes_played", ">", str(max_minutes_played/3)) ]
        if league is not None:
            if filter_fields is not None:
                filter_fields.append( ("teams.league_name", "=", league) )
            else:
                filter_fields = [ ("teams.league_name", "=", league) ]
        if filter_fields is not None:
            filter_fields = [(filter_fields, "AND")]
        order_by_stat = select_fields[0]
        order_field = ([order_by_stat], True)
        result = Query(
                  DB_PATH, 
                  stmt(select_fields, filter_fields, order_field)
              ).query_db()
        ranked_result = rank(result, select_fields, order_by_stat)
        query_result[stat] = ranked_result
    return query_result

def defending_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    for stat in ["tackles", "interceptions", "blocks"]:
        select_fields = [f"players.{stat}"]
        select_fields = (select_fields if per_90 is False
                         else [f"({select_fields[0]})/(players.minutes_played/90)"])
        filter_fields = (None if per_90 is False 
                         else [("players.minutes_played", ">", str(max_minutes_played/3))])
        if league is not None:
            if filter_fields is not None:
                filter_fields.append( ("teams.league_name", "=", league) )
            else:
                filter_fields = [ ("teams.league_name", "=", league) ]
        if filter_fields is not None:
            filter_fields = [(filter_fields, "AND")]
        order_by_stat = select_fields[0]
        order_field = ([order_by_stat], True)
        result = Query(
                  DB_PATH, 
                  stmt(select_fields, filter_fields, order_field)
              ).query_db()
        ranked_result = rank(result, select_fields, order_by_stat)
        query_result[stat] = ranked_result
    return query_result

def other_stats(league, per_90):
    query_result = dict()
    max_minutes_played = get_max(DB_PATH,"players.minutes_played")
    for stat in ["rating", "goals_conceded", "penalties_saved"]:
        select_fields = ([f"(players.{stat})/(players.minutes_played/90)"]
                         if per_90 is True and stat == "goals_conceded"
                         else [f"players.{stat}"])
        filter_fields = None
        if stat != "penalties_saved":
            filter_fields = [("players.minutes_played", ">", str(max_minutes_played/3))]
        # other two stats are only for keepers
        if stat != "rating":  
            if filter_fields is not None:
                filter_fields.append( ("players.position", "=", "Goalkeeper") )
            else:
                filter_fields = [ ("players.position", "=", "Goalkeeper") ]
        if league is not None:
            if filter_fields is not None:
                filter_fields.append( ("teams.league_name", "=", league) )
            else:
                filter_fields = [ ("teams.league_name", "=", league) ]
        if filter_fields is not None:
            filter_fields = [(filter_fields, "AND")]
        order_by_stat = select_fields[0]
        order_field = (([order_by_stat], True) 
                       if stat != "goals_conceded" 
                       else ([order_by_stat], False))
        result = Query(
                  DB_PATH, 
                  stmt(select_fields, filter_fields, order_field)
              ).query_db()
        if stat == "goals_conceded":
            ranked_result = rank(result, select_fields, order_by_stat, False)
        else:
            ranked_result = rank(result, select_fields, order_by_stat)
        query_result[stat] = ranked_result
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
    query_result["scoring"] = scoring_stats(league, per_90)
    query_result["shooting"] = shooting_stats(league, per_90)
    query_result["passing"] = passing_stats(league, per_90)
    query_result["dribbling"] = dribbling_stats(league, per_90)
    query_result["defending"] = defending_stats(league, per_90)
    query_result["other"] = other_stats(league, per_90)
    return query_result
