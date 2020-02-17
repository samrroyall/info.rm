#!/usr/bin/env python3

import sys
import argparse
import pathlib
from request import Request
from orm import initialize_engine, Leagues, Teams, Players
from sqlalchemy.orm import sessionmaker, session
from sqlalchemy.exc import IntegrityError

##########################
#### HELPER FUNCTIONS ####
##########################

def initialize_parser():
    parser = argparse.ArgumentParser(description="""
            _       ____                     
           (_)___  / __/___    _________ ___ 
          / / __ \/ /_/ __ \  / ___/ __ `__ \ 
         / / / / / __/ /_/ / / /  / / / / / /
        /_/_/ /_/_/  \____(_)_/  /_/ /_/ /_/ 
        """, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "action",
        type = str,
        choices = [
            "setup",
            "update_all",
            "update_leagues",
            "update_teams",
            "update_players",
            "query_db"
        ],
        help = "procedure to be run by info.rm"
    )
    parser.add_argument(
        "-t",
        "--token",
        type = str,
        dest = "token",
        help = "(setup only) the user's API-Football access token"
    )
    parser.add_argument(
        "-s",
        "--season",
        type = str,
        dest = "current_season",
        help = "(setup only) the season the user desires data on: 'YYYY-YYYY'"
    )
    parser.add_argument(
        "-st",
        "--subscription-time",
        type = str,
        dest = "subscription_time",
        help = "(setup only) the hour and minute a user's API-Football subscription began: 'HH:MM'"
    )    
    args = parser.parse_args()
    if args.action == "setup" and (not args.token or not args.current_season or not args.subscription_time):
        print("info.rm.py: error: setup procedure requires the following arguments: -t/--token, -s/--season, and -st/--subscription-time")
        parser.print_help()
        sys.exit(1)
    elif args.action != "setup" and (args.token or args.current_season or args.subscription_time):
        print(f"info.rm.py: error: {args.action} procedure takes no additional arguments")
        parser.print_help()
        sys.exit(1)
    else:
        return args

def initialize_session(engine):
    """ Function for initializing session with DB """
    Session = sessionmaker(bind=engine) 
    session = Session()
    return session

def read_config():
    """ Function for reading configuration information from config.ini """
    current_path = pathlib.Path(__file__).parent.absolute()
    config_args = {}
    with open(f"{current_path}/config.ini", "r") as f:
        for line in f.readlines():
            key_value_list = line.strip().split("=")
            config_args.update({key_value_list[0]:key_value_list[1]})
    return config_args

def write_config(kwargs):
    """ Function for writing configuration information from config.ini """
    current_path = pathlib.Path(__file__).parent.absolute()
    with open(f"{current_path}/config.ini", "w") as f:
        for key,value in kwargs.items():
            f.write(f"{key}={value}\n")

def get_ids(action, config_args):
    """ Function for reading IDs from config.ini """
    if action == "update_teams":
        key_string = "league_ids"
    elif action == "update_players":
        key_string = "team_ids"
    else:
        key_string = None
    if key_string and key_string in config_args:
        return eval(config_args.get(key_string))
    else:
        return None

def set_ids(id_dict):
    """ Function for writing IDs to config.ini """
    current_path = pathlib.Path(__file__).parent.absolute()
    config_args = read_config()
    config_args.update(id_dict)
    write_config(config_args)

##########################
#### ACTION FUNCTIONS ####
##########################

def update_table(action, ids, engine, **kwargs):
    """ Function for updating specific table data from API and storing in DB """
    request_type_string = "{}Request".format(action.split("_")[1].capitalize())
    request_type = Request.get_registry().get(request_type_string)
    orm_instances = []
    response_ids = []
    if action != "update_leagues" and not ids:
        print(f"ERROR: Required IDs not present for {action} procedure. Ensure that the setup and higher-level procedures have been run.")
        sys.exit(1)
    if ids:
        for id in ids:
            kwargs["foreign_key"] = id
            result = request_type(**kwargs).update()
            response_ids += result.get("ids")
            orm_instances += result.get("orm_data")
    else:
        result = request_type(**kwargs).update()
        response_ids = result.get("ids")
        orm_instances = result.get("orm_data")
    # initialize database connection
    session = initialize_session(engine)
    # add ORM instances from api_response to session
    session.add_all(orm_instances)
    # update database tables with api_response
    try:
        session.commit()
    except IntegrityError as ie:
        print("INFO: An attmempt to insert an existing row into the database was made.")
        print(ie)
    # update config.ini with new IDs
    key_string = f"{action.split('_')[1][:-1]}_ids"
    set_ids({key_string:response_ids})
    return response_ids

def update_all(engine, **kwargs):
    """ Function for updating all data from API and storing in DB """
    league_ids = update_table("update_leagues", None, engine, **kwargs)
    team_ids = update_table("update_teams", league_ids, engine, **kwargs)
    update_table("update_players", team_ids, engine, **kwargs)
    set_ids({"league_ids":league_ids,"team_ids":team_id})
    return

def query_db(engine):
    """ Function for querying data from DB """
    # initialize database connection
    session = initialize_session(engine) 
    orm_classes = [Leagues, Teams, Players]
    for orm_class in orm_classes:
        for row in session.query(orm_class):
            print(row)
        print()


def setup(kwargs):
    """ Function for writing CLI arguments to config file.
        Parameters:
            token             :: API token to be used for future responses
            subscription_time :: Time current API subscription began (HH:MM)
            current_season    :: Current season (e.g. 2019-2020)
    """
    write_config(kwargs)

#######################
#### MAIN FUNCTION ####
#######################

def main(**kwargs):
    """ info.rm.py's main function.
        action :: desired procedure
            setup
            update_all
            update_leagues
            update_teams
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
        elif action == "update_all":
            update_all(engine, **config_args)
        else:
            ids = get_ids(action, config_args)
            update_table(action, ids, engine, **config_args)

if __name__ == "__main__":
    args = vars(initialize_parser())
    main(**args)
