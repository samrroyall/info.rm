#!/usr/bin/env python3

from orm import initialize_engine
from parser import initialize_parser
from tasks import setup, query_db, insert_all, update_table
from config import read_config, get_ids

##########################
#### PARSER FUNCTIONS ####
##########################


#######################
#### MAIN FUNCTION ####
#######################

def main(**kwargs):
    """ info.rm.py's main function.
        action :: desired procedure
            setup
            insert_all
            insert_leagues
            insert_teams
            insert_players
            update_players
    """
    action = kwargs.get("action")
    del kwargs["action"]
    if action == "setup":
        setup(kwargs)
    else:
        engine = initialize_engine()
        config_args = read_config()
        if action == "query_db":
            query_db(engine)
        elif action == "insert_all":
            insert_all(engine, **config_args)
        # handle update_players, and insert_*
        else:
            ids = get_ids(action, config_args)
            update_table(action, ids, engine, **config_args)

if __name__ == "__main__":
    args = vars(initialize_parser())
    main(**args)
