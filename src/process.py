#!/usr/bin/env python3

from datetime import datetime
from typing import Dict, Any, Optional, Type

from config import get_config_args
from orm import Leagues, Teams, Players, Base

###########################
##### PROCESS HELPERS #####
###########################

def get_alternative_league_name(league_name):
    if league_name == "Bundesliga 1":
        return "Bundesliga"
    elif league_name == "Primera Division":
        return "La Liga"
    else:
        return None

#############################
##### PROCESS FUNCTIONS #####
#############################

def process_leagues(leagues: Dict[str, Any], _) -> Dict[str, Any]:
    """ Function to process the API response regarding league data. """
    orm_class: Type[Base] = Leagues
    # attributes: Dict[str, Any] = getattr(orm_class, "_TYPES")
    current_leagues = get_config_args("current_leagues")

    leagues_id = []
    filtered_leagues = []
    for league in leagues:
        if f"{league.get('name')},{league.get('country')}" in current_leagues:
            league["season_start"] = datetime.strptime(
                                         league.get("season_start"),
                                         "%Y-%m-%d"
                                     ).date()
            league["season_end"] = datetime.strptime(
                                       league.get("season_end"),
                                       "%Y-%m-%d"
                                   ).date()
            league["is_current"] = bool(league.get("is_current"))
            league_ids.append({league.get("league_id"):league.get("name")})
            filtered_leagues.append(league)
    return {"ids":league_ids,"processed_data":filtered_leagues}

def process_teams(teams: Dict[str, Any], league_id: int) -> Dict[str, Any]:
    """ Function to process the API response regarding team data. """
    league_name: str = get_config_args("league_ids").get(league_id)
    orm_class: Type[Base] = Teams
    #attributes: Dict[str, Any] = getattr(orm_class, "_TYPES")

    team_ids = []
    for team in teams:
        team["league_id"] = league_id 
        team["league_id"] = league_name
        team_ids.append({
            team.get("team_id"):{
                "team_name":team.get("name"),
                "league_name":league_name,
                "league_id":league_id
            }
        })
    return {"ids":team_ids,"processed_data":teams}


    
def process_player(players: Dict[str, Any], foreign_key: str) -> Dict[str, Any]:
    team_id: int = int(foreign_key)
    team_name: str = foreign_key.get("team_name")
    league_id: str = foreign_key.get("league_id")
    league_name: str = foreign_key.get("league_name")
    orm_class: Type[Base]  = Players
    attributes: Dict[str, Any] = getattr(orm_class, "_TYPES")

    filtered_players = {}
    for player in players_data:
        if player.get("league") == self.league_name or (self.alt_league_name and player.get("league") == self.alt_league_name):
            player["uid"] = md5((f"{player.get('player_id')}{player.get('team_id')}{player.get('league')}").encode()).hexdigest()
            # check for duplicates
            if player.get("uid") in filtered_players.keys():
                # check which instance is most recent
                if player.get("games").get("minutes_played") and (player.get("games").get("minutes_played") 
                                                                    > filtered_players[player.get("uid")].get("minutes_played")):
                    player = self.temp_func(player)
                else:
                    continue
            else:
                player = self.process_player(player)
            filtered_players[player.get("uid")] = player
    if action_type == "insert":
        filtered_players = [self.orm_class().from_json(instance) for instance in filtered_players.values()]
    elif action_type == "update":
        filtered_players = filtered_players.values()
    return {"ids":[],"processed_data":filtered_players}


def temp_func():
    # process player data
    if player.get("weight"):
            player["weight"] = float(player.get("weight").split(" ")[0]) * 0.393701
    else:
        player["weight"] = None
    if player.get("height"):
        player["height"] = float(player.get("height").split(" ")[0]) * 2.20462
    else:
        player["height"] = None
    if player.get("rating"):
        player["rating"] = float(player.get("rating"))
    else:
        player["rating"] = None
    if player.get("captain"):
        player["captain"] = bool(player.get("captain"))
    else:
        player["captain"] = None
    if player.get("birth_date"):
        player["birth_date"] = datetime.strptime(player.get("birth_date"), "%d/%m/%Y").date()
    else:
        player["birth_date"] = None
    if player.get("position"):
        player["position"] = player.get("position").lower()
    else:
        player["position"] = None
    # shots
    player["shots_on"] = player.get("shots").get("on")
    player["shots"] = player.get("shots").get("total")
    if player.get("shots") and player.get("shots") > 0:
        player["shots_on_pct"] = round(100.0 * player.get("shots_on") / player.get("shots"))
    else:
        player["shots_on_pct"] = None
    # goals
    player["goals_conceded"] = player.get("goals").get("conceded")
    player["assists"] = player.get("goals").get("assists")
    player["goals"] = player.get("goals").get("total")
    # passes
    player["passes_key"] = player.get("passes").get("key")
    player["passes_accuracy"] = player.get("passes").get("accuracy")
    player["passes"] = player.get("passes").get("total")
    # tackles
    player["blocks"] = player.get("tackles").get("blocks")
    player["interceptions"] = player.get("tackles").get("interceptions")
    player["tackles"] = player.get("tackles").get("total")
    # duels
    player["duels_won"] = player.get("duels").get("won")
    player["duels"] = player.get("duels").get("total")
    if player.get("duels") and player.get("duels") > 0:
        player["duels_won_pct"] = round(100.0 * player.get("duels_won") / player.get("duels"))
    else:
        player["duels_won_pct"] = None
    # dribbles
    player["dribbles_attempted"] = player.get("dribbles").get("attempted")
    player["dribbles_succeeded"] = player.get("dribbles").get("success")
    if player.get("dribbles_attempted") and player.get("dribbles_attempted") > 0:
        player["dribbles_succeeded_pct"] = round(100.0 * player.get("dribbles_succeeded") / 
                                                    player.get("dribbles_attempted"))
    else:
        player["dribbles_succeeded_pct"] = None
    # fouls
    player["fouls_drawn"] = player.get("fouls").get("drawn")
    player["fouls_committed"] = player.get("fouls").get("committed")
    # cards
    player["cards_yellow"] = player.get("cards").get("yellow")
    player["cards_red"] = player.get("cards").get("red")
    player["cards_second_yellow"] = player.get("cards").get("yellowred")
    player["cards_straight_red"] = player.get("cards_red") - player.get("cards_second_yellow") 
    # pentalties
    player["penalties_won"] = player.get("penalty").get("won")
    player["penalties_committed"] = player.get("penalty").get("commited") # [sic]
    player["penalties_saved"] = player.get("penalty").get("saved")
    player["penalties_scored"] = player.get("penalty").get("success")
    player["penalties_missed"] = player.get("penalty").get("missed")
    if player.get("penalties_scored_pct") and player.get("penalties_scored_pct") > 0:
        player["penalties_scored_pct"] = round(100.0 * player.get("penalties_scored") / 
                                                    (player.get("penalties_scored") + 
                                                    player.get("penalties_missed")))
    else:
        player["penalties_scored_pct"] = None
    # games
    player["games_appearances"] = player.get("games").get("appearences") # [sic]
    player["minutes_played"] = player.get("games").get("minutes_played") # [sic]
    player["games_started"] = player.get("games").get("lineups") # [sic]
    player["games_bench"] = player.get("substitutes").get("bench") # [sic]
    player["substitutions_in"] = player.get("substitutes").get("in")
    player["substitutions_out"] = player.get("substitutes").get("out")
    new_player = {}
    for k, v in player.items():
        if hasattr(self.orm_class, k):
            new_player[k] = v
    return new_player

