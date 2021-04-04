from django.db.models import F, FloatField, IntegerField, QuerySet
from django.db.models.functions import Cast 
from typing import Callable, Dict, List, Tuple, Union

from .card import BuilderCard, CardList
from .models import Country, Season, League, Team, Player, PlayerStat 
from .queryset import annotate_queryset, modify_queryset, filter_by_comparison, order_queryset
stat_list = [stat[0] for stat in PlayerStat.STATS]

############################
#### VALIDATION HELPERS ####
############################

def valid_team(id: str) -> bool:
    return id == "" or len(Team.objects.filter(id=int(id))) > 0

def valid_league(id: str) -> bool:
    return id == "" or len(League.objects.filter(league_id=int(id))) > 0

def valid_season(id: str) -> bool:
    return len(Season.objects.filter(id=int(id))) > 0

def valid_number(n_str: str) -> bool:
    if '.' not in n_str: return n_str.isdecimal()
    split_n_str = n_str.split('.')
    return split_n_str[0].isdecimal() and split_n_str[1].isdecimal()

def valid_position(pos: str) -> bool:
    return pos == "" or PlayerStat.get_position(pos) != PlayerStat.DEFAULT_POSITION

def valid_country(id: str) -> bool:
    return id == "" or len(Country.objects.filter(id=int(id))) > 0

def valid_arith_op(op: str) -> bool:
    return op in ["", "*", "/", "+", "-"]

def valid_logical_op(op: str) -> bool: 
    return op in ["<", ">", "=", "><"]

def add_error(errors: Dict[str, List[str]], key: str, message: str) -> None:
    if key in errors:
        errors[key].append(message)
    else:
        errors[key] = [message]

def check_comparison_val(
    errors: Dict[str, List[str]], 
    data: Dict[str, Union[str, int, float]], 
    error_key: str, 
    field_name: str
) -> None:
    if not valid_logical_op(data["logicalOp"]):
        add_error(errors, error_key, f"Logical operator for {field_name} field is invalid")
    if not valid_number(data["firstVal"]):
        add_error(errors, error_key, f"First value for {field_name} field is invalid")
    if data["logicalOp"] == "><" and ( data["firstVal"] > data["secondVal"] or 
        not valid_number(data["secondVal"])
    ):
        add_error(errors, error_key, f"Second value for {field_name} field is invalid")

def check_stat(
    errors: Dict[str, List[str]], 
    data: Dict[str, Union[str, int, float]], 
    error_key: str, 
    field_name: str
) -> None:
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

def query_validator(
    postData: Dict[str, Union[float, int]]
) -> Dict[str, List[str]]:
    errors: Dict[str, List[str]] = {}

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

def camelize(stat_name: str) -> str:
    camel_stat: str = stat_name.replace('_', ' ').title()
    return camel_stat

def get_comparison_field_name(stat: Dict[str, Union[int, float]]) -> str:
    if stat["arithOp"] == "":
        return camelize(stat['firstStat']) + "Float"
    return camelize(stat["firstStat"]) + " " + stat["arithOp"] + " " + camelize(stat["secondStat"])

def get_comparison_field_value(
    stat: Dict[str, Union[int, float]]
) -> Union[IntegerField, FloatField]:
    op_to_callable = {
        "/": lambda a, b: a/b,
        "*": lambda a, b: a*b,
        "+": lambda a, b: a+b,
        "-": lambda a, b: a-b,
    }
    if stat["arithOp"] == "":
        return Cast( F(stat["firstStat"]), FloatField() )
    return op_to_callable[stat["arithOp"]]( 
        Cast(F(stat["firstStat"]), FloatField()), 
        Cast(F(stat["secondStat"]), FloatField()) 
    )

########################
####### DB QUERY #######
########################

def get_queryset_lambdas(
    queryset: QuerySet, 
    post_data: Dict[str, Union[float, int]]
) -> QuerySet:
    # season lambda
    queryset_lambdas = [ lambda q: q.filter( team__season__id=int(post_data["seasonId"])) ]
    count = 1
    for stat in post_data["filterStats"]:
        if stat["firstStat"] == "" or stat["logicalOp"] == "": continue
        annotation_name = f"filterStat{count}"
        queryset_lambdas += [
            # new field annotation lambda
            lambda q: annotate_queryset(
                queryset=q, 
                field_value=get_comparison_field_value(stat),
                per_ninety=stat["perNinety"],
                annotation_name=annotation_name
            ),
            lambda q: filter_by_comparison(q, stat, annotation_name) # stat lambda
        ]
        count += 1
    # minutesPlayed lambda
    if post_data["minutesPlayed"]["logicalOp"] != "":
        queryset_lambdas.append( lambda q: filter_by_comparison(q, post_data["minutesPlayed"], "minutes_played") )
    # age lambda
    if post_data["age"]["logicalOp"] != "":
        queryset_lambdas.append( lambda q: filter_by_comparison(q, post_data["age"], "age") )
    # league/team lambda
    if post_data["leagueId"] != "" and post_data["team"]["id"] != "":
        queryset_lambdas.append( lambda q: q.filter(team__id=int(post_data["team"]["id"])) )
    elif post_data["leagueId"] != "" :
        queryset_lambdas.append( lambda q: q.filter(team__league__league_id=int(post_data["leagueId"])) )
    # nationality lambda
    if post_data["country"] != "":
        queryset_lambdas.append( lambda q: q.filter(player__nationality__id=int(post_data["country"])) )
    # position lambda
    if post_data["position"] != "":
        queryset_lambdas.append( lambda q: q.filter(position=PlayerStat.get_position(post_data["position"])) )
    return queryset_lambdas

def get_query_result(post_data: Dict[str, Union[int, float]]) -> BuilderCard:
    select_fields = { 
        get_comparison_field_name(stat): {
            "value": get_comparison_field_value(stat),
            "per_ninety": stat["perNinety"],
        }
        for stat in post_data["selectStats"] if stat["firstStat"] != ""
    }
    order_by_stat = (
        post_data["orderByStat"] if post_data["orderByStat"]["firstStat"]
        else post_data["selectStats"][0]
    )
    order_by_field = {
        "value": get_comparison_field_value(order_by_stat),
        "per_ninety": order_by_stat["perNinety"],
        "desc": (
            True if "lowToHigh" not in order_by_stat 
            else (not order_by_stat["lowToHigh"])
        )
        # "pct": ???
    }
    queryset = PlayerStat.objects.all()
    return CardList([
        BuilderCard.from_queryset(
            queryset=queryset,
            lambdas=get_queryset_lambdas(queryset, post_data),
            select_fields=select_fields,
            order_by_field=order_by_field
        )
    ])