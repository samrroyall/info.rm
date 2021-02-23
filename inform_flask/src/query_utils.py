#!/usr/bin/env python3

import json
import os
import pathlib
import sqlite3
import unidecode
from typing import List, Tuple, Optional, Dict, Any

file_path = pathlib.Path(__file__).parent.absolute()
db_path = os.path.join(str(file_path), "info.rm.db")

#################################
#### Public Function Helpers ####
#################################

FLOAT_STATS = [
    "stats.rating",
]

PCT_STATS = [
    "stats.shots_on_pct",
    "stats.passes_accuracy",
    "stats.duels_won_pct",
    "stats.dribbles_succeeded_pct",
    "stats.penalties_scored_pct",
]

# Bundesliga 1 (78),
# Ligue 1 (61), 
# Premier League (39), 
# Primera Division (140),
# Serie A (135)
TOP_5 = ["78", "61", "39", "140", "135"]
TOP_5_STR = "(78, 61, 39, 140, 135)"

stats_keys = {
    0: "id", 
    1: "player_id",
    2: "name", 
    3: "firstname", 
    4: "lastname", 
    5: "season", 
    6: "is_current",
    7: "league_id", 
    8: "league_name", 
    9: "team_id", 
    10: "team_name", 
    11: "position", 
    12: "rating", 
    13: "shots", 
    14: "shots_on", 
    15: "shots_on_pct",
    16: "goals",
    17: "goals_conceded",
    18: "assists",
    19: "passes",
    20: "passes_key",
    21: "passes_accuracy",
    22: "tackles",
    23: "blocks",
    24: "interceptions",
    25: "duels",
    26: "duels_won",
    27: "duels_won_pct",
    28: "dribbles_past",
    29: "dribbles_attempted",
    30: "dribbles_succeeded",
    31: "dribbles_succeeded_pct",
    32: "fouls_drawn",
    33: "fouls_committed",
    34: "cards_yellow",
    35: "cards_red",
    36: "penalties_won",
    37: "penalties_committed",
    38: "penalties_scored",
    39: "penalties_missed",
    40: "penalties_scored_pct",
    41: "penalties_saved",
    42: "games_appearances",
    43: "minutes_played",
    44: "games_started",
    45: "substitutions_in",
    46: "substitutions_out",
    47: "games_bench"
}

players_keys = {
    0: "id",
    1: "name",
    2: "firstname",
    3: "lastname",
    4: "age",
    5: "birth_date",
    6: "nationality",
    7: "flag",
    8: "height",
    9: "weight"
}

teams_keys = {
    0: "id",
    1: "name",
    2: "logo"
}

leagues_keys = {
    0: "id",
    1: "name",
    2: "type",
    3: "country",
    4: "logo",
    5: "flag"
}

static_keys = [
    "id", 
    "player_id",
    "name", 
    "firstname", 
    "lastname", 
    "season", 
    "league_id", 
    "league_name", 
    "team_id", 
    "team_name", 
    "position", 
    "rating"
]

pct_keys = [
    "shots_on_pct", 
    "passes_accuracy", 
    "duels_won_pct", 
    "dribbles_succeeded_pct",
    "penalties_scored_pct"
]
        

# format query result into a dict
def result_to_dict(
        query_result: List[str], 
        index_dict: Dict[int, str]
    ) -> Dict[str,str]:
    result = dict()
    for index, colname in index_dict.items():
        result[colname] = query_result[index]
    return result

def stats_to_per90( 
        formatted_result: List[str]
    ) -> Dict[str,Any]:
    minutes_played = float(formatted_result.get("minutes_played"))
    for key, value in formatted_result.items():
        if (key not in static_keys and
            key not in pct_keys and
            key != "minutes_played"):
            value = value if value is not None else 0
            formatted_result[key] = float(value) / (minutes_played / 90.0)
    return formatted_result

##########################
#### Public Functions ####
##########################

# used for default queries 
def get_max(
        stat: str,
        league: str,
        season: str
    ) -> float:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    if league is None:
        league_string = ""
    elif league == "Top-5":
        league_string = f" AND league_id IN {TOP_5_STR}"
    else:
        league_string = f" AND league_id = {league}"

    query_string = f"SELECT max({stat}) FROM stats WHERE season = {season}{league_string};"
    cursor.execute(query_string)
    query_result = list(cursor.fetchall()[0])[0]
    connection.commit()
    connection.close()
    return query_result

