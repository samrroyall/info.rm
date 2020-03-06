#!/usr/bin/env python3

from typing import Type, Dict, Set, Any
from orm import Leagues, Teams, Players
from requests import get
from time import sleep
from datetime import datetime
from hashlib import md5


class Registry(type):
    """ Class defining Subclass registry. All metaclasses of registry will be listed in _REGISTRY as
    {class_name:class} key-value pairs.
        Class variables:
            _REGISTRY :: Dictionary mapping child class names to child class objects
    """
    _REGISTRY: Dict[str, Any] = dict()

    @classmethod
    def __new__(cls, *args, **kwargs) -> Type[cls]:
        new_class = super().__new__(cls, *args, **kwargs)
        if new_class._REGISTER:
            cls._REGISTRY[new_class.__name__] = new_class
        return new_class

    @classmethod
    def get_registry(cls) -> Any:
        return cls._REGISTRY


class Request(metaclass=Registry):
    """ Class defining methods used during the collection and processing of 
    data through API requests."""

    # CLASS VARIABLES - change some of these to CLI arguments
    _REGISTER: bool = False
    _API_URL: str = "https://api-football-v1.p.rapidapi.com/v2/"
    _API_HOST: str = "api-football-v1.p.rapidapi.com"
    _API_RATELIMIT_HEADER: str = "X-RateLimit-requests-Limit"
    _API_RATELIMIT_REMAINING_HEADER: str = "X-RateLimit-requests-Remaining"
    _RATELIMIT: Optional[int] = None
    _RATELIMIT_REMAINING: Optional[int] = None
    _RATELIMIT_RESET: Optional[datetime] = None
    
    def __init__(
        self, 
        current_season: str, 
        subscription_time: str,
        token: str
    ) -> None:
        cls = self.__class__
        self.reset_hour: int = int(subscription_time.split(':')[0])
        self.reset_minute: int = int(subscription_time.split(':')[1])
        self.current_season_long: str = current_season
        self.current_season_short: str = current_season.split('-')[0]
        self.headers: Dict[str,str] = { 
            "x-rapidapi-key": token,
            "x-rapidapi-host": cls._API_HOST
        }
        
    def set_reset_time_day(self) -> None:
        """ Method to calculate reset time for daily ratelimit."""
        cls = self.__class__
        today = datetime.today()
        # If past <reset_hour> <reset_minute> on current date set reset time to tomorrow
        if (today.hour > self.reset_hour or today.hour == self.reset_hour and 
                today.minute >= self.reset_minute):
            reset_datetime = today.replace( 
                hour = self.reset_hour, 
                minute = self.reset_minute,
                second = 0,
                microsecond = 0 
            )
        # Set reset time to <reset_hour> <reset_minute> on current date
        else:
            reset_datetime = today.replace(
                day = today.day + 1, 
                hour = self.reset_hour, 
                minute = self.reset_minute,
                second = 0,
                microsecond = 0
            )
        cls._RATELIMIT_RESET = reset_datetime.timestamp()

    def set_ratelimit(self, headers) -> None:
        """ Method to check and respond to API rate limit status before subsequent call.
        """
        cls = self.__class__
        # DAILY RATELIMIT
        # If daily ratelimit has not been set, set it 
        if not cls._RATELIMIT:
            cls._RATELIMIT = headers.get(cls._API_RATELIMIT_HEADER)
        # Always update requests remaining for daily ratelimit
        cls._RATELIMIT_REMAINING = headers.get(cls._API_RATELIMIT_REMAINING_HEADER)
        # Set daily ratelimit reset time on first request
        if not cls._RATELIMIT_RESET:
            self.set_reset_time_day()

    def get_ratelimit(self):
        """ Method to check and respond to API rate limit status before subsequent call.
        """
        cls = self.__class__

        # Check DAILY RATELIMIT
        # update daily ratelimit reset time if passed
        if cls._RATELIMIT_RESET and cls._RATELIMIT_RESET <= datetime.today().timestamp():
            self.set_reset_time_day()
        # If daily ratelimit requests remaining hits 0, sleep until reset time + one second
        if cls._RATELIMIT_REMAINING and cls._RATELIMIT_REMAINING == 0:
            sleep(cls._RATELIMIT_RESET - datetime.today().timestamp() + 1)
    
    def make_call(self):
        """ Method to make API call.
            Arguments:
                parameter :: specific location in endpoint for API call (optional)
        """
        cls = self.__class__ 
        # View ratelimit before proceeding, sleep if needed
        self.get_ratelimit()
        # Make API request
        url = f"{cls._API_URL}{self.endpoint}" 
        api_response = get(url, headers=self.headers)
        # Update ratelimit
        self.set_ratelimit(api_response.headers)
        # Deal with API response status code
        if api_response.status_code == 429:
            print("INFO: Minute Ratelimit Reached. Sleeping Now...")
            sleep(61)
            return self.make_call()
        elif not api_response.json().get("api"):
            print(f"ERROR: HTTP Request '{url}' Did Not Return Data.")
            print(f"\tResponse: {api_response.json().get('api')}")
        elif api_response.status_code != 200:
            print(f"ERROR: HTTP Request '{url}' Failed. Status: {api_response.status_code}.")
            print(f"\tDescription: {api_response.json().get('message')}")
        else:
            return api_response.json()

    def process_response(self, response_data, type):
        """ Method to process the response of an API call, altering fields and adding foreign key if 
        needed. Implement in child classes.
            Arguments:
                response_data :: data returned by API 
        """
        pass

    def update(self, action_type):
        """ Method to gather, process, and store API data. """
        api_response = self.make_call()
        response_data = api_response.get("api").get(self.orm_class.__name__.lower())
        return self.process_response(response_data, action_type) 


