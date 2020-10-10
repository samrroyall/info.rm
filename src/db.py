#!/usr/bin/env python3

import pathlib
from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker, session, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import create_database, database_exists
import sys

from orm import Leagues, Teams, Players, Stats, Base

def initialize_engine():
    db_path = pathlib.Path(__file__).parent.absolute()
    db_url = f"sqlite:///{db_path}/info.rm.db"
    if not database_exists(db_url):
        create_database(db_url)
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def modify_db_row(engine, data, table):
    """ Function for initializing session with DB and inserting new rows"""
    # initialize DB session
    Session = sessionmaker(bind=engine)
    session = Session()
    # assess whether data currently exists in DB
    query_result = session.query(table).filter(table.id == data.get("id"))
    # attempt to insert ORM instances from api_response to session
    if len(list(query_result)) == 0:
        orm_data = table().from_json(data)
        try:
            session.add(orm_data)
            session.commit()
            session.close()
        except:
            print("""ERROR: Data insertion into DB failed.
    MESSAGE: """, sys.exc_info()[0])
            raise
    else:
        try:
            session.query(table).filter(table.id == data.get("id")).update(data)
            session.commit()
            session.close()
        except:
            print("""ERROR: Data update on DB failed.
    MESSAGE: """, sys.exc_info()[0])
            raise
    return session

