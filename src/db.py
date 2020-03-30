#!/usr/bin/env python3

from orm import Leagues, Teams, Players, Base
from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker, session, Query
from sqlalchemy_utils import create_database, database_exists

import sys
import pathlib
from sqlalchemy.exc import IntegrityError

def initialize_engine(season):
    db_path = pathlib.Path(__file__).parent.parent.absolute()
    db_url = f"sqlite:///{db_path}/db/info-rm-{season}.db"
    if not database_exists(db_url):
        create_database(db_url)
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def update_table(engine, player):
    """ Function for initializing session with DB and updating existing Players rows"""
    # initialize DB session
    Session = sessionmaker(bind=engine)
    session = Session()
    # update database tables with api response data
    try:
        session.query(Players).\
                filter(Players.id == player.get("id")).\
                update(player)
    except:
        print("ERROR: Update Unsuccessful.")
        sys.exit(1)
    return session

def insert_into_table(engine, data):
    """ Function for initializing session with DB and inserting new rows"""
    # initialize DB session
    Session = sessionmaker(bind=engine)
    session = Session()
    # add ORM instances from api_response to session
    session.add(data)
    # insert api response data into database tables
    try:
        session.commit()
        session.close()
    except IntegrityError as ie:
        print("ERROR: An attmempt to insert an existing row into the database was made.")
        print("MESSAGE: ", ie)
        sys.exit(1)
    return session

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
                    filter( Teams.league_id == id )
    elif sub_action == "players":
        # check if tables in DB
        if engine.has_table("Players") and engine.has_table("Teams"):
            query_result = session.query(Players.id).\
                    filter( Players.team_id == id )
    if query_result and len(list(query_result)) > 0:
        return True # matching DB rows were found
    else:
        return False # matching DB rows were not found