class LeaguesRequest(Request):
    """ Class defining methods used during the collection and processing of data through API requests 
    regarding Leagues data.
    """
    _REGISTER  = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = f"leagues/season/{self.current_season_short}"
        self.orm_class = Leagues

    def process_response(self, leagues_data, action_type):
        cls = self.__class__
        filtered_leagues = []
        league_ids = []
        for league in leagues_data:
            if f"{league.get('name')},{league.get('country')}" in cls._CURRENT_LEAGUES:
                league["season_start"] = datetime.strptime(league.get("season_start"),"%Y-%m-%d").date()
                league["season_end"] = datetime.strptime(league.get("season_end"),"%Y-%m-%d").date()
                league["is_current"] = bool(league.get("is_current"))
                league_ids.append({"name":league.get("name"),"id":league.get("league_id")})
                if action_type == "update":
                    filtered_leagues.append(league)
                elif action_type == "insert":
                    filtered_leagues.append(self.orm_class().from_json(league))
        return {"ids":league_ids,"processed_data":filtered_leagues}


class TeamsRequest(Request):
    """ Class defining methods used during the collection and processing of data through API requests 
    regarding Teams data.
    """

    _REGISTER  = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.league_id = kwargs.get("foreign_key").get("id")
        self.league_name = kwargs.get("foreign_key").get("name")
        self.endpoint = f"teams/league/{self.league_id}"
        self.orm_class = Teams

    def process_response(self, teams_data, action_type):
        team_ids = []
        for idx in range(len(teams_data)):
            team = teams_data[idx]
            team["league_id"] = self.league_id 
            team_ids.append({"league_name":self.league_name,"team_name":team.get("name"),"id":team.get("team_id")})
            if action_type == "insert":
                teams_data[idx] = self.orm_class().from_json(team)
        return {"ids":team_ids,"processed_data":teams_data}


class PlayersRequest(Request):
    """ Class defining methods used during the collection and processing of data through API requests 
    regarding Teams data.
    """    

    _REGISTER  = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.team_id = kwargs.get("foreign_key").get("id")
        self.team_name = kwargs.get("foreign_key").get("team_name")
        self.league_name = kwargs.get("foreign_key").get("league_name")
        self.alt_league_name = self.get_alternative_league_name()
        self.endpoint = f"players/team/{self.team_id}/{self.current_season_long}"
        self.orm_class = Players

    def get_alternative_league_name(self):
        if self.league_name == "Bundesliga 1":
            return "Bundesliga"
        elif self.league_name == "Primera Division":
            return "La Liga"
        else:
            return None

    def process_response(self, players_data, action_type):
        filtered_players = {}
        for player in players_data:
            if player.get("league") == self.league_name or (self.alt_league_name and player.get("league") == self.alt_league_name):
                player["uid"] = md5((f"{player.get('player_id')}{player.get('team_id')}{player.get('league')}").encode()).hexdigest()
                # check for duplicates
                if player.get("uid") in filtered_players.keys():
                    # check which instance is most recent
                    if player.get("games").get("minutes_played") and (player.get("games").get("minutes_played") 
                                                                        > filtered_players[player.get("uid")].get("minutes_played")):
                        player = self.process_player(player)
                    else:
                        continue
                else:
                    player = self.process_player(player)
                filtered_players[player.get("uid")] = player
        if action_type == "insert":
            filtered_players = [self.orm_class().from_json(instance) for instance in filtered_players.values()]
        elif action_type == "update":
            filtered_players = filtered_players.values()
        return {"ids":[],"processed_data":filtered_players}


