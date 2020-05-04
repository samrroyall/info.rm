#!/usr/bin/env python3

from db import previously_inserted
from orm import Leagues, Teams, Players
from request import Request
from config import write_config
from manifest import set_arg, get_arg

def get_data(action, engine, season):
    """ Function for updating specific table data from API and storing in DB """
    endpoint = action.split("_")[1] 
    action_type = action.split("_")[0]
    request_type = Request.get_registry().get(f"{endpoint.capitalize()}Request")

    # for league and teams endpoint
    response_ids = dict()
    processed_data = []

    # for players endpoint
    processed_players = dict()
    processed_stats = dict()
    #player_transfers = dict()

    # league requests do not require ids from prior calls
    if endpoint == "leagues":
        result = request_type(season).update()
        response_ids.update(result.get("ids"))
        processed_data += result.get("processed_data")
    # player and team requests do not require ids from prior calls
    else:
        if endpoint == "teams":
            ids = get_arg("league_ids")
        elif endpoint == "players":
            ids = get_arg("team_ids", season)

        assert ids is not None, \
            f"ERROR: Required IDs not present for {action} procedure."

        # make requests
        for id in ids.keys():
            if endpoint == "teams":
                result = request_type(id, season).update()
                response_ids.update(result.get("ids"))
                processed_data += result.get("processed_data")
            elif endpoint == "players":
                processed_players, processed_stats = request_type(
                                                            id, 
                                                            processed_players, 
                                                            processed_stats,
                                                            season
                                                        ).update()
                print("INFO: Response for {0} Obtained Successfully.".\
                    format(ids.get(id).get("team_name")))

               
    # update manifest with new IDs
    if endpoint == "players": 
        set_arg("player_ids", set(processed_players.keys()))
        return {"players": processed_players.values(), "stats": processed_stats.values()}
    else:
        if endpoint == "leagues":
            set_arg("league_ids", response_ids)
        elif endpoint == "teams":
            set_arg("team_ids", response_ids, season)
        return processed_data

def setup(args):
    """ Function for writing CLI arguments to config file.
        Parameters:
            token             :: API token to be used for future responses
            leagues           :: List of leagues to be tracked (e.g. 1 2 3 4 5)
            subscription_time :: Time current API subscription began (HH:MM)
    """
    config_args = {
        "token": args.get("token"),
        "subscription_time": args.get("subscription_time")
    }
    write_config(config_args)
    set_arg("leagues", args.get("leagues"))


