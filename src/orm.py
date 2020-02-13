#!/usr/bin/env python3

from sqlalchemy import Column
from sqlalchemy.types import Integer, String, Date, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
#from datetime import date

Base = declarative_base()

class Leagues(Base):
    __tablename__ = "leagues"

    league_id = Column(Integer, primary_key = True)
    name = Column(String)
    type = Column(String)
    country = Column(String)
    season = Column(Integer) # 2019
    season_start = Column(Date) # YYYY-MM-DD -> Datetime.Date()
    season_end = Column(Date) # YYYY-MM-DD -> Datetime.Date()
    logo = Column(String)
    flag = Column(String)
    is_current = Column(Boolean) # 1 or 0 -> True or False

def league_from_json(datum):
    ''' Function that converts an API response datum into a Leagues instance.
    '''

    instance = Leagues()
    for key,value in datum.items():
        if key == "season_start" or key == "season_end":
            setattr(instance, key, datetime.strptime(value, "%Y-%m-%d").date()) # python3.6 functionality
            #setattr(instance, key, date.fromisoformat(value)) # python3.8 functionality
        elif key == "is_current":
            setattr(instance, key, bool(value))
        elif hasattr(Leauges, key):
            setattr(instance, key, value)
        else:
            print("*TODO* throw error")
    return instance


class Teams(Base):
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key = True)
    league_id = Column(Integer, ForeignKey("leagues.league_id"), nullable = False) # not included in output
    name = Column(String)
    logo = Column(String)
    founded = Column(Integer)
    venue_name = Column(String)
    venue_city = Column(String)
    country = Column(String)
    venue_capacity = Column(Integer)

def team_from_json(datum, foreign_key):
    ''' Function that converts an API response datum into a Teams instance.
    '''
    instance = Teams()
    for key,value in datum.items():
        if hasattr(Teams, key):
            setattr(instance, key, value)
        else:
            print("*TODO* throw error")
    setattr(instance, "league_id", foreign_key)
    return instance

class Players(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key = True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable = False) # not included in output
    firstname = Column(String)
    lastname = Column(String)
    position = Column(String) # Attacker, ... 
    age = Column(Integer)
    birth_date = Column(Date) # YYYY/MM/DD -> Datetime.Date()
    nationality = Column(String)
    height = Column(Float) # "X cm" -> cm_to_in(float("X")) 
    weight = Column(Float) # "X kg" -> kg_to_lb(float("X"))
    rating = Column(Float) # "X" -> float("X")
    captain = Column(Boolean) # 1 or 0 -> True or False

    # STATS
    # "shots": {"total":x,"on":y}
    shots = Column(Integer)
    shots_on = Column(Integer)
    shots_percent = Column(Integer)# CALCULATE: shots_on/shots
    # "goals": {"total":x,"conceded":y,"assists":z}
    goals = Column(Integer)
    goals_conceded = Column(Integer)
    assists = Column(Integer)
    # "passes": {"total":x,"key":y,"accuracy":z}
    passes = Column(Integer)
    passes_key = Column(Integer)
    passes_percent = Column(Integer)
    # "tackes": {"total":x,"blocks":y,"interceptions":z}
    tackles = Column(Integer)
    blocks = Column(Integer)
    interceptions = Column(Integer)
    # "duels": {"total":x,"won":y}
    duels = Column(Integer)
    duels_won = Column(Integer)
    duels_percent # CALCULATE duels_won/duels
    # "dribbles": {"attempts":x,"success":y}
    dribbles_attempted = Column(Integer)
    dribbles_won = Column(Integer)
    dribbles_percent = # CALCULATE dribbles_won/dribbles_attempted
    # "fouls": {"drawn":x,"committed":y}
    fouls_drawn = Column(Integer)
    fouls_committed = Column(Integer)
    # "cards": {"yellow":x,"yellowred":y,"red":z}
    cards_yellow = Column(Integer)
    cards_second_yellow = Column(Integer)
    cards_red = Column(Integer)
    cards_straight_red = Column(Integer) # CALCULATE cards_red - cards_secondyellow
    # "penalty": {"won":x,"commited":y,"success":z,"missed":za,"saved":zb} [sic]
    penalty_won = Column(Integer)
    penalty_committed = Column(Integer)
    penalty_success = Column(Integer)
    penalty_missed = Column(Integer)
    pentlty_percent = Column(Integer) # CALCULATE penalty_success/(penalty_success+penalty_missed)
    penalty_saved = Column(Integer)
    # "games": {"appearences":x,"minutes_played":y,"lineups":z} [sic]
    games_appearances = Column(Integer)
    minutes_played = Column(Integer)
    games_started = Column(Integer)
    # "substitutes": {"in":x,"out":y,"bench":z}
    substitutes_in = Column(Integer)
    substitutes_out = Column(Integer)
    games_bench = Column(Integer)

def player_from_json(datum, foreign_key):
    ''' Function that converts an API response datum into a Players instance.
    '''
    pass 