# used for player pages
def get_player_data(
        id: str,
        per_90: bool
    ) -> Dict[str, Any]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    result = dict() 

    # player info 
    cursor.execute(f"SELECT * FROM players WHERE id = {id};")
    player_result = list(cursor.fetchall()[0])
    connection.commit()
    if len(player_result) == 0:
        return None
    result["player"] = result_to_dict(player_result, players_keys)


    result["stats"] = dict()

    cursor.execute(f"SELECT * FROM stats WHERE player_id = {id};")
    stats_result = [list(stat) for stat in cursor.fetchall()]
    connection.commit()

    current_season = None
    current_index = None
    for i in range(len(stats_result)):
        stats_row = list(stats_result[i])
        formatted_row = result_to_dict(stats_row, stats_keys)
        # divide relevant stats by minutes played / 90
        if per_90 is True:
            formatted_row = stats_to_per90(formatted_row)

        # get season and set up result dictionary structure
        season = formatted_row.get("season")
        if season != current_season:
            current_season = season
            current_index = 0
            result["stats"][current_season] = dict()
        else:
            current_index += 1

        result["stats"][current_season][current_index] = dict()

        # get team logo
        team_id = formatted_row.get("team_id")
        cursor.execute(f"SELECT logo FROM teams WHERE id = {team_id};")
        team_logo = cursor.fetchall()[0][0]
        connection.commit()

        # get league flag
        league_id = formatted_row.get("league_id")
        cursor.execute(f"SELECT flag FROM leagues WHERE id = {league_id};")
        league_flag = cursor.fetchall()[0][0]
        connection.commit()

        result["stats"][current_season][current_index]["stats"] = formatted_row
        result["stats"][current_season][current_index]["team"] = {"logo": team_logo}
        result["stats"][current_season][current_index]["league"] = {"flag": league_flag}


    connection.close()
    return result

# used for builder form select fields
def get_select_data() -> Dict[str, Any]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    result = dict()

    # leagues stay static
    cursor.execute("SELECT DISTINCT name FROM leagues;")
    leagues_result = [tup[0] for tup in cursor.fetchall()]
    connection.commit()
    leagues_result.sort()
    result["leagues"] = leagues_result
    
    seasons = get_seasons()

    # clubs
    result["clubs"] = dict()
    for season in seasons:
        result["clubs"][season] = dict()
        for league in result.get("leagues"):
            # leagues stay static
            cursor.execute(f"SELECT DISTINCT team_name FROM stats WHERE season = {season} AND league_name = \"{league}\";")
            clubs_result = [tup[0] for tup in cursor.fetchall()]
            connection.commit()
            clubs_result.sort()
            result["clubs"][season][league] = clubs_result

    # get all nations
    cursor.execute("SELECT DISTINCT nationality FROM players;")
    nations_result = [tup[0] for tup in cursor.fetchall()]
    connection.commit()
    nations_result.sort()
    result["nations"] = nations_result

    return result

def get_leagues_dict() -> List[Tuple[str, int]]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get leagues
    cursor.execute("SELECT name, id FROM leagues;")
    leagues_result = cursor.fetchall()
    connection.commit()

    result = dict()
    for tup in leagues_result:
        result[str(tup[1])] = tup[0]
    return result 

def get_flags() -> List[Tuple[str, int]]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get leagues
    cursor.execute("SELECT flag, id FROM leagues;")
    leagues_result = cursor.fetchall()
    connection.commit()

    result = dict()
    for tup in leagues_result:
        result[str(tup[1])] = tup[0]
    return result

def get_world_leagues() -> List[int]:
# open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get leagues
    cursor.execute("SELECT id FROM leagues WHERE country = \"World\";")
    leagues_result = [int(tup[0]) for tup in cursor.fetchall()]
    connection.commit()
    return leagues_result 

def get_positions() -> List[str]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get positions
    cursor.execute("SELECT DISTINCT position FROM stats;")
    position_result = [tup[0] for tup in cursor.fetchall()]
    connection.commit()
    return position_result

