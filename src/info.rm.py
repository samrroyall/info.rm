#!/usr/bin/env python3

import argparse
import request.Request

########################
#### UPDATE METHODS ####
########################

def update_table(action, ids, **kwargs):
    """ Function for updating data from API and storing in DB
    """
    request = Request.get_registry().get(action.split("_")[1].capitalize())
    if ids:
        result = []
        response_ids = []
        for id in ids:
            kwargs["foreign_key"] = id
            data, id_data = request(kwargs).update()
            result += data
            response_ids += id_data
    else:
        result, response_ids = request(kwargs).update()
    db.store_response(result)

    return response_ids

def update_all(**kwargs):
    league_ids = update_table("update_leagues", None, kwargs)
    team_ids = update_table("update_teams", league_ids, kwargs)
    update_table("update_players", team_ids, kwargs)

    return 

def config(**kwargs):
    """ Function for writing CLI arguments to config file.
        Parameters:
            token             :: API token to be used for future responses
            subscription_time :: Hour current API subscription began
            current_season    :: Start year of current season (e.g. 2019, for the 2019-2020 season)
    """
    with open("config.ini", "w") as f:
        for key,value in kwargs:
            f.write(f"{key}={value}\n")

def read_config():
    args = {}
    with open("config.ini", "r") as f:
        for line in f.readlines():
            args.update({line.split("=")[0]:line.split("=")[1]})
    return args

def main(**kwargs):
    """ info.rm.py's main function.
        action :: desired procedure
            config
            update_all
            update_leagues
            update_teams
            update_players
    """
    action = kwargs.get("action")
    if action == "config":
        config(kwargs)
    else:
        args = read_config()
        ids = None # somefunction(action)
        if action == "update_all":
            ids = update_table("update_leagues", ids, args)
            ids = update_table("update_teams", ids, args)
            update_table("update_players", ids, args)
        else:
            update_table(action, ids, args)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""\
        >>>>>>>DESCRIPTION GOES HERE<<<<<<<
    """)
    parser.add_argument(
        "action",
        nargs = 1,
        type = str,
        choices = [
            "config",
            "update_all",
            "update_leagues",
            "update_teams",
            "update_players"
        ],
        help = "procedure to be run by info.rm"
    )
    parser.add_argument(
        "-t",
        "--token",
        nargs = 1,
        type = str,
        required = False,
        dest = "token",
        help = "the user's API-Football access token"
    )
    parser.add_argument(
        "-s",
        "--season",
        nargs = 1,
        type = str,
        required = False,
        dest = "current_season",
        help = "the season the user desires data on: 'YYYY-YYYY'"
    )
    parser.add_argument(
        "-st",
        "--subcription-time",
        nargs = 1,
        type = str,
        required = False,
        dest = "subscription_time",
        help = "the hour and minute a user's API-Football subscription began: 'HH:MM'"
    )
    args = parser.parse_args() 
    main(args)
