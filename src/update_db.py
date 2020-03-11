#!/usr/bin/env python3
import sys

from request import Request
from parser import initialize_parser
from orm import Leagues, Teams, Players
from tasks import setup, get_data, query_db
from db import initialize_engine, update_table, insert_into_table

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
            query_db
    """
    action = kwargs.get("action")
    if action == "setup":
        del kwargs["action"]
        setup(kwargs)
    else:
        engine = initialize_engine()
        if action == "query_db":
            query_db(engine)
        else:
            processed_data = get_data(action, engine)
            action_type = action.split("_")[0]
            if action_type == "insert":
                endpoint = action.split("_")[1]
                for processed_vals in processed_data:
                    orm_class = eval(endpoint.capitalize())()
                    session = insert_into_table(engine, orm_class.from_json(processed_vals))
                session.close()
            elif action_type == "update":
                for processed_vals in processed_data:
                    session = update_table(engine, processed_vals)
                session.close()

if __name__ == "__main__":
    args = vars(initialize_parser())
    main(**args)