def get_seasons() -> List[str]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get seasons
    cursor.execute("SELECT DISTINCT season FROM stats;")
    season_result = [str(tup[0]) for tup in cursor.fetchall()]
    connection.commit()
    return season_result 

def get_players() -> Dict[str, Any]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get players names and IDs
    cursor.execute("SELECT players.firstname, players.lastname, players.id FROM players;")
    player_result = cursor.fetchall()
    connection.commit()

    players = [] 
    for tup in player_result:
        name = f"{tup[0]} {tup[1]}"
        decoded_name = unidecode.unidecode(name.lower())
        id = tup[2]

        players.append({
            "name": decoded_name,
            "id": id
        })

    return players

def get_team_seasons(team_id: int) -> List[int]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get team data 
    cursor.execute(f"SELECT DISTINCT(stats.season) FROM stats JOIN teams ON stats.team_id=teams.id WHERE teams.id = {team_id};")
    season_data = cursor.fetchall()
    connection.commit()

    team_seasons = []
    for season in season_data:
        team_seasons.append(season[0])

    team_seasons.sort()
    return team_seasons

def get_team_players(team_id: int, season: int) -> Dict[str, Any]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get team data 
    cursor.execute(f"SELECT teams.name, teams.logo FROM teams WHERE teams.id = {team_id};")
    team_data = cursor.fetchall()
    connection.commit()
    team_name = team_data[0][0]
    team_logo = team_data[0][1]

    # get player data 
    cursor.execute(f"""
        SELECT players.firstname, players.lastname, players.id, stats.position 
        FROM stats 
        JOIN players ON stats.player_id=players.id
        WHERE stats.team_id={team_id} AND stats.season={season};
    """)
    team_player_result = cursor.fetchall()
    connection.commit()

    team_players = {}
    team_players["teams"] = {
        "name": team_name,
        "logo": team_logo
    }
    team_players["players"] = {}
    player_ids = set()
    for tup in team_player_result:
        if tup[1] not in player_ids:
            player_ids.add(tup[1])
        else:
            continue
        player_data = {
            "name": tup[0] + " " + tup[1],
            "id": tup[2]
        }
        position = tup[3]
        if position in team_players.get("players").keys():
            team_players["players"][position].append(player_data)
        else:
            team_players["players"][position] = [player_data]

    for position in team_players.get("players").keys():
        players = sorted(
            team_players.get("players").get(position),
            key=lambda p: p["name"]
        )
        team_players["players"][position] = players

    return team_players

def get_teams() -> Dict[str, Any]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get team names and IDs
    cursor.execute("SELECT teams.name, teams.logo, teams.id FROM teams;")
    team_result = cursor.fetchall()
    connection.commit()

    teams = [] 
    for tup in team_result:
        if (tup[0] is None or tup[1] is None or tup[2] is None):
            continue

        name = tup[0]
        decoded_name = unidecode.unidecode(name.lower())
        logo = tup[1] 
        id = tup[2]

        teams.append({
            "name": decoded_name,
            "logo": logo,
            "id": id
        })

    return teams

def get_leagues() -> Dict[str, Any]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get league names and IDs
    cursor.execute("SELECT leagues.name, leagues.logo, leagues.id FROM leagues;")
    team_result = cursor.fetchall()
    connection.commit()

    leagues = [] 
    for tup in team_result:
        if (tup[0] is None or tup[1] is None or tup[2] is None):
            continue

        name = tup[0]
        decoded_name = unidecode.unidecode(name.lower())
        logo = tup[1] 
        id = tup[2]

        leagues.append({
            "name": decoded_name,
            "logo": logo,
            "id": id
        })

    return leagues

def get_num_stats(league: str, season: str) -> int:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    if league is None:
        league_string = ""
    elif league == "Top-5":
        league_string = f" AND league_id IN {TOP_5_STR}"
    else:
        league_string = f" AND league_id = {league}"

    query_string = f"SELECT count(id) FROM stats WHERE season = {season}{league_string}"
    cursor.execute(query_string)
    query_result = list(cursor.fetchall()[0])[0]
    connection.commit()
    connection.close()
    return query_result

#################################
### Global Variable Functions ###
#################################

def get_top_five() -> List[str]:
    return TOP_5

def get_pct_stats() -> List[str]:
    return PCT_STATS

def get_float_stats() -> List[str]:
    return FLOAT_STATS

