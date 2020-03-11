#!/usr/bin/env python3

from hashlib import md5
from datetime import datetime, date

from config import get_config_arg
from orm import Leagues, Teams, Players

###########################
##### PROCESS HELPERS #####
###########################

def get_alternative_league(league_name):
    if league_name == "Bundesliga 1":
        return "Bundesliga"
    elif league_name == "Primera Division":
        return "La Liga"
    else:
        return None

def generate_uid(player_id, team_id, league):
    uid_string = f"{player_id}{team_id}{league}"
    return md5(uid_string.encode()).hexdigest()

def process_height_weight(height, weight):
    if height: 
        height_in = float(height.split(" ")[0]) * 0.393701
        feet = int(height_in // 12)
        inches = round(height_in % 12)
        height = f"{feet}'{inches}\""
    if weight:
        weight_lb = round(float(weight.split(" ")[0]) * 2.20462)
        weight = f"{weight_lb} lbs"
    return height, weight

def process_birthdate(birthdate_str) -> date:
    if birthdate_str:
        birthdate_date = datetime.strptime(
                             birthdate_str,
                             "%d/%m/%Y"
                         ).date()
    return birthdate_date

# no type checking on functions dealing with JSON data
def check_keys(response_data, attributes):
    """ Function to fix response data types and remove unnecessary keys. """
    # cast keys to correct types, discard unneeded keys
    unneeded_keys = []
    for k, v in response_data.items():
        if k in attributes:
            type_func = attributes.get(k)
            if type_func != date and v is not None:
                response_data[k] = attributes.get(k)(v)
        else:
            unneeded_keys.append(k)

    # remove unneeded keys
    for key in unneeded_keys:
        del response_data[key]
    return response_data

def not_null(value):
    """ Function to turn quantitative stats to 0 if currently null. """
    return 0 if value is None else value

# no type checking on functions dealing with JSON data
def process_stats(stats, temp_player):
    # games
    player_game_info = stats.get("games")
    temp_player["position"] = player_game_info.get("position")
    temp_player["rating"] = player_game_info.get("rating")
    temp_player["captain"] = player_game_info.get("captain")
    temp_player["minutes_played"] = not_null(player_game_info.get("minutes"))
    temp_player["games_appearances"] = not_null(player_game_info.get("appearences")) #sic
    temp_player["games_started"] = not_null(player_game_info.get("lineups"))
    # substitutes
    player_sub_info = stats.get("substitutes")
    temp_player["games_bench"] = not_null(player_sub_info.get("bench"))
    temp_player["substitutions_in"] = not_null(player_sub_info.get("in"))
    temp_player["substitutions_out"] = not_null(player_sub_info.get("out"))
    # shots
    player_shot_info = stats.get("shots")
    temp_player["shots"] = not_null(player_shot_info.get("total"))
    temp_player["shots_on"] = not_null(player_shot_info.get("on"))
    temp_player["shots_on_pct"] = None
    # ensure >= 0 shots
    if temp_player.get("shots") > 0: 
        temp_player["shots_on_pct"] = round(temp_player.get("shots_on") * 100
                                            / temp_player.get("shots"))
    # goals
    player_goal_info = stats.get("goals")
    temp_player["goals"] = not_null(player_goal_info.get("total"))
    temp_player["goals_conceded"] = not_null(player_goal_info.get("conceded"))
    temp_player["assists"] = not_null(player_goal_info.get("assists"))
    # passes
    player_pass_info = stats.get("passes")
    temp_player["passes"] = not_null(player_pass_info.get("total"))
    temp_player["passes_key"] = not_null(player_pass_info.get("key"))
    temp_player["passes_accuracy"] = player_pass_info.get("accuracy")
    # tackles
    player_tackle_info = stats.get("tackles")
    temp_player["tackles"] = not_null(player_tackle_info.get("total"))
    temp_player["blocks"] = not_null(player_tackle_info.get("blocks"))
    temp_player["interceptions"] = not_null(player_tackle_info.get("interceptions"))
    # duels
    player_duel_info = stats.get("duels")
    temp_player["duels"] = not_null(player_duel_info.get("total"))
    temp_player["duels_won"] = not_null(player_duel_info.get("won"))
    temp_player["duels_won_pct"] = None
    # ensure >= 0 duels
    if temp_player.get("duels") > 0: 
        temp_player["duels_won_pct"] = round(temp_player.get("duels_won") * 100
                                                / temp_player.get("duels"))
    # dribbles
    player_dribble_info = stats.get("dribbles")
    temp_player["dribbles_past"] = not_null(player_dribble_info.get("past"))
    temp_player["dribbles_attempted"] = not_null(player_dribble_info.get("attempts"))
    temp_player["dribbles_succeeded"] = not_null(player_dribble_info.get("success"))
    temp_player["dribbles_succeeded_pct"] = None 
    # ensure >= 0 dribbles_attempted
    if temp_player.get("dribbles_attempted") > 0: 
        temp_player["dribbles_succeeded_pct"] = round(
                                            temp_player.get("dribbles_succeeded") 
                                            / temp_player.get("dribbles_attempted")
                                            * 100
                                        )
    # fouls
    player_foul_info = stats.get("fouls")
    temp_player["fouls_drawn"] = not_null(player_foul_info.get("drawn"))
    temp_player["fouls_committed"] = not_null(player_foul_info.get("committed"))
    # cards
    player_card_info = stats.get("cards")
    temp_player["cards_yellow"] = not_null(player_card_info.get("yellow"))
    temp_player["cards_red"] = not_null(player_card_info.get("red"))
    temp_player["cards_second_yellow"] = not_null(player_card_info.get("yellowred"))
    temp_player["cards_straight_red"] = (temp_player.get("cards_red") 
                                        - temp_player.get("cards_second_yellow"))
    # penalty
    player_pen_info = stats.get("penalty")
    temp_player["penalties_won"] = not_null(player_pen_info.get("won"))
    temp_player["penalties_scored"] = not_null(player_pen_info.get("scored"))
    temp_player["penalties_missed"] = not_null(player_pen_info.get("missed"))
    temp_player["penalties_saved"] = not_null(player_pen_info.get("saved"))
    temp_player["penalties_committed"] = not_null(player_pen_info.get("commited")) #sic
    temp_player["penalties_scored_pct"] = None
    if (temp_player.get("penalties_scored") > 0 or 
        temp_player.get("penalties_missed") > 0): 
        temp_player["penalties_scored_pct"] = round(
                                            temp_player.get("penalties_scored") /
                                            (temp_player.get("penalties_scored")
                                                + temp_player.get("penalties_missed"))
                                            * 100
                                        )   
    return temp_player
         
#############################
##### PROCESS FUNCTIONS #####
#############################

# no type checking on functions dealing with JSON data
def process_leagues(leagues, _):
    """ Function to process the API response regarding league data. """
    orm_class = Leagues
    attributes = getattr(orm_class, "_TYPES")
    current_leagues = eval(get_config_arg("leagues"))

    league_ids = dict()
    filtered_leagues = []
    for idx in range(len(leagues)):
        league = leagues[idx]
        league_name = league.get("league").get("name")
        league_country = league.get("country").get("name")
        if f"{league_name},{league_country}" in current_leagues:
            temp_league = dict()
            # seasons
            temp_league["season"] = league.get("seasons")[0].get("year")
            temp_league["season_start"] = datetime.strptime(
                                              league.get("seasons")[0].get("start"),
                                              "%Y-%m-%d"
                                          ).date()
            temp_league["season_end"] = datetime.strptime(
                                            league.get("seasons")[0].get("end"),
                                            "%Y-%m-%d"
                                        ).date()
            temp_league["is_current"] = bool(league.get("seasons")[0].get("current"))
            # league
            temp_league["name"] = league_name
            temp_league["id"] = league.get("league").get("id")
            temp_league["logo"] = league.get("league").get("logo")
            temp_league["type"] = league.get("league").get("type")
            # country
            temp_league["country"] = league_country
            temp_league["flag"] = league.get("country").get("flag")
            # generate output dict
            league_ids[temp_league.get("id")] = temp_league.get("name")
            filtered_leagues.append(check_keys(temp_league, attributes))
    return {"ids":league_ids,"processed_data":filtered_leagues}

# no type checking on functions dealing with JSON data
def process_teams(teams, league_id):
    """ Function to process the API response regarding team data. """
    league_name = eval(get_config_arg("league_ids")).get(league_id)
    orm_class = Teams
    attributes = getattr(orm_class, "_TYPES")

    team_ids = dict()
    for idx in range(len(teams)):
        team = teams[idx]
        temp_team = dict()
        temp_team["league_id"] = league_id 
        temp_team["league_name"] = league_name
        # team
        temp_team["id"] = team.get("team").get("id")
        temp_team["name"] = team.get("team").get("name")
        temp_team["logo"] = team.get("team").get("logo")
        temp_team["founded"] = team.get("team").get("founded")
        # coach
        temp_team["coach_name"] = team.get("coach").get("name")
        temp_team["coach_firstname"] = team.get("coach").get("firstname")
        temp_team["coach_lastname"] = team.get("coach").get("lastname")
        # venue
        temp_team["venue_name"] = team.get("venue").get("name")
        temp_team["venue_city"] = team.get("venue").get("city")
        temp_team["venue_capacity"] = team.get("venue").get("capacity")
        # generate output dict
        teams[idx] = check_keys(temp_team, attributes)
        team_ids[temp_team.get("id")] = {
            "team_name":temp_team.get("name"),
            "league_name":league_name,
            "league_id":league_id
        }
    return {"ids":team_ids,"processed_data":teams}

def process_players(players, team_id):
    """ Function to process the API response regarding player data. """
    config_values = eval(get_config_arg("team_ids")).get(team_id)
    league_name = config_values.get("league_name")
    alt_league_name = get_alternative_league(league_name)
    orm_class = Players
    attributes = getattr(orm_class, "_TYPES")

    filtered_players = dict()
    for idx in range(len(players)):
        player = players[idx]
        # check player
        # ensure only player stats for current leagues are being processed
        if isinstance(player.get("statistics"), list):
            player_stats = player.get("statistics")
        else:
            player_stats = [player.get("statistics")]
        for stats in player_stats:
            temp_player = dict()
            temp_league_name = stats.get("league").get("name")
            if temp_league_name != league_name and (not alt_league_name or 
                temp_league_name != alt_league_name):
                continue
            # use consistent league name
            # only store statistics on players that have played
            if (not stats.get("games").get("minutes") or 
                stats.get("games").get("minutes") == 0):
                continue
            # create uid
            temp_player["league_id"] = stats.get("league").get("id")
            temp_player["league_name"] = league_name
            temp_player["team_id"] = stats.get("team").get("id")
            temp_player["team_name"] = stats.get("team").get("name")
            temp_player["id"] = player.get("player").get("id")
            # if player league is current, create UID column 
            temp_player["uid"] = generate_uid(
                                temp_player.get("id"),
                                temp_player.get("team_id"),
                                temp_player.get("league")
                            )
            # check for duplicates, only process most recent versions
            if (temp_player.get("uid") in filtered_players and 
                stats.get("games").get("minutes") <= 
                filtered_players[temp_player.get("uid")].get("minutes_played")):
                continue
            # player 
            player_info = player.get("player")
            temp_player["name"] = player_info.get("name")
            temp_player["firstname"] = player_info.get("firstname")
            temp_player["lastname"] = player_info.get("lastname")
            temp_player["age"] = player_info.get("age")
            temp_player["nationality"] = player_info.get("nationality")
            temp_player["height"], temp_player["weight"] = process_height_weight(
                                                               player_info.get("height"),
                                                               player_info.get("weight")
                                                           )
            temp_player["birth_date"] = process_birthdate(
                                            player_info.get("birth").get("date")
                                        )
            temp_player = process_stats(stats, temp_player)
            processed_player = check_keys(temp_player, attributes)
            filtered_players[processed_player.get("uid")] = processed_player
    return {"ids": [], "processed_data": filtered_players.values()}


