from .query import Query, get_max, get_column, get_by, grab_columns
from .web_query import rank_response

def scoring_stats(league, season, per_90):
    query_result = dict()
    max_minutes_played = get_max("players.minutes_played", season)
    max_shots = get_max("players.shots", season)
    for stat in ["goals", "assists", "goal_contributions", "goals_per_shot"]:
        if stat == "goal_contributions":
            select_fields = ["players.goals+players.assists"]
        elif stat == "goals_per_shot":
            select_fields = ["players.goals/players.shots"]
        else:
            select_fields = [f"players.{stat}"]
        select_fields = ([f"({select_fields[0]})/(players.minutes_played/90)"] 
                         if per_90 is True and stat != "goals_per_shot"
                         else select_fields)
        if per_90 is True and stat != "goals_per_shot":
            filter_fields = [ ("players.minutes_played", ">", str(max_minutes_played/3)) ]
        elif stat == "goals_per_shot":
            filter_fields = [ ("players.shots", ">", str(max_shots/3)) ]
        else:
            filter_fields = None
        if league is not None:
            if filter_fields is not None:
                filter_fields.append( ("teams.league_name", "=", league) )
            else:
                filter_fields = [ ("teams.league_name", "=", league) ]
        if filter_fields is not None:
            filter_fields = [(filter_fields, "AND")]
        order_by_stat = select_fields[0]
        order_field = ([order_by_stat], True)
        query_result[stat] = rank_response(select_fields, filter_fields, order_field, season)
    return query_result

def shooting_stats(league, season, per_90):
    query_result = dict()
    max_minutes_played = get_max("players.minutes_played", season)
    for stat in ["shots", "shots_on"]:
        select_fields = ([f"({select_fields[0]})/(players.minutes_played/90)"]
                             if per_90 is True else [f"players.{stat}"])
        if per_90 is True:
            filter_fields = [ ("players.minutes_played", ">", str(max_minutes_played/3)) ]
        else:
            filter_fields = None
        if league is not None:
            if filter_fields is not None:
                filter_fields.append( ("teams.league_name", "=", league) )
            else:
                filter_fields = [ ("teams.league_name", "=", league) ]
        if filter_fields is not None:
            filter_fields = [(filter_fields, "AND")]
        order_by_stat = select_fields[0]
        order_field = ([order_by_stat], True)
        query_result[stat] = rank_response(select_fields, filter_fields, order_field, season)
    return query_result

def passing_stats(league, season, per_90):
    query_result = dict()
    max_minutes_played = get_max("players.minutes_played", season)
    max_passes = get_max("players.passes", season)
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
        query_result[stat] = rank_response(select_fields, filter_fields, order_field, season)
    return query_result

def dribbling_stats(league, season, per_90):
    query_result = dict()
    max_minutes_played = get_max("players.minutes_played", season)
    max_dribbles_attempted = get_max("players.dribbles_attempted", season)
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
        query_result[stat] = rank_response(select_fields, filter_fields, order_field, season)
    return query_result

def defending_stats(league, season, per_90):
    query_result = dict()
    max_minutes_played = get_max("players.minutes_played", season)
    if int(season) < 2017:
        stats = ["interceptions"]
    else:
        stats = ["tackles", "interceptions", "blocks"]
    for stat in stats:
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
        query_result[stat] = rank_response(select_fields, filter_fields, order_field, season)
    return query_result

def other_stats(league, season, per_90):
    query_result = dict()
    max_minutes_played = get_max("players.minutes_played", season)
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
        query_result[stat] = rank_response(select_fields, filter_fields, order_field, season)
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

def dashboard_stats(league, season, per_90):
    league = LEAGUE_LOOKUP.get(league)
    query_result = dict()
    query_result["scoring"] = scoring_stats(league, season, per_90)
    query_result["shooting"] = shooting_stats(league, season, per_90)
    query_result["passing"] = passing_stats(league, season, per_90)
    query_result["dribbling"] = dribbling_stats(league, season, per_90)
    query_result["defending"] = defending_stats(league, season, per_90)
    query_result["other"] = other_stats(league, season, per_90)
    return query_result
