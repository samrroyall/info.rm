#!/usr/bin/env python3

from request import Request
from orm import Leagues, Teams, Players
from config import set_ids, write_config
from db import store_data, update_data, previously_inserted, query_database

import sys
from sqlalchemy import and_, update

def update_table(action, ids, engine, **kwargs):
    """ Function for updating specific table data from API and storing in DB """
    sub_action = action.split("_")[1] 
    action_type = action.split("_")[0]
    request_type = Request.get_registry().get(f"{sub_action.capitalize()}Request") # grab correct request class from Request registry
    response_ids = [] 
    # league requests do not require ids from prior calls
    if sub_action == "leagues":
        result = request_type(**kwargs).update("insert")
        response_ids = result.get("ids")
        store_data(engine, result.get("processed_data"))
    else:
        if not ids:
            print(f"ERROR: Required IDs not present for {action} procedure. Ensure that the setup and higher-level procedures have been run.")
            sys.exit(1)
        for id in ids:
            kwargs["foreign_key"] = id # points current Request class to previous Request class
            if action_type == "insert":
                id_name = "name" if sub_action == "teams" else "team_name"
                print(f"INFO: Attempting to insert rows for {id.get(id_name)}...")
                # ensure data has not been previously inserted into database
                if previously_inserted(engine, action, id):
                    print("ERROR: Attempt to insert data already present in DB stopped.")
                    continue
                result = request_type(**kwargs).update("insert")
                response_ids += result.get("ids") 
                store_data(engine, result.get("processed_data"))
            elif action_type == "update":
                # ensure data has been previously inserted into database
                if not previously_inserted(engine, action, id):
                    print("ERROR: Attempt to update data not present in DB stopped.")
                    continue
                result = request_type(**kwargs).update("update")
                update_data(engine, result.get("processed_data"))
    # update config.ini with new IDs
    if len(response_ids) > 0:
        key_string = f"{action.split('_')[1][:-1]}_ids"
        set_ids({key_string:response_ids})
    return response_ids

def insert_all(engine, **kwargs):
    """ Function for updating all data from API and storing in DB """
    league_ids = update_table("insert_leagues", None, engine, **kwargs)
    team_ids = update_table("insert_teams", league_ids, engine, **kwargs)
    update_table("insert_players", team_ids, engine, **kwargs)
    set_ids({"league_ids":league_ids,"team_ids":team_id})
    return

def query_db(engine):
    """ Function for querying data from DB """
    # initialize database connection
    for f, l, s in query_database(engine):
        print(f"{f+' '+l}\t{s}")
        

def setup(kwargs):
    """ Function for writing CLI arguments to config file.
        Parameters:
            token             :: API token to be used for future responses
            subscription_time :: Time current API subscription began (HH:MM)
            current_season    :: Current season (e.g. 2019-2020)
    """
    write_config(kwargs)


