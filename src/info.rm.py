#!/usr/bin/env python3

import sys
import argparse
import pathlib
from request import Request
from orm import initialize_engine, Leagues, Teams, Players
from sqlalchemy import and_, update
from sqlalchemy.orm import sessionmaker, session
from sqlalchemy.exc import IntegrityError

##########################
#### PARSER FUNCTIONS ####
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
            "insert_all",
            "insert_leagues",
            "insert_teams",
            "insert_players",
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

#############################
#### DB HELPER FUNCTIONS ####
#############################

def update_data(engine, data):
    """ Function for initializing session with DB and updating existing Players rows"""
    Session = sessionmaker(bind=engine) 
    session = Session()
    # update DB rows
    for player in data:
        session.query(Players).filter(Players.uid == player.get("uid")).update(player)
        session.commit()
    session.close()

def store_data(engine, data):
    """ Function for initializing session with DB and inserting new rows"""
    Session = sessionmaker(bind=engine) 
    session = Session()
    # add ORM instances from api_response to session
    session.add_all(data)
    # update database tables with api_response
    try:
        session.commit()
        session.close()
    except IntegrityError as ie:
        print("INFO: An attmempt to insert an existing row into the database was made.")
        #print(ie)

def previously_inserted(engine, action, id):
    """ Function for ensuring duplicate DB insertions are not made"""
    Session = sessionmaker(bind=engine) 
    session = Session()
    query_result = None
    sub_action = action.split("_")[1]
    if sub_action == "teams":
        # check if table in DB
        if engine.has_table("Leagues"):
            query_result = session.query(Leagues.league_id).\
                    filter(Leagues.league_id == id.get("id"))
    elif sub_action == "players":
        # check if tables in DB
        if engine.has_table("Leagues") and engine.has_table("Teams"):
            league_id = session.query(Leagues.league_id).\
                    filter(Leagues.name == id.get("league_name"))[0][0]
            query_result = session.query(Teams.team_id, Teams.league_id).\
                    filter(
                            and_( 
                                Teams.team_id == id.get("id"), 
                                Teams.league_id == league_id
                            )
                    )
    if query_result and len(list(query_result)) > 0:
        return True
    elif query_result:
        return False
    else:
        print("ERROR: An error occurred in previously_inserted.")
        sys.exit(1)

##########################
#### CONFIG FUNCTIONS ####
##########################

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
    sub_action = action.split("_")[1]
    if sub_action == "teams":
        key_string = "league_ids"
    elif sub_action == "players":
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
    if action != "insert_leagues" and not ids:
        print(f"ERROR: Required IDs not present for {action} procedure. Ensure that the setup and higher-level procedures have been run.")
        sys.exit(1)
    if ids:
        sub_action = action.split("_")[0]
        for id in ids:
            kwargs["foreign_key"] = id
            if sub_action == "insert":
                # ensure data has not been previously inserted into database
                if previously_inserted(engine, action, id):
                    print("ERROR: Attempt to insert data already present in DB stopped.")
                    continue
                result = request_type(**kwargs).update("insert")
                response_ids += result.get("ids")
                store_data(engine, result.get("processed_data"))
            elif sub_action == "update":
                if not previously_inserted(engine, action, id):
                    print("ERROR: Attempt to update data not present in DB stopped.")
                    continue
                result = request_type(**kwargs).update("update")
                update_data(engine, result.get("processed_data"))
    else:
        result = request_type(**kwargs).update("insert")
        response_ids = result.get("ids")
        store_data(engine, result.get("processed_data"))
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
    Session = sessionmaker(bind=engine) 
    session = Session()
    # print Premier League Top 25 Scorers by goals/minute
    query_result = session.query( 
            Players.firstname,
            Players.lastname, 
            Players.goals, 
            Players.minutes_played 
        ).filter( 
            Players.minutes_played > 900.0 
        ).order_by( 
            Players.goals/(Players.minutes_played/90.0
        ))[::-1][:25]

    print("NAME\t\t\t\t\tG/90\tGOALS\tMINUTES PLAYED")
    for fname, lname, goals, minutes_played in query_result:
        print(f"{(fname + ' ' + lname).ljust(35,' ')}\t{round(goals/(minutes_played/90.0), 2)}\t{goals}\t{minutes_played}")
    session.close()


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
