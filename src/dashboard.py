from query import Query
from query_utils import get_max, get_top_five, get_num_stats
from web_query import rank_response

DEFAULT_FILTER = None
MP_FILTER = None
PASS_FILTER = None 
SHOT_FILTER = None 
PER_90 = None
TOP_5 = get_top_five()

##########################
###### QUERY HELPERS #####
##########################

def finalize_query(select_fields, filter_fields):
        # finalize filters
        filter_fields = [(filter_fields, "AND")]

        # order by
        order_by_stat = select_fields[0]
        order_field = ([order_by_stat], True)
        return rank_response(select_fields, filter_fields, order_field)

##########################
###### MAIN HELPERS ######
##########################

def scoring_stats():
    scoring_query = dict()
    for stat in ["goals", "assists", "goal_contributions", "goals_per_shot"]:
        # select fields
        if stat == "goal_contributions":
            select_fields = ["stats.goals+stats.assists"]
        elif stat == "goals_per_shot":
            select_fields = ["stats.goals/stats.shots"]
        else:
            select_fields = [f"stats.{stat}"]

        # initialize filters
        filter_fields = [] + DEFAULT_FILTER

        # handle goals per shot filter
        if stat == "goals_per_shot":
            filter_fields.append( ("stats.shots", ">", SHOT_FILTER) )
        # handle per 90
        elif PER_90 is True:
            select_fields = [f"({select_fields[0]})/(stats.minutes_played/90)"]
            filter_fields.append( ("stats.minutes_played", ">", MP_FILTER) )

        scoring_query[stat] = finalize_query(select_fields, filter_fields)
    return scoring_query

def shooting_stats():
    shooting_query = dict()
    for stat in ["shots", "shots_on"]:
        # select fields
        select_fields = [f"stats.{stat}"]

        # initialize filters
        filter_fields = [] + DEFAULT_FILTER

        # handle per 90
        if PER_90 is True:
            select_fields = [f"({select_fields[0]})/(stats.minutes_played/90)"]
            filter_fields.append( ("stats.minutes_played", ">", MP_FILTER) )

        shooting_query[stat] = finalize_query(select_fields, filter_fields)
    return shooting_query

def passing_stats():
    passing_query = dict()
    for stat in ["passes_key", "passes", "passes_accuracy"]:
        # select_fields
        select_fields = [f"stats.{stat}"]

        # initialize filters
        filter_fields = [] + DEFAULT_FILTER

        # handle passes accuracy
        if stat == "passes_accuracy":
            filter_fields.append( ("stats.passes", ">", PASS_FILTER) )
        # handle per 90
        elif PER_90 is True:
            select_fields = [f"({select_fields[0]})/(stats.minutes_played/90)"]
            filter_fields.append( ("stats.minutes_played", ">", MP_FILTER) )

        passing_query[stat] = finalize_query(select_fields, filter_fields)
    return passing_query

def dribbling_stats():
    dribbling_query = dict()
    for stat in ["dribbles_succeeded", "dribbles_attempted", "dribbles_succeeded_pct"]:
        # select_fields
        select_fields = [f"stats.{stat}"]

        # initialize filters
        filter_fields = [] + DEFAULT_FILTER

        # handle dribbles succeeded pct
        if stat == "dribbles_succeeded_pct":
            filter_fields.append( ("stats.dribbles_attempted", ">", DRIBBLE_FILTER) )
        # handle per 90
        elif PER_90 is True:
            select_fields = [f"({select_fields[0]})/(stats.minutes_played/90)"]
            filter_fields.append( ("stats.minutes_played", ">", MP_FILTER) )
 
        dribbling_query[stat] = finalize_query(select_fields, filter_fields)
    return dribbling_query 

def defending_stats(season):
    defending_query = dict()
    if int(season) < 2017:
        stats = ["interceptions"]
    else:
        stats = ["tackles", "interceptions", "blocks"]
    for stat in stats:
        select_fields = [f"stats.{stat}"]

        # initialize filters
        filter_fields = [] + DEFAULT_FILTER

        # handle per 90
        if PER_90 is True:
            select_fields = [f"({select_fields[0]})/(stats.minutes_played/90)"]
            filter_fields += [("stats.minutes_played", ">", MP_FILTER)]

        defending_query[stat] = finalize_query(select_fields, filter_fields)
    return defending_query

def other_stats():
    other_query = dict()
    for stat in ["rating", "goals_conceded", "penalties_saved"]:
        # select_fields
        select_fields = [f"stats.{stat}"]

        # initialize filters
        filter_fields = [] + DEFAULT_FILTER

        # handle per 90
        if PER_90 is True or stat != "penalties_saved":
            filter_fields.append( ("stats.minutes_played", ">", MP_FILTER) )
        if PER_90 is True and stat == "goals_conceded":
            select_fields = [f"({select_fields[0]})/(stats.minutes_played/90)"]

        if stat != "rating":
            filter_fields.append( ("stats.position", "=", "Goalkeeper") )

        # finalize filters 
        filter_fields = [(filter_fields, "AND")]

        # order_by 
        order_by_stat = select_fields[0]
        order_field = (([order_by_stat], True)
                       if stat != "goals_conceded"
                       else ([order_by_stat], False))

        other_query[stat] = rank_response(select_fields, filter_fields, order_field)
    return other_query

##########################
##### MAIN FUNCTION ######
##########################

def dashboard_stats(league, season, per_90):
    num_stats = get_num_stats(league, season)
    if not num_stats:
        return dict()

    global PER_90
    PER_90 = per_90

    global DEFAULT_FILTER
    DEFAULT_FILTER = [("stats.season", "=", season)]

    if league == "Top-5":
        DEFAULT_FILTER.append( ("stats.league_id", "IN", TOP_5) )
    else:
        DEFAULT_FILTER.append( ("stats.league_id", "=", league) )

    global DRIBBLE_FILTER
    DRIBBLE_FILTER = str(get_max("stats.dribbles_attempted", league, season)/5)

    global MP_FILTER
    MP_FILTER = str(get_max("stats.minutes_played", league, season)/5)

    global PASS_FILTER
    PASS_FILTER = str(get_max("stats.passes", league, season)/5)

    global SHOT_FILTER
    SHOT_FILTER = str(get_max("stats.shots", league, season)/5)

    query_result = dict()
    query_result["scoring"] = scoring_stats()
    query_result["shooting"] = shooting_stats()
    query_result["passing"] = passing_stats()
    query_result["dribbling"] = dribbling_stats()
    query_result["defending"] = defending_stats(season)
    query_result["other"] = other_stats()

    return query_result
