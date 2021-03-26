from .models import Country, Season, League, Team, Player, PlayerStat 

def valid_team(id):
    print(f"team id: {id}")
    return id == "" or len(Team.objects.filter(id=int(id))) > 0

def valid_league(id):
    print(f"league id: {id}")
    return id == "" or len(League.objects.filter(league_id=int(id))) > 0

def valid_season(start_year):
    return len(Season.objects.filter(start_year=start_year)) > 0

def valid_number(n_str):
    if '.' not in n_str: return n_str.isdecimal()
    split_n_str = n_str.split('.')
    return split_n_str[0].isdecimal() and split_n_str[1].isdecimal()

def valid_position(pos):
    return pos == "" or PlayerStat.get_position(pos) != PlayerStat.DEFAULT_POSITION

def valid_country(id):
    return id == "" or len(Country.objects.filter(id=int(id))) > 0

def valid_logical_op(op):
    return op in ["", "<", ">", "=", "><"]

def valid_arith_op(op):
    return op in ["", "*", "/", "+", "-"]

def add_error(errors, key, message):
    if key in errors:
        errors[key].append(message)
    else:
        errors[key] = [message]

def query_validator(postData):
    errors = {}

    #### REQUIRED VALIDATIONS ####
    # ensure that at least one select stat is selected
    if postData["selectStats"][0]["firstStat"] == "":
        add_error(errors, "selectStatsErrors", "At least one select field must be specified")
    # ensure that a season is selected
    if postData["season_start"] == "":
        add_error(errors, "seasonErrors", "Season field is required")
    if len(errors) > 0: 
        print(errors)
        return errors

    ###### OTHER VALIDATIONS ######
    # ensure that season is valid
    if not valid_season(postData["season_start"]):
        add_error(errors, "seasonErrors", "Season field is invalid")
    # ensure that select stats are valid
    # ...
    # ensure that league filter is valid
    if not valid_league(postData["league_id"]):
        add_error(errors, "leagueErrors", "League field is invalid")
    # ensure that team-league filter and team are valid
    if not valid_team(postData["team"]["id"]):
        add_error(errors, "teamErrors", "Club field is invalid")
    if not valid_league(postData["team"]["league_id"]):
        add_error(errors, "teamErrors", "League input for Club field is invalid")
    # ensure that filter minutesPlayed is valid
    if not valid_logical_op(postData["minutesPlayed"]["logicalOp"]):
        add_error(errors, "minutesPlayedErrors", "Logical operator for Minutes Played field is invalid")
    if postData["minutesPlayed"]["logicalOp"] != "" and not valid_number(postData["minutesPlayed"]["firstVal"]):
        add_error(errors, "minutesPlayedErrors", "First value for Minutes Played field is invalid")
    if postData["minutesPlayed"]["logicalOp"] == "><" and not valid_number(postData["minutesPlayed"]["secondVal"]):
        add_error(errors, "minutesPlayedErrors", "Second value for Minutes Played field is invalid")
    # ensure that filter stats are valid
    # ...
    # ensure that filter age is valid
    if not valid_logical_op(postData["age"]["logicalOp"]):
        add_error(errors, "ageErrors", "Logical operator for Age field is invalid")
    if postData["age"]["logicalOp"] != "" and not valid_number(postData["age"]["firstVal"]):
        add_error(errors, "ageErrors", "First alue for Age field is invalid")
    if postData["age"]["logicalOp"] == "><" and not valid_number(postData["age"]["secondVal"]):
        add_error(errors, "ageErrors", "Second value for Age field is invalid")
    # ensure that filter nationality is valid
    if not valid_country(postData["country"]):
        add_error(errors, "nationalityErrors", "Nationality field is invalid")
    # ensure that filter position is valid
    if not valid_position(postData["position"]):
        add_error(errors, "positionErrors", "Position field is invalid")
    # ensure that order by stat is valid
    # ...
    print(errors)
    return errors

def get_query_result(postData):
    return