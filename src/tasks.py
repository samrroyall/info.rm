#!/usr/bin/env python3

import sys

from request import Request
from orm import Leagues, Teams, Players
from config import set_config_arg, get_config_arg, write_config
from db import previously_inserted

#from sqlalchemy import and_, update

def get_data(action, engine):
    """ Function for updating specific table data from API and storing in DB """
    endpoint = action.split("_")[1] 
    action_type = action.split("_")[0]
    request_type = Request.get_registry().get(f"{endpoint.capitalize()}Request")

    response_ids = []
    response_data = []
    # league requests do not require ids from prior calls
    if endpoint == "leagues":
        result = request_type().update()
        response_ids = result.get("ids")
        response_data = result.get("processed_data")
    # player and team requests do not require ids from prior calls
    elif endpoint == "teams" or endpoint == "players":
        # get ids
        id_type = "league_ids" if endpoint == "teams" else "team_ids"
        assert get_config_arg(id_type), \
            f"ERROR: Required IDs not present for {action} procedure."
        ids = eval(get_config_arg(id_type)).keys()
        # make requests
        for id in ids:
            if action_type == "insert":
                # ensure data has not been previously inserted into database
                assert not previously_inserted(engine, action, id), \
                    "ERROR: Attempt to insert data already present in DB stopped."
            elif action_type == "update":
                # ensure data has been previously inserted into database
                assert previously_inserted(engine, action, id), \
                    "ERROR: Attempt to update data not present in DB stopped."
            result = request_type(id).update()
            if result.get("ids"):
                response_ids += result.get("ids") 
            response_data = result.get("processed_data")
    # update config.ini with new IDs
    if len(response_ids) > 0:
        config_arg = f"{endpoint[:-1]}_ids"
        set_config_arg(config_arg, response_ids)
    return response_data

#def query_db(engine):
#    """ Function for querying data from DB """
#    # initialize database connection
#    count = 1
#    for f, l, t, s in query_database(engine):
#        print(f"{count}. {f+' '+l} ({t})\t{s}")
#        count += 1
        

def setup(config_args):
    """ Function for writing CLI arguments to config file.
        Parameters:
            token             :: API token to be used for future responses
            subscription_time :: Time current API subscription began (HH:MM)
            current_season    :: Current season (e.g. 2019-2020)
    """
    write_config(config_args)


