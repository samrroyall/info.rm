#!/usr/bin/env python3

from .request import Request

########################
#### UPDATE METHODS ####
########################

def update_table(action, ids, **kwargs):
    """ Function for updating data from API and storing in DB
    """
    request = Request._REGISTRY.get(action.split("_")[1].capitalize())
    if ids:
        result = []
        for id in ids:
            kwargs["foreign_key"] = id
            data, ids = request(kwargs).update()
            result += data
    else:
        result, ids = request(kwargs).update()
    db.store_response()

    return ids

def update_all(**kwargs):
    league_ids = update_leagues(kwargs)
    kwargs["ids"] = league_ids
    team_ids = update_leagues(kwargs)
    kwargs["ids"] = team_ids
    update_leagues(kwargs)

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
            f.write(f"{key}={value}\n"

def read_config():
    with open("config.ini", "r") as f:
        args = {}
        for line in f.readlines():
            args.update({line.split("=")[0]:line.split("=")[1]})
        return args

def main(**kwargs)
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
    args = None # argparse result
    main(args)
