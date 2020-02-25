#!/usr/bin/env python3

from orm import Leagues, Teams, Players
from sqlalchemy.orm import sessionmaker, session, Query

import sys
from sqlalchemy.exc import IntegrityError

def query_database(engine):
    """ Function for querying data from DB """
    # initialize database connection
    Session = sessionmaker(bind=engine) 
    session = Session()
    query_result = session.query(Players.firstname, Players.lastname, Players.goals).order_by(Players.goals)[::-1][:25]
    session.close()
    return query_result

def update_data(engine, data):
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


