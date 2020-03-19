#!/usr/bin/env python3
import sys

from parser import initialize_parser
from orm import Leagues, Teams, Players
from tasks import setup, get_data
from db import initialize_engine, update_table, insert_into_table

#######################
#### MAIN FUNCTION ####
#######################

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
        engine = initialize_engine()
        processed_data = get_data(action, engine)
        action_type = action.split("_")[0]
        endpoint = action.split("_")[1]
        for processed_vals in processed_data:
            if action_type == "insert":
                orm_class = eval(endpoint.capitalize())()
                session = insert_into_table(engine, orm_class.from_json(processed_vals))
            elif action_type == "update":
                session = update_table(engine, processed_vals)
            session.close()

if __name__ == "__main__":
    args = vars(initialize_parser())
    main(**args)
