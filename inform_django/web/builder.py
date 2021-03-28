from django.db.models import F, FloatField, IntegerField, QuerySet, Max
from django.db.models.functions import Cast 

from .models import Country, Season, League, Team, Player, PlayerStat 
stat_list = [stat[0] for stat in PlayerStat.STATS]

############################
#### VALIDATION HELPERS ####
############################

def valid_team(id):
    return id == "" or len(Team.objects.filter(id=int(id))) > 0

def valid_league(id):
    return id == "" or len(League.objects.filter(league_id=int(id))) > 0

def valid_season(id):
    return len(Season.objects.filter(id=int(id))) > 0

def valid_number(n_str):
    if '.' not in n_str: return n_str.isdecimal()
    split_n_str = n_str.split('.')
    return split_n_str[0].isdecimal() and split_n_str[1].isdecimal()

def valid_position(pos):
    return pos == "" or PlayerStat.get_position(pos) != PlayerStat.DEFAULT_POSITION

def valid_country(id):
    return id == "" or len(Country.objects.filter(id=int(id))) > 0

def valid_arith_op(op):
    return op in ["", "*", "/", "+", "-"]

def valid_logical_op(op):
    return op in ["<", ">", "=", "><"]

def add_error(errors, key, message):
    if key in errors:
        errors[key].append(message)
    else:
        errors[key] = [message]

def check_comparison_val(errors, data, error_key, field_name):
    if not valid_logical_op(data["logicalOp"]):
        add_error(errors, error_key, f"Logical operator for {field_name} field is invalid")
    if not valid_number(data["firstVal"]):
        add_error(errors, error_key, f"First value for {field_name} field is invalid")
    if data["logicalOp"] == "><" and ( data["firstVal"] > data["secondVal"] or 
        not valid_number(data["secondVal"])
    ):
        add_error(errors, error_key, f"Second value for {field_name} field is invalid")

def check_stat(errors, data, error_key, field_name):
    # skip empty stats
    if data["firstStat"] == "": return
    # for select, filter, and orderBy stats
    if not valid_arith_op(data["arithOp"]):
        add_error(errors, error_key, f"Arithmetic operator for {field_name} field is invalid")
    if data["firstStat"] != "" and not data["firstStat"] in stat_list:
        add_error(errors, error_key, f"First stat for {field_name} field is invalid")
    if data["arithOp"] != "" and not data["secondStat"] in stat_list:
        add_error(errors, error_key, f"Second stat for {field_name} field is invalid")
    if type(data["perNinety"]) != bool:
        add_error(errors, error_key, f"Per 90 toggle for {field_name} field is invalid")
    # for filter stats
    if "logicalOp" in data:
        check_comparison_val(errors, data, error_key, field_name)
    # for orderBy stats
    if "lowToHigh" in data and type(data["lowToHigh"]) != bool:
            add_error(errors, error_key, f"Low to High toggle for {field_name} field is invalid")

##########################
####### VALIDATION #######
##########################

def query_validator(postData):
    errors = {}

    ##### REQUIRED VALIDATIONS #####
    # ensure that at least one select stat is selected
    if postData["selectStats"][0]["firstStat"] == "":
        add_error(errors, "selectStatsErrors", "At least one Select Stat must be specified")
    # ensure that a season is selected
    if postData["seasonId"] == "":
        add_error(errors, "seasonErrors", "Season field is required")
    if len(errors) > 0: 
        return errors

    ###### OTHER VALIDATIONS ######
    # ensure that season is valid
    if not valid_season(postData["seasonId"]):
        add_error(errors, "seasonErrors", "Season field is invalid")
    # ensure that select stats are valid
    for stat in postData["selectStats"]:
        check_stat(errors, stat, "selectStatsErrors", "Select Stat")
    # ensure that league filter is valid
    if not valid_league(postData["leagueId"]):
        add_error(errors, "leagueErrors", "League field is invalid")
    # ensure that team-league filter and team are valid
    if not valid_team(postData["team"]["id"]):
        add_error(errors, "teamErrors", "Club field is invalid")
    if not valid_league(postData["team"]["leagueId"]):
        add_error(errors, "teamErrors", "League input for Club field is invalid")
    # ensure that filter minutesPlayed is valid
    if postData["minutesPlayed"]["logicalOp"] != "":
        check_comparison_val(errors, postData["minutesPlayed"], "minutesPlayedErrors", "Minutes Played")
    # ensure that filter stats are valid
    for stat in postData["filterStats"]:
        check_stat(errors, stat, "filterStatsErrors", "Filter Stat")
    # ensure that filter age is valid
    if postData["age"]["logicalOp"] != "":
        check_comparison_val(errors, postData["age"], "ageErrors", "Age")
    # ensure that filter nationality is valid
    if not valid_country(postData["country"]):
        add_error(errors, "nationalityErrors", "Nationality field is invalid")
    # ensure that filter position is valid
    if not valid_position(postData["position"]):
        add_error(errors, "positionErrors", "Position field is invalid")
    # ensure that order by stat is valid
    check_stat(errors, postData["orderByStat"], "orderByStatErrors", "Order By Stat")

    return errors

