#!/usr/bin/env python3

from db import previously_inserted
from orm import Leagues, Teams, Players
from request import Request

from config import set_config_arg, get_config_arg, write_config, config_exists

#from sqlalchemy import and_, update

def get_data(action, engine, season):
    """ Function for updating specific table data from API and storing in DB """
    assert config_exists(season), "ERROR: Config not present. Run `setup` procedure."
    endpoint = action.split("_")[1] 
    action_type = action.split("_")[0]
    request_type = Request.get_registry().get(f"{endpoint.capitalize()}Request")

    # for league and teams endpoint
    response_ids = dict()
    processed_data = dict()

    # for players endpoint
    processed_players = dict()
    processed_stats = dict()

    # league requests do not require ids from prior calls
    if endpoint == "leagues":
        result = request_type(season).update()
        response_ids = result.get("ids")
        processed_data.update(result)
    # player and team requests do not require ids from prior calls
    elif endpoint == "teams" or endpoint == "players":
        # get ids
        id_type = "league_ids" if endpoint == "teams" else "team_ids"
        assert get_config_arg(id_type, season), \
            f"ERROR: Required IDs not present for {action} procedure."
        ids = eval(get_config_arg(id_type, season))
        # make requests
        for id in ids.keys():

            # check DB before inserting
            if action_type == "insert":
                # ensure data has not been previously inserted into database
                #assert not previously_inserted(engine, action, id), \
                    #"ERROR: Attempt to insert data already present in DB stopped."
                pass
            # check DB before updating
            elif action_type == "update":
                # ensure data has been previously inserted into database
                #assert previously_inserted(engine, action, id), \
                    #"ERROR: Attempt to update data not present in DB stopped."
                pass

            if endpoint == "players":
                processed_players, processed_stats = request_type(id, processed_players, processed_stats, season).update()
                print(processed_players, processed_stats)
                print("INFO: Response for {0} Obtained Successfully.".\
                    format(ids.get(id).get("team_name")))

            elif endpoint == "teams":
                result = request_type(id, season).update()
                response_ids.update(result.get("ids"))
                if processed_data.get("processed_data") is None:
                    processed_data["processed_data"] = result.get("processed_data")
                else:
                    processed_data["processed_data"] += result.get("processed_data")
                
    # update config.ini with new IDs
    if endpoint == "players": 
        return {"players": processed_players.values(), "stats": processed_stats.values()}
    else:
        config_arg = f"{endpoint[:-1]}_ids"
        set_config_arg(config_arg, response_ids, season)
        processed_data = processed_data.get("processed_data")
        return processed_data

def setup(config_args):
    """ Function for writing CLI arguments to config file.
        Parameters:
            token             :: API token to be used for future responses
            leagues           :: List of leagues to be tracked (e.g. 1 2 3 4 5)
            subscription_time :: Time current API subscription began (HH:MM)
            current_season    :: Current season (e.g. 2019-2020)
    """
    write_config(config_args)


