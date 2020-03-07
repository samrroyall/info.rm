#!/usr/bin/env python3

from datetime import datetime
from typing import Dict, Any, Optional, Type, Set, List

from config import get_config_args
from orm import Leagues, Teams, Players, Base

###########################
##### PROCESS HELPERS #####
###########################

def get_alternative_league_name(league_name: str) -> str:
    if league_name == "Bundesliga 1":
        return "Bundesliga"
    elif league_name == "Primera Division":
        return "La Liga"
    else:
        return None

def create_uid(player_id: int, team_id: int, league: str) -> str:
    uid_string = f"{player_id}{team_id}{league}"
    return md5(uid_string.encode()).hexdigest()

def process_height_weight(player: Dict[str, Any]) -> Dict[str, Any]:
    if player.get("weight"):
        weight_lb = round(float(player.get("weight").split(" ")[0]) * 2.20462)
        player["weight"] = f"{weight_lb} lbs"
    if player.get("height"): 
        height_in = float(player.get("height").split(" ")[0]) * 0.393701
        feet = int(height_in // 12)
        inches = round(height_in % 12)
        player["height"] = f"{feet}'{inches}\""
    return player

def process_birthdate(player: Dict[str, Any]) -> Dict[str, Any]:
    if player.get("birth_date"):
        player["birth_date"] = datetime.strptime(
                                   player.get("birth_date"),
                                   "%d/%m/%Y"
                               ).date()
    return player

def check_keys(
        response_data: Dict[str, Any], 
        attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
    """ Function to fix response data types and remove unnecessary keys. """
    # cast keys to correct types, discard unneeded keys
    unneeded_keys: List[str] = []
    for k, v in response_data.items():
        if k in attributes:
            response_data[k] = attributes.get(k)(v)
        else:
            unneeded_attrs.append(k)

    # remove unneeded keys
    for key in unneeded_keys:
        del response_data[key]
    return response_data

def process_stats(player: Dict[str, Any]) -> Dic[str, Any]:
    # shots
    temp_dict = player.get("shots")
    player["shots"] = temp_dict.get("total")
    player["shots_on"] = temp_dict.get("on")
    player["shots_on_pct"] = None
    # ensure shots exists and is != 0
    if player.get("shots"): 
        player["shots_on_pct"] = round(temp_dict.get("shots_on") * 100
                                       / temp_dict.get("shots"))
    # goals
    temp_dict = player.get("goals")
    player["goals"] = temp_dict.get("total")
    player["assists"] = temp_dict.get("assists")
    player["goals_conceded"] = temp_dict.get("conceded")
    # passes
    temp_dict = player.get("passes")
    player["passes"] = temp_dict.get("total")
    player["passes_key"] = temp_dict.get("key")
    player["passes_accuracy"] = player.get("passes").get("accuracy")
    # tackles
    temp_dict = player.get("tackles")
    player["tackles"] = temp_dict.get("total")
    player["blocks"] = temp_dict.get("blocks")
    player["interceptions"] = temp_dict.get("interceptions")
    # duels
    temp_dict = player.get("duels")
    player["duels"] = temp_dict.get("total")
    player["duels_won"] = temp_dict.get("won")
    player["duels_won_pct"] = None
    # ensure duels exists and is != 0
    if player.get("duels"):
        player["duels_won_pct"] = round(player.get("duels_won") * 100 
                                        / player.get("duels"))
    # dribbles
    player["dribbles_attempted"] = temp_dict.get("attempted")
    player["dribbles_succeeded"] = temp_dict.get("success")
    player["dribbles_succeeded_pct"] = None
    if player.get("dribbles_attempted"):
        player["dribbles_succeeded_pct"] = round(player.get("dribbles_succeeded") * 100
                                                 / player.get("dribbles_attempted"))
    # fouls
    player["fouls_drawn"] = player.get("fouls").get("drawn")
    player["fouls_committed"] = player.get("fouls").get("committed")
    # cards
    player["cards_yellow"] = player.get("cards").get("yellow")
    player["cards_red"] = player.get("cards").get("red")
    player["cards_second_yellow"] = player.get("cards").get("yellowred")
    player["cards_straight_red"] = (player.get("cards_red") 
                                    - player.get("cards_second_yellow"))
    # pentalties
    player["penalties_won"] = player.get("penalty").get("won")
    player["penalties_committed"] = player.get("penalty").get("commited") # [sic]
    player["penalties_saved"] = player.get("penalty").get("saved")
    player["penalties_scored"] = player.get("penalty").get("success")
    player["penalties_missed"] = player.get("penalty").get("missed")
    player["penalties_scored_pct"] = None
    if player.get("penalties_scored") > 0 or 
        player.get("penalties_missed") > 0:
        player["penalties_scored_pct"] = round(player.get("penalties_scored") * 100
                                               / (player.get("penalties_scored")
                                                  + player.get("penalties_missed")))
    # games
    player["games_appearances"] = player.get("games").get("appearences") # [sic]
    player["minutes_played"] = player.get("games").get("minutes_played")
    player["games_started"] = player.get("games").get("lineups")
    player["games_bench"] = player.get("substitutes").get("bench")
    player["substitutions_in"] = player.get("substitutes").get("in")
    player["substitutions_out"] = player.get("substitutes").get("out")
    return player


#############################
##### PROCESS FUNCTIONS #####
#############################

def process_leagues(
        leagues: Dict[str, Any], 
        _
    ) -> Dict[str, Union[List[Dict[int, Any]], List[Dict[str, Any]]]]:
    """ Function to process the API response regarding league data. """
    orm_class: Type[Base] = Leagues
    attributes: Dict[str, Any] = getattr(orm_class, "_TYPES")
    current_leagues: Set[str] = get_config_args("current_leagues")

    leagues_id: List[Dict[int,Any]] = []
    filtered_leagues: List[Dict[str,Any]] = []
    for league in leagues:
        if f"{league.get('name')},{league.get('country')}" in current_leagues:
            league["season_start"]: datetime = datetime.strptime(
                                                   league.get("season_start"),
                                                   "%Y-%m-%d"
                                               ).date()
            league["season_end"]: datetime = datetime.strptime(
                                                 league.get("season_end"),
                                                 "%Y-%m-%d"
                                             ).date()
            league["is_current"]: bool = bool(league.get("is_current"))
            league_ids.append({
                league.get("league_id"):league.get("name")
            })
            filtered_leagues.append(check_keys(league, attributes))
    return {"ids":league_ids,"processed_data":filtered_leagues}

def process_teams(
        teams: Dict[str, Any],
        league_id: int
    ) -> Dict[str, Union[List[Dict[int, Any]], List[Dict[str, Any]]]]:
    """ Function to process the API response regarding team data. """
    league_name: str = get_config_args("league_ids").get(league_id)
    orm_class: Type[Base] = Teams
    attributes: Dict[str, Any] = getattr(orm_class, "_TYPES")

    team_ids: List[Dict[int,Any]] = []
    for idx in range(len(teams)):
        team = teams[idx]
        team["league_id"]: int = league_id 
        team["league_name"]: str = league_name
        teams[idx] = check_keys(team, attributes)
        team_ids.append({
            team.get("team_id"):{
                "team_name":team.get("name"),
                "league_name":league_name,
                "league_id":league_id
            }
        })
    return {"ids":team_ids,"processed_data":teams}

def process_player(
        players: Dict[str, Any],
        team_id: int
    ) -> Dict[str, Dict[str, Any]]:
    """ Function to process the API response regarding player data. """
    config_values: Dic[str, Union[str, int]] = get_config_args("team_ids").get(team_id)
    team_name: str = config_values.get("team_name")
    league_id: int = config_values.get("league_id")
    league_name: str = config_values.get("league_name")
    alt_league_name: Optional[str] = get_alternative_league(league_name)
    orm_class: Type[Base] = Players
    attributes: Dict[str, Any] = getattr(orm_class, "_TYPES")

    filtered_players: Dict[str, Dict[str, Any]] = {}
    for player in players_data:
        # ensure only player stats for current leagues are being processed
        if player.get("league") != league_name and (not alt_league_name or 
            player.get("league") != alt_league_name):
            continue
        # use consistent league name
        player["league"]: str = league_name
        # only store statistics on players that have played
        if not player.get("games").get("minutes_played") or 
            player.get("games").get("minutes_played") == 0:
            continue
        # if player league is current, create UID column 
        player["uid"]: str = generate_uid(
                                 player.get("player_id"),
                                 player.get("team_id"),
                                 player.get("league")
                             )
        # check for duplicates, only process most recent versions
        if (player.get("uid") in filtered_players and 
            player.get("games").get("minutes_played") <= 
            filtered_players[player.get("uid")].get("minutes_played")):
            continue
        # process player 
        player: Dict[str, Any] = check_keys(
                                    attributes,
                                    process_stats(process_birthdate(process_height_weight(player)))
                                 )
        filtered_players[player.get("uid")]: Dict[str, Any] = player
    return filtered_players.values()

