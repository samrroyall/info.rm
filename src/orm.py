#!/usr/bin/env python3

from sqlalchemy import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, String, Date, Boolean, Float
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from datetime import datetime
#from datetime import date

class BaseMixin:
    """ Mixin Class to set common attributes and methodsfor Base class. """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def from_json(self, json_data):  
        """ Instance method to set class attributes from json input."""
        for key, value in json_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

Base = declarative_base(cls=BaseMixin)

class Leagues(Base):
    """ ORM Class defining attributes corresponding to columns in 'leagues' table. """
    league_id = Column(Integer, primary_key = True)
    name = Column(String)
    type = Column(String)
    country = Column(String)
    season = Column(Integer) 
    season_start = Column(Date) 
    season_end = Column(Date) 
    logo = Column(String)
    flag = Column(String)
    is_current = Column(Boolean)

class Teams(Base):
    """ ORM Class defining attributes corresponding to columns in 'teams' table."""
    team_id = Column(Integer, primary_key = True)
    league_id = Column(Integer, ForeignKey("leagues.league_id"), nullable = False)     
    name = Column(String)
    logo = Column(String)
    founded = Column(Integer)
    venue_name = Column(String)
    venue_city = Column(String)
    country = Column(String)
    venue_capacity = Column(Integer)

class Players(Base):
    """ ORM Class defining attributes corresponding to columns in 'players' table."""
    player_id = Column(Integer, primary_key = True)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable = False) 
    firstname = Column(String)
    lastname = Column(String)
    position = Column(String) # Attacker, Defender, Midfielder, Goalkeeper
    age = Column(Integer)
    birth_date = Column(Date) 
    nationality = Column(String)
    height = Column(Float)  
    weight = Column(Float) 
    rating = Column(Float) 
    captain = Column(Boolean) 
    # STATS
    # "shots": {"total":x,"on":y}
    shots = Column(Integer)
    shots_on = Column(Integer)
    shots_on_pct = Column(Integer)
    # "goals": {"total":x,"conceded":y,"assists":z}
    goals = Column(Integer)
    goals_conceded = Column(Integer)
    assists = Column(Integer)
    # "passes": {"total":x,"key":y,"accuracy":z}
    passes = Column(Integer)
    passes_key = Column(Integer)
    passes_accuracy = Column(Integer)
    # "tackles": {"total":x,"blocks":y,"interceptions":z}
    tackles = Column(Integer)
    blocks = Column(Integer)
    interceptions = Column(Integer)
    # "duels": {"total":x,"won":y}
    duels = Column(Integer)
    duels_won = Column(Integer)
    duels_won_pct = Column(Integer) # CALCULATE duels_won/duels
    # "dribbles": {"attempts":x,"success":y}
    dribbles_attempted = Column(Integer)
    dribbles_succeeded = Column(Integer)
    dribbles_succeeded_pct = Column(Integer) 
    # "fouls": {"drawn":x,"committed":y}
    fouls_drawn = Column(Integer)
    fouls_committed = Column(Integer)
    # "cards": {"yellow":x,"yellowred":y,"red":z}
    cards_yellow = Column(Integer)
    cards_red = Column(Integer)
    cards_second_yellow = Column(Integer)
    cards_straight_red = Column(Integer) 
    # "penalty": {"won":x,"commited":y,"success":z,"missed":za,"saved":zb} [sic]
    penalties_won = Column(Integer)
    penalties_committed = Column(Integer)
    penalties_success = Column(Integer)
    penalties_missed = Column(Integer)
    pentlties_scored_pct = Column(Integer)
    penalties_saved = Column(Integer)
    # "games": {"appearences":x,"minutes_played":y,"lineups":z} [sic]
    games_appearances = Column(Integer)
    minutes_played = Column(Integer)
    games_started = Column(Integer)
    # "substitutes": {"in":x,"out":y,"bench":z}
    substitutions_in = Column(Integer)
    substitutions_out = Column(Integer)
    games_bench = Column(Integer)