#######################
#### QUERY HELPERS ####
#######################

def camelize(stat_name):
    camel_stat = stat_name.replace('_', ' ').title().replace(' ', '')
    return camel_stat[0].lower() + camel_stat[1:]

def get_arith_annotation_name(stat1, op, stat2, per_ninety):
    op_to_word = {
        "/": "Over",
        "*": "Times",
        "+": "Plus",
        "-": "Minus",
    }
    return f"{ camelize(stat1) }{ op_to_word[op] }{ camelize(stat2) }{ 'Per90' if per_ninety is True else '' }"

def get_annotation_name(stat):
    if stat["arithOp"] == "":
        return f"{ camelize(stat['firstStat']) }Float{ 'Per90' if stat['perNinety'] is True else '' }"
    return get_arith_annotation_name(stat["firstStat"], stat["arithOp"], stat["secondStat"], stat["perNinety"])

def get_arith_annotation_value(stat1, op, stat2):
    op_to_callable = {
        "/": lambda a, b: a/b,
        "*": lambda a, b: a*b,
        "+": lambda a, b: a+b,
        "-": lambda a, b: a-b,
    }
    if op == "/":
        annotation_value = op_to_callable[op]( Cast(F(stat1), FloatField()), Cast(F(stat2), FloatField()) )
    else:
        annotation_value = op_to_callable[op]( F(stat1), F(stat2) )
    return annotation_value

def get_annotation_value(stat):
    if stat["arithOp"] == "":
        annotation_value = Cast( F(stat["firstStat"]), FloatField() )
    else:
        annotation_value = get_arith_annotation_value(stat["firstStat"], stat["arithOp"], stat["secondStat"])
    per_ninety_value = Cast(F("minutes_played"), FloatField())/90.0
    return annotation_value if stat["perNinety"] is False else Cast(annotation_value, FloatField())/per_ninety_value

def annotate_queryset(queryset, stat, annotation_name = None):
    # annotate
    if annotation_name is None: annotation_name = get_annotation_name(stat)
    annotation_value = get_annotation_value(stat)
    annotation_map = { annotation_name: annotation_value }
    return queryset.annotate(**annotation_map), annotation_name

def filter_queryset(queryset, stat, field_name):
    # handle empty filters
    if stat["logicalOp"] == "": return queryset
    # filter
    if stat["logicalOp"] in (">", "><"):
        filter_map = { f"{field_name}__gt": float(stat["firstVal"]) } 
        queryset = queryset.filter(**filter_map)
    if stat["logicalOp"] in ("<", "><"):
        filter_map = { f"{field_name}__lt": float(stat["firstVal" if stat["logicalOp"] == "<" else "secondVal"]) }
        queryset = queryset.filter(**filter_map)
    if stat["logicalOp"] == "=":
        filter_map = { field_name: float(stat["firstVal"]) }
        queryset = queryset.filter(**filter_map)
    return queryset

########################
####### DB QUERY #######
########################

def get_filtered_queryset(queryset, post_data):
    for stat in post_data["filterStats"]:
        # handle empty stat filters
        if stat["firstStat"] == "": continue
        # annotate
        queryset, annotation_name = annotate_queryset(queryset, stat)
        # filter 
        queryset = filter_queryset(queryset, stat, annotation_name)

    # OTHER FILTERS
    # minutesPlayed
    queryset = filter_queryset(queryset, post_data["minutesPlayed"], "minutes_played")
    # age
    queryset = filter_queryset(queryset, post_data["age"], "age")
    # league and team
    if post_data["leagueId"] != "":
        if post_data["team"]["id"] != "":
            queryset = queryset.filter(team__id=int(post_data["team"]["id"]))
        else:
            queryset = queryset.filter(team__league__league_id=int(post_data["leagueId"]))
    # nationality
    if post_data["country"] != "":
        queryset = queryset.filter(player__nationality__id=int(post_data["country"]))
    # position
    if post_data["position"] != "":
        queryset = queryset.filter(position=PlayerStat.get_position(post_data["position"]))

    return queryset

def get_ordered_queryset(queryset, post_data):
    # default ordering is first select stat
    order_by_stat = ( 
        post_data["selectStats"][0] if post_data["orderByStat"]["firstStat"] == ""
        else post_data["orderByStat"]
    )
    # annotate queryset with order stat 
    queryset, _ = annotate_queryset(queryset, order_by_stat, "orderByStat")
    # annotate queryset with order_by field
    order_field = "-orderByStat" if post_data["orderByStat"]["lowToHigh"] is False else "orderByStat"
    return queryset.order_by(order_field)

def get_query_result(post_data):
    queryset = PlayerStat.objects.filter(team__season__id=int(post_data["seasonId"]))
    # filter queryset
    filtered_queryset = get_filtered_queryset(queryset, post_data)
    # order queryset 
    ordered_queryset = get_ordered_queryset(filtered_queryset, post_data)
    # return subset of ordered result
    return ordered_queryset[:50]