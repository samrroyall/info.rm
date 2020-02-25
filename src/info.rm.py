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
    # initialize DB session
    Session = sessionmaker(bind=engine) 
    session = Session()
    # update database tables with api response data
    for player in data:
        try:
            session.query(Players).filter(Players.uid == player.get("uid")).update(player)
            session.commit()
        except:
            print("ERROR: A problem occurred while updating Players table.")
    session.close()

def store_data(engine, data):
    """ Function for initializing session with DB and inserting new rows"""
    for instance in data:
        # initialize DB session
        Session = sessionmaker(bind=engine) 
        session = Session()
        # add ORM instances from api_response to session
        session.add(instance)
        # insert api response data into database tables
        try:
            session.commit()
            session.close()
        except IntegrityError as ie:
            print("INFO: An attmempt to insert an existing row into the database was made.")
            #print(ie)

def previously_inserted(engine, action, id):
    """ Function for ensuring duplicate DB insertions are not made"""
    # initialize DB session
    Session = sessionmaker(bind=engine) 
    session = Session()
    query_result = False
    # handle updates to/inserts into tables for team and player data differently
    sub_action = action.split("_")[1]
    if sub_action == "teams":
        # check if tables in DB
        if engine.has_table("Teams"):
            query_result = session.query(Teams.league_id).\
                    filter( Teams.league_id == id.get("id") )
    elif sub_action == "players":
        # check if tables in DB
        if engine.has_table("Leagues") and engine.has_table("Teams"):
            # grab league_id matching player league_name
            league_id_query = session.query(Leagues.league_id).\
                    filter(Leagues.name == id.get("league_name"))
            if len(list(league_id_query)) > 0:
                league_id = league_id_query[0][0] # query responses like [(data, ), (data, )]
                # check if team_id and league_id exist in DB matching player team_id and league_id
                query_result = session.query(Teams.team_id, Teams.league_id).\
                        filter(
                            and_( 
                                Teams.team_id == id.get("id"), 
                                Teams.league_id == league_id
                            )
                    )
    if query_result and len(list(query_result)) > 0:
        return True # matching DB rows were found
    else:
        return False # matching DB rows were not found

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
    # handle team and player insert/update operations differently
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
    Session = sessionmaker(bind=engine) 
    session = Session()
    league_query = session.query(Leagues)
    for row in league_query:
        print(row)
    print()

    team_query = session.query(Teams)
    for row in team_query:
        print(row)
    print()

    # print Premier League Top 25 Scorers by goals/minute
    query_result = session.query( 
            Players.firstname,
            Players.lastname, 
            Players.team_id,
            Players.penalties_saved
        ).\
        order_by( 
            Players.penalties_saved,
            Players.lastname
        )[::-1][:10]

    for f, l, t, s in query_result:
        tn = session.query(
                Teams.name
            ).filter(
                Teams.team_id == t
            )[0][0]
        print(f"{f+' '+l}\t{tn}({t})\t{s}")

    print()

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
