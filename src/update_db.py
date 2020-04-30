#!/usr/bin/env python3
import sys

from db import initialize_engine, update_table, insert_into_table
from orm import Leagues, Teams, Players, Stats
from parser import initialize_parser
from tasks import setup, get_data

########################
### GLOBAL VARIABLES ###
########################

# Desired Leagues that do not carry player stats 
# FUTURE_LEAGUES = [
#   "Jupiler Pro League,Belgium",
#   "Premier League,Ukraine",
#   "Premiership,Scotland",
#   "Czech Liga,Czech-Republic"
# ]

LEAGUES = [
    # TOP 5
    "Bundesliga 1,Germany",
    "Ligue 1,France",
    "Premier League,England",
    "Primera Division,Spain",
    "Serie A,Italy",
    # OTHER
    "UEFA Champions League,World",
    "UEFA Europa League,World",
    "Primeira Liga,Portugal",
    "Premier League,Russia",
    "Eredivisie,Netherlands",
    "Super Lig,Turkey",
    "Tipp3 Bundesliga,Austria",
    "Superligaen,Denmark"
]

#######################
#### MAIN FUNCTION ####
#######################

def update_db(engine, endpoint, action_type, processed_data):
    for processed_vals in processed_data:
       if action_type == "insert":
           session = insert_into_table(engine, processed_vals, eval(endpoint.capitalize()))
       elif action_type == "update":
           session = update_table(engine, processed_vals, eval(endpoint.capitalize()))
       session.close()

def main(**kwargs):
    """ info.rm.py's db modification utility.
        action :: desired procedure
            insert_leagues
            insert_teams
            insert_players
            update_players
            setup
    """
    action = kwargs.get("action")
    if action == "setup":
        del kwargs["action"]
        setup(kwargs)
    else:
        season = kwargs.get("current_season").split("-")[0]
        engine = initialize_engine()
        processed_data = get_data(action, engine, season)
        action_type = action.split("_")[0]
        endpoint = action.split("_")[1]
        if endpoint == "players":
            processed_players = processed_data.get("players")
            update_db(engine, endpoint, action_type, processed_players)

            processed_stats = processed_data.get("stats")
            update_db(engine, "stats", action_type, processed_stats)
        else:
            update_db(engine, endpoint, action_type, processed_data)

if __name__ == "__main__":
    args = vars(initialize_parser())
    args["leagues"] = LEAGUES
    main(**args)
