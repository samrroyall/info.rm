#!/usr/bin/env python3

from request import Request
from tasks import setup, get_data
from parser import initialize_parser
from orm import Leagues, Teams, Players
from db import initialize_engine, update_table, insert_into_table

##########################
#### PARSER FUNCTIONS ####
##########################


#######################
#### MAIN FUNCTION ####
#######################

def main(**kwargs):
    """ info.rm.py's main function.
        action :: desired procedure
            insert_leagues
            insert_teams
            insert_players
            update_players
    """
    action = kwargs.get("action")
    if action == "setup":
        del kwargs["action"]
        setup(kwargs)
    else:
        engine = initialize_engine()
        response_data = get_data(action, engine)
        action_type = action.split("_")[0]
        if action_type == "insert":
            endpoint = action.split("_")[1]
            orm_class = eval(endpoint.capitalize())()
            orm_instances = [orm_class.from_json(instance) for instance in response_data]
            insert_into_table(engine, orm_instances)
        elif action_type == "update":
            update_table(engine, response_data)

if __name__ == "__main__":
    args = vars(initialize_parser())
    main(**args)
