from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.defaulttags import register
import json

from .builder import get_query_result, query_validator
from .card_data import get_dashboard_data, get_player_data, get_from_cache, insert_to_cache
from .queryset import get_max, modify_queryset
from .management.commands.helpers.config import top_five_league_ids, other_league_ids, international_league_ids
from .models import Country, Season, League, Team, Player, PlayerStat 

#################################
##### CUSTOM DJANGO FILTERS #####
#################################

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def fst(list):
    return list[0]

@register.filter
def snd(list):
    return list[1]

@register.filter
def split(str, char):
    return str.split(char)

#############################
########## HELPERS ##########
#############################

def get_current_season(start_year = None):
    default = Season.objects.all().order_by("-start_year")[0]
    if start_year is None:
        return default
    seasons = Season.objects.filter( start_year=start_year )
    if len(seasons) != 1:
        return default
    return seasons[0]

def get_per_ninety(request):
    if "per_ninety" not in request.session:
        request.session["per_ninety"] = False
    return request.session.get("per_ninety")

def get_card_data(season, per_ninety, league = None):
    # return stored result if present
    card_cache_data = get_from_cache(season, per_ninety, league)
    if card_cache_data is not None:
        return card_cache_data

    # generate dashboard cards 
    # current league(s)
    valid_leagues = [ 
        league if league is not None
        else League.objects.get(league_id=id) for id in top_five_league_ids 
    ]
    # initial queryset filter lambdas
    lambdas = [
        lambda q: q.filter(team__season=season),
        lambda q: q.filter(team__league__in=valid_leagues),
        lambda q: q.filter(minutes_played__gte=get_max(q, "minutes_played")/5)
    ]
    initial_queryset = modify_queryset(PlayerStat.objects.all(), lambdas)
    card_data = get_dashboard_data(initial_queryset, per_ninety)
    insert_to_cache(season, per_ninety, league, card_data)
    return card_data

def default_context(season = None):
    # grab current season
    current_season = get_current_season(season) 
    return {
        # navbar leagues
        "first_row_leagues": [ League.objects.get(league_id=id) for id in top_five_league_ids ],
        "second_row_leagues": [ League.objects.get(league_id=id) for id in other_league_ids ],
        # season data
        "current_season": current_season,
        "seasons": Season.objects.order_by("-start_year"),
    }

def get_player_cards(playerstats, per_ninety):
    card_dict = {}
    for playerstat in playerstats:
        card_dict[playerstat.team.id] = get_player_data(playerstat, per_ninety)
    return {
        "cards": card_dict,
        "teams": sorted([ps.team for ps in playerstats], key=lambda team: team.id)
    }

def get_all_leagues():
    leagues_dict = {}
    for league in League.objects.all():
        league_str = f"{league.league_id}@{league.name}"
        leagues_dict[league_str] = {}
        for team in league.teams.all():
            if team.season.start_year not in leagues_dict[league_str]:
                leagues_dict[league_str][team.season.start_year] = []
            leagues_dict[league_str][team.season.start_year].append(team)
    return leagues_dict
    
#############################
########## ROUTES ###########
#############################

def home(request):
    return redirect(f"/dashboard/{get_current_season().start_year}")

def dashboard(request, season):
    # create context dict
    context = default_context(season)
    # set/get per ninety
    context["per_ninety"] = get_per_ninety(request)
    # grab page card_data
    context["card_data"] = get_card_data(context["current_season"], context["per_ninety"])
    # render page
    return render(request, "dashboard.html", context)

def leagues(request, id, season):
    # create context dict
    context = default_context(season)
    # get league information 
    leagues = League.objects.filter( league_id=id )
    if len(leagues) != 1:
        return redirect("/")
    context["current_league"] = leagues[0]
    # set/get per ninety
    context["per_ninety"] = get_per_ninety(request)
    # grab page card_data
    context["card_data"] = get_card_data(context["current_season"], context["per_ninety"], context["current_league"])
    # render page
    return render(request, "dashboard.html", context)

def teams(request, id, season):
    # create context dict
    context = default_context(season)
    teams = Team.objects.filter( team_id=id, season=Season.objects.get(start_year=season) )
    # get current team
    context["current_team"] = teams[0]
    for team in teams:
        if team.league.league_id not in international_league_ids:
            context["current_team"] = team
    # get team seasons
    context["seasons"] = list(set([t.season for t in Team.objects.filter( team_id=id )]))
    # get current team's players
    context["current_playerstats"] = context["current_team"].stats.all()
    # get player positions 
    context["positions"] = [pos for pos in PlayerStat.POSITIONS if pos[0] != PlayerStat.DEFAULT_POSITION]
    # render page
    return render(request, "team.html", context)

def players(request, id, season):
    # create context dict
    context = default_context(season)
    # set/get per ninety
    context["per_ninety"] = get_per_ninety(request)
    # get current players
    players = Player.objects.filter(player_id=id)
    if len(players) != 1:
        return redirect("/")
    current_player = players[0]
    context["current_player"] = current_player 
    context["current_playerstats"] = current_player.stats.filter(
        team__season = context["current_season"]
    )
    # get player seasons
    context["seasons"] = list(set([ps.team.season for ps in current_player.stats.all()]))
    context["player_cards"] = get_player_cards(context["current_playerstats"], context["per_ninety"])
    # render page
    return render(request, "player.html", context)

def builder(request):
    # create context dict
    context = default_context()
    # get countries 
    context["countries"] = sorted(list(Country.objects.all()), key=lambda x: x.name)
    # get player positions 
    context["positions"] = [pos for pos in PlayerStat.POSITIONS if pos[0] != PlayerStat.DEFAULT_POSITION]
    # get player stats 
    context["stats"] = PlayerStat.STATS
    # get leagues/teams for each season
    context["leagues"] = get_all_leagues()
    # query result
    if "query_data" in request.session:
        context["builder_card"] = get_query_result(request.session["query_data"])
    return render(request, "builder.html", context)

#############################
####### POST REQUESTS #######
#############################

def change_per_ninety(request):
    if request.method != "POST" or not request.is_ajax():
        return redirect("/")
    per_ninety_val = request.POST.get("per_ninety") == "true"
    request.session["per_ninety"] = per_ninety_val
    return JsonResponse({"message": "Per Ninety value changed successfully"}, status=200) 

def make_query(request):
    if request.method != "POST" or not request.is_ajax():
        return redirect("/builder")
    post_data = json.loads(list(request.POST.keys())[0])
    # validate query
    errors = query_validator(post_data)
    if len(errors) > 0:
        return JsonResponse(errors, status=400) 
    request.session["query_data"] = post_data
    return JsonResponse({"result": "query was success"}, status=200)
