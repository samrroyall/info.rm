from .query import get_max, get_column, get_by, grab_columns
from .web_query import rank_response

########################
##### FORM INPUTS ######
########################

CURRENT_SEASON = "2019"
SEASONS = ["2019", "2018", "2017", "2016", "2015"]
lops = ["+","-","*","/"]
cops = ["<",">","=","><"]
positions = ["Attacker", "Midfielder", "Defender", "Goalkeeper"]
stats = {
    "Assists": "players.assists",
    "Successful_Dribbles": "players.dribbles_succeeded",
    "Successful_Dribbles_Percentage": "players.dribbles_succeeded_pct",
    "Attempted_Dribbles": "players.dribbles_attempted",
    "Goals": "players.goals",
    "Shots": "players.shots",
    "Shots_on_Target": "players.shots_on",
    "Shots_on_Target_Percentage": "players.shots_on_pct",
    "Penalties_Won": "players.penalties_won",
    "Penalties_Scored": "players.penalties_scored",
    "Penalties_Scored_Percentage": "players.penalties_scored_pct",
    "Penalties_Missed": "players.penalties_missed",
    "Passes": "players.passes",
    "Pass_Accuracy": "players.passes_accuracy",
    "Key_Passes": "players.passes_key",
    "Blocks": "players.blocks",
    "Interceptions": "players.interceptions",
    "Tackles": "players.tackles",
    "Penalties_Committed": "players.penalties_committed",
    "Goals_Conceded": "players.goals_conceded",
    "Player_Rating": "players.rating",
    "Penalties_Saved": "players.penalties_saved",
    "Red_Cards": "players.cards_red",
    "Straight_Red_Cards": "players.cards_straight_red",
    "Yellow_Cards": "players.cards_yellow",
    "Second_Yellow_Cards": "players.cards_second_yellow"
}

##############################
##### HELPER FUNCTIONS #######
##############################

def get_data():
    nations = dict()
    clubs_dict = dict()

    leagues = get_column("name", "leagues")
    leagues.sort()

    for season in SEASONS:
        temp_clubs = get_by(
                        "name",
                        "teams",
                        "league_name",
                        "name",
                        "leagues",
                        season
                    )
        for league in leagues:
            temp_clubs[league].sort()
        clubs_dict[season] = temp_clubs

        temp_nations = get_column("nationality", "players", season)
        temp_nations.sort()
        nations[season] = temp_nations

    return leagues, clubs_dict, nations

def check_input_value(input, type):
    if type == "stats":
        # int or float
        if not input.isdecimal():
            split = input.split(".")
            if not (split[0].isdecimal() or not split[1].isdecimal()) and input[0] != ".":
                return False
        return True

def check_cop_values(cop, input_one, input_two):
    if cop not in cops:
        return 0
    # check first input, handles empty case
    if not check_input_value(input_one, "stats"):
        return 0
    if cop == "><":
        # check second input, handles empty case
        if not check_input_value(input_two, "stats"):
            return 0
        # ensure first input is smaller
        if float(input_one) >= float(input_two):
            return 0
        return 2
    else:
        return 1

