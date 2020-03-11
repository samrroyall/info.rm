#!/usr/bin/env python3

from datetime import datetime,date

from sqlalchemy import Column, Integer, String, Date, Boolean, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr

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

    def get_type(self, col_name):
        """ Instance method to check values of class columns."""
        cls = self.__class__
        assert cls._TYPES.get(col_name), "ERROR: Column not present in table."
        return cls._TYPES.get(col_name)


Base = declarative_base(cls=BaseMixin)


class Leagues(Base):
    """ ORM Class defining attributes for leagues table. """

    _TYPES = {
        "id": int,
        "name": str,
        "type": str,
        "country": str,
        "season": int,
        "season_start": date,
        "season_end": date,
        "logo": str,
        "flag": str,
        "is_current": bool,
    }

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    country = Column(String)
    season = Column(Integer) 
    season_start = Column(Date) 
    season_end = Column(Date) 
    logo = Column(String)
    flag = Column(String)
    is_current = Column(Boolean)

    def __repr__(self):
        """ Instance to print class objects """
        return f"<Leagues(league_id={self.id}, name={self.name}, country={self.country}, season={self.season}, ...)>"


class Teams(Base):
    """ ORM Class defining attributes for teams table."""

    _TYPES = {
        "id": int,
        "league_id": int,
        "league_name": str,
        "name": str,
        "logo": str,
        "founded": str,
        "coach_name": str,
        "coach_firstname": str,
        "coach_lastname": str,
        "venue_name": str,
        "venue_city": str,
        "venue_capacity": int,
    }


    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    league_name = Column(String)
    name = Column(String)
    logo = Column(String)
    founded = Column(Integer)
    coach_name = Column(String)
    coach_firstname = Column(String)
    coach_lastname = Column(String)
    venue_name = Column(String)
    venue_city = Column(String)
    venue_capacity = Column(Integer)

    def __repr__(self):
        """ Instance to print class objects """
        return f"<Teams(team_id={self.id}, league_id={self.league_id}, name={self.name}, country={self.country}, ...)>"


class Players(Base):
    """ ORM Class defining attributes for players table. """

    _TYPES = {
        "uid": str,
        "league_id": int,
        "league_name": str,
        "team_id": int,
        "team_name": str,
        "id": int,
        "name": str,
        "firstname": str,
        "lastname": str,
        "position": str,
        "age": int,
        "birth_date": date,
        "nationality": str,
        "height": str,
        "weight": str,
        "rating": float,
        "captain": bool,
        "shots": float,
        "shots_on": float,
        "shots_on_pct": float,
        "goals": float,
        "goals_conceded": float,
        "assists": float,
        "passes": float,
        "passes_key": float,
        "passes_accuracy": float,
        "tackles": float,
        "blocks": float,
        "interceptions": float,
        "duels": float,
        "duels_won": float,
        "duels_won_pct": float,
        "dribbles_past": float,
        "dribbles_attempted": float,
        "dribbles_succeeded": float,
        "dribbles_succeeded_pct": float,
        "fouls_drawn": float,
        "fouls_committed": float,
        "cards_yellow": float,
        "cards_red": float,
        "cards_second_yellow": float,
        "cards_straight_red": float,
        "penalties_won": float,
        "penalties_committed": float,
        "penalties_success": float,
        "penalties_missed": float,
        "penalties_scored_pct": float,
        "penalties_saved": float,
        "minutes_played": float,
        "games_appearances": float,
        "games_started": float,
        "games_bench": float,
        "substitutions_in": float,
        "substitutions_out": float,
    }

    uid = Column(String, primary_key=True) # hash of id, team_id, league_id
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False) 
    league_name = Column(String)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False) 
    team_name = Column(String)
    id = Column(Integer)
    name = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    position = Column(String) # Attacker, Defender, Midfielder, Goalkeeper
    age = Column(Integer)
    birth_date = Column(Date) 
    nationality = Column(String)
    height = Column(String)  
    weight = Column(String) 
    rating = Column(Float) 
    captain = Column(Boolean) 
    # "shots": {"total":x,"on":y}
    shots = Column(Float)
    shots_on = Column(Float)
    shots_on_pct = Column(Float)
    # "goals": {"total":x,"conceded":y,"assists":z}
    goals = Column(Float)
    goals_conceded = Column(Float)
    assists = Column(Float)
    # "passes": {"total":x,"key":y,"accuracy":z}
    passes = Column(Float)
    passes_key = Column(Float)
    passes_accuracy = Column(Float)
    # "tackles": {"total":x,"blocks":y,"interceptions":z}
    tackles = Column(Float)
    blocks = Column(Float)
    interceptions = Column(Float)
    # "duels": {"total":x,"won":y}
    duels = Column(Float)
    duels_won = Column(Float)
    duels_won_pct = Column(Float) # CALCULATE duels_won/duels
    # "dribbles": {"attempts":x,"success":y}
    dribbles_past = Column(Float)
    dribbles_attempted = Column(Float)
    dribbles_succeeded = Column(Float)
    dribbles_succeeded_pct = Column(Float) 
    # "fouls": {"drawn":x,"committed":y}
    fouls_drawn = Column(Float)
    fouls_committed = Column(Float)
    # "cards": {"yellow":x,"yellowred":y,"red":z}
    cards_yellow = Column(Float)
    cards_red = Column(Float)
    cards_second_yellow = Column(Float)
    cards_straight_red = Column(Float) 
    # "penalty": {"won":x,"commited":y,"success":z,"missed":za,"saved":zb} [sic]
    penalties_won = Column(Float)
    penalties_committed = Column(Float)
    penalties_success = Column(Float)
    penalties_missed = Column(Float)
    penalties_scored_pct = Column(Float)
    penalties_saved = Column(Float)
    # "games": {"appearences":x,"minutes_played":y,"lineups":z} [sic]
    games_appearances = Column(Float)
    minutes_played = Column(Float)
    games_started = Column(Float)
    # "substitutes": {"in":x,"out":y,"bench":z}
    substitutions_in = Column(Float)
    substitutions_out = Column(Float)
    games_bench = Column(Float)

    def __repr__(self):
        """ Instance to print class objects """
        return f"""<Players(player_id={self.id}, name={self.name}, team_id={self.team_id}, league={self.league},
                age={self.age}, position={self.position}, nationality={self.nationality}, ...)>"""
