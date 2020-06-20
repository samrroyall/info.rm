#!/usr/bin/env python3

from config import write_config
from db import initialize_engine, modify_db_row 
from manifest import set_manifest_arg, get_manifest_arg
from orm import Leagues, Teams, Players, Stats
from parser import initialize_parser
from request import Request

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

########################
####### HELPERS ########
########################

def get_data(action, engine, season):
    """ Function for updating specific table data from API and storing in DB """
    request_type = Request.get_registry().get(f"{action.capitalize()}Request")

    # for league and teams endpoint
    response_ids = dict()
    processed_data = []

    # for players endpoint
    processed_players = dict()
    processed_stats = dict()

    # league requests do not require ids from prior calls
    if action == "leagues":
        result = request_type(season).update()
        response_ids.update(result.get("ids"))
        processed_data += result.get("processed_data")
    # player and team requests do require ids from prior calls
    else:
        # get ids
        ids = get_manifest_arg("league_ids") if action == "teams" else get_manifest_arg("team_ids", season)
        assert ids is not None, \
            f"ERROR: Required IDs not present for {action} procedure."

        # make requests
        for id in ids.keys():
            if action == "teams":
                result = request_type(id, season).update()
                response_ids.update(result.get("ids"))
                processed_data += result.get("processed_data")
            elif action == "players":
                processed_players, processed_stats = request_type(
                                                            id, 
                                                            processed_players, 
                                                            processed_stats,
                                                            season
                                                        ).update()
                print("INFO: Response for {0} Obtained Successfully...".\
                    format(ids.get(id).get("team_name")))

               
    # update manifest with new IDs
    if action == "players": 
        set_manifest_arg("player_ids", set(processed_players.keys()))
        return {"players": processed_players.values(), "stats": processed_stats.values()}
    else:
        if action == "leagues":
            set_manifest_arg("league_ids", response_ids)
        elif action == "teams":
            set_manifest_arg("team_ids", response_ids, season)
        return processed_data

def setup(args):
    """ Function for writing arguments to config file."""
    config_args = {
        "token": args.get("token"),
        "subscription_time": args.get("subscription_time")
    }
    write_config(config_args)
    set_manifest_arg("leagues", args.get("leagues"))

def update_db(engine, action, processed_data):
    """ Function that calls the modify_db_row() function on each processed row.
    """
    for processed_vals in processed_data:
       session = modify_db_row(engine, processed_vals, eval(action.capitalize()))
       session.close()

#######################
#### MAIN FUNCTION ####
#######################

def main(**kwargs):
    """ info.rm.py's db modification utility.
        action :: desired procedure
            leagues
            teams
            players
            setup
    """
    action = kwargs.get("action")
    if action == "setup":
        del kwargs["action"]
        setup(kwargs)
    else:
        engine = initialize_engine()
        season = kwargs.get("current_season").split("-")[0]
        processed_data = get_data(action, engine, season)
        if action == "players":
            update_db(engine, action, processed_data.get("players"))
            update_db(engine, "stats", processed_data.get("stats"))
        else:
            update_db(engine, action, action_type, processed_data)

if __name__ == "__main__":
    args = vars(initialize_parser())
    args["leagues"] = LEAGUES
    main(**args)