def get_stat_values(form_data_dict, type = "select"):
    values = []
    if type == "order":
        length = 1
    else:
        length = 3
    for i in range(1,length + 1):
        # check values
        if type == "select":
            field_one = form_data_dict[f"select_field1_{i}"]
            field_two = form_data_dict[f"select_field2_{i}"]
            lop = form_data_dict[f"select_op_{i}"]
            per90 = False if f"select_per90_toggle_{i}" not in form_data_dict.keys() else True
        elif type == "order":
            field_one = form_data_dict["order_field1"]
            field_two = form_data_dict["order_field2"]
            lop = form_data_dict["order_op"]
            per90 = False if "order_per90_toggle" not in form_data_dict.keys() else True
            desc = True if "asc_toggle" not in form_data_dict.keys() else False
        elif type == "filter":
            field_one = form_data_dict[f"stat_field1_{i}"]
            field_two = form_data_dict[f"stat_field2_{i}"]
            lop = form_data_dict[f"stat_lop_{i}"]
            input_one = form_data_dict[f"stat_input1_{i}"]
            input_two = form_data_dict[f"stat_input2_{i}"]
            cop = form_data_dict[f"stat_cop_{i}"]
            per90 = False if f"stat_per90_toggle_{i}" not in form_data_dict.keys() else True

        if field_one not in stats.keys():
            continue
        else:
            if field_two in stats.keys() and lop in lops:
                select_string = f"{stats.get(field_one)}{lop}{stats.get(field_two)}"
            elif field_two not in stats.keys() and lop == "":
                select_string = stats.get(field_one)
            else:
                continue
            if per90:
                select_string = f"({select_string})/(players.minutes_played/90.0)"
            if type == "select":
                values.append(select_string)
            elif type == "order":
                values = ([select_string], desc)
            elif type == "filter":
                cop_values = check_cop_values(cop, input_one, input_two)
                if cop_values == 0:
                    continue
                elif cop_values == 2:
                    values.append( (select_string, ">", input_one) )
                    values.append( (select_string, "<", input_two) )
                elif cop_values == 1:
                    values.append( (select_string, cop, input_one) )
    return values

#############################
##### QUERY FUNCTIONS #######
#############################

def default_stats():
    leagues, clubs_dict, nations = get_data()
    select_fields = [
        "players.rating",
        "players.goals",
        "players.assists"
    ]
    max_minutes_played = get_max("players.minutes_played", CURRENT_SEASON)
    filter_fields = [
        ([("players.minutes_played",">",str(max_minutes_played/3))],"")
    ]
    order_field = (["players.rating"], True)

    query_result = rank_response(select_fields, filter_fields, order_field, CURRENT_SEASON)
    return query_result, leagues, clubs_dict, nations

def custom_stats(form_data):
    form_data_dict = dict()

    # move form data into dict
    for field, value in form_data:
        form_data_dict[field] = value
    # get select values
    select_fields = get_stat_values(form_data_dict, "select")
    # get filter values
    filter_fields = []

    # get age and minutes_played values
    for key in ["age", "minutes_played"]:
        cop = form_data_dict[f"{key}_op"]
        input_one = form_data_dict[f"{key}_input1"]
        input_two = form_data_dict[f"{key}_input2"]
        key_string = f"players.{key}"
        cop_values = check_cop_values(cop, input_one, input_two)
        if cop_values == 2:
            filter_fields.append( (key_string, ">", input_one) )
            filter_fields.append( (key_string, "<", input_two) )
        elif cop_values == 1:
            filter_fields.append( (key_string, cop, input_one) )

    # get season in scope 
    season = form_data_dict.get("season_select")
    # make query
    leagues, clubs_dict, nations = get_data()

    # get club, league, nationality, position values
    for key in ["club", "league", "nationality", "position"]:
        if key != "club":
            value = form_data_dict.get(f"{key}_select")
        if key == "position" and value and value in positions:
            key_string = "players.position"
        elif key == "league" and value and value in leagues:
            key_string = "teams.league_name"
        elif (key == "club" and form_data_dict.get("club_league_select") and
            value in clubs_dict.get(form_data_dict.get("club_league_select"))):
            key_string = "teams.name"
        elif key == "nationality" and value and value in nations.get(season):
              key_string = "players.nationality"
        else:
            continue
        filter_fields.append( (key_string, "=", value) )
    
    print(filter_fields)

    # get filter by stats
    stat_values = get_stat_values(form_data_dict, "filter")
    if len(stat_values) > 0:
        filter_fields += stat_values
    # finalize filter fields
    if len(filter_fields) > 0:
        filter_fields = [(filter_fields, "AND")]
    else:
        filter_fields = None
    # get order_by values
    order_field = get_stat_values(form_data_dict, "order")
    if len(order_field) == 0:
        order_field = ([select_fields[0]], True)
    
    try:
        query_result = rank_response(select_fields, filter_fields, order_field, season)
    except:
        query_result = "ERROR"
    return query_result, leagues, clubs_dict, nations, season
