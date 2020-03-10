#!/usr/bin/env python3

from orm import Leagues, Teams, Players, Base
from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker, session, Query
from sqlalchemy_utils import create_database, database_exists

import sys
import pathlib
from sqlalchemy.exc import IntegrityError

def initialize_engine():
    db_path = pathlib.Path(__file__).parent.parent.absolute()
    db_url = f"sqlite:///{db_path}/db/info.rm.db"
    if not database_exists(db_url):
        create_database(db_url)
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

#def query_database(engine):
#    """ Function for querying data from DB """
#    # initialize database connection
#    Session = sessionmaker(bind=engine) 
#    session = Session()
#    query_result = session.query(Players.firstname, Players.lastname, Players.position, Players.passes_accuracy).\
#        filter(and_(Players.minutes_played >= 900.0, Players.passes >= 500.0, Players.position == "midfielder")).\
#        order_by(Players.passes_accuracy)[::-1][:50]
#    #query_result = session.query(Players.firstname, Players.lastname, Players.team_id, Players.rating).\
#    #    filter(Players.minutes_played >= 350.0).\
#    #    order_by(Players.rating)[::-1][:25]
#
#    session.close()
#    return query_result

def update_table(engine, data):
    """ Function for initializing session with DB and updating existing Players rows"""
    for player in data:
        # initialize DB session
        Session = sessionmaker(bind=engine) 
        session = Session()
        # update database tables with api response data
        try:
            session.query(Players).filter(Players.uid == player.get("uid")).update(player)
            session.commit()
            print("INFO: Update Successful.")
        except:
            print("ERROR: Update Unsuccessful. A problem occurred while updating Players table.")
    session.close()

def insert_into_table(engine, data):
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
            print("INFO: Insertion Successful.")
        except IntegrityError as ie:
            print("ERROR: Insertion Unsuccessful. An attmempt to insert an existing row into the database was made.")
            sys.exit(1)
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
        if engine.has_table("Players") and engine.has_table("Teams"):
            query_result = session.query(Players.uid).\
                    filter( Players.team_id == id.get("id") )
    if query_result and len(list(query_result)) > 0:
        return True # matching DB rows were found
    else:
        return False # matching DB rows were not found


