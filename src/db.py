#!/usr/bin/env python3

from orm import Leagues, Teams, Players, Stats, Base

import pathlib
from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker, session, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import create_database, database_exists
import sys

def initialize_engine():
    db_path = pathlib.Path(__file__).parent.parent.absolute()
    db_url = f"sqlite:///{db_path}/db/info.rm.db"
    if not database_exists(db_url):
        create_database(db_url)
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def update_table(engine, data, table):
    """ Function for initializing session with DB and updating existing Players rows"""
    # initialize DB session
    Session = sessionmaker(bind=engine)
    session = Session()
    # update database tables with api response data
    query_result = session.query(table).filter(table.id == data.get("id"))
    if len(list(query_result)) == 0:
        try:
            session.query(table).\
                    filter(table.id == data.get("id")).\
                    update(data)
        except:
            print("ERROR: Update Unsuccessful.")
            sys.exit(1)
    return session

def insert_into_table(engine, data, table):
    """ Function for initializing session with DB and inserting new rows"""
    # initialize DB session
    Session = sessionmaker(bind=engine)
    session = Session()
    # add ORM instances from api_response to session
    query_result = session.query(table).filter(table.id == data.get("id"))
    orm_class = table()
    data = orm_class.from_json(data)
    if len(list(query_result)) == 0:
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
    pass
    # # initialize DB session
    # Session = sessionmaker(bind=engine)
    # session = Session()
    # query_result = False
    # # handle updates to/inserts into tables for team and player data differently
    # sub_action = action.split("_")[1]
    # if sub_action == "teams":
    #     # check if tables in DB
    #     if engine.has_table("Teams"):
    #         query_result = session.query(Teams.league_id).\
    #                 filter( Teams.league_id == id )
    # elif sub_action == "players":
    #     # check if tables in DB
    #     if engine.has_table("Stats") and engine.has_table("Teams"):
    #         query_result = session.query(Stats.id).\
    #                 filter( Stats.team_id == id )
    # if query_result and len(list(query_result)) > 0:
    #     return True # matching DB rows were found
    # else:
    #     return False # matching DB rows were not found
