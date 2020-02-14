#!/usr/bin/env python3

from requests import get
from time import sleep
from datetime import datetime
#from datetime import date
from .orm import Leagues, Teams, Players


class Registry(type):
    """ Class defining Subclass registry. All metaclasses of registry will be listed in _REGISTRY as
    {class_name:class} key-value pairs.
        Class variables:
            _REGISTRY :: Dictionary mapping child class names to child class objects
    """
    _REGISTRY = {} # Dict[str:class]
    def __new__(cls, *args, **kwargs):
        new_class = super().__new__(cls, *args, **kwargs)
        if new_class._REGISTER:
            cls._REGISTRY[new_class.__name__] = new_class
        return new_class

class Request(metaclass=Registry):
    """ Class defining methods used during the collection and processing of data through API requests. 
        Class variables:
            _REGISTER
            _RATELIMIT_DAY              :: Total number of requests allowed per day
            _RATELIMIT_DAY_REMAINING    :: Total number of requests remaining for the current day
            _RATELIMIT_DAY_RESET        :: Time for daily ratelimit reset
            _RATELIMIT_MINUTE           :: Total number of requests allowed per minute
            _RATELIMIT_MINUTE_REMAINING :: Total number of requests remaining for the current minute
            _RATELIMIT_MINUTE_RESET     :: Time for per-minute ratelimit reset
    """

    # CLASS VARIABLES - change some of these to CLI arguments
    _REGISTER             = False
    _API_URL              = "https://api-football-v1.p.rapidapi.com/v2/"
    _HEADERS              = {"x-rapidapi-host":"api-football-v1.p.rapidapi.com"}
    _CURRENT_LEAGUES      = {"Premier League,England"}
    endpoint              = None
    #_CURRENT_LEAGUES = {
    #     "Premier League,England",
    #     "Ligue 1,France",
    #     "Serie A,Italy",
    #     "Primera Division,Spain",
    #     "Bundesliga 1,Germany"
    #}

    # RATELIMIT VARIABLES
    _RATELIMIT_DAY              = None
    _RATELIMIT_DAY_REMAINING    = None
    _RATELIMIT_DAY_RESET        = None
    _RATELIMIT_MINUTE           = 30
    _RATELIMIT_MINUTE_REMAINING = 30
    _RATELIMIT_MINUTE_RESET     = None

    def __init__(self, **kwargs):
        self.current_season_short = kwargs.get("current_season").split('-')[0]
        self.current_season_long = kwargs.get("current_season") 
        self.reset_hour = int(kwargs.get("subscription_time").split(':')[0])
        self.reset_minute = int(kwargs.get("subscription_time").split(':')[1])
        self._HEADERS.update({"token":kwargs.get("token")})
        
    @classmethod
    def set_reset_time_day(cls):
        """ Method to calculate reset time for daily ratelimit.
        """
        today = datetime.today()
        # If past <reset_hour> <reset_minute> on current date set reset time to tomorrow
        if today.hour > cls._RESET_HOUR or (today.hour == cls._RESET_HOUR and today.minute >= cls._RESET_MINUTE):            
            reset_dt = today.replace( 
                hour = cls._RESET_HOUR, 
                minute = cls._RESET_MINUTE,
                second = 0,
                microsecond = 0 
            )
        # Set reset time to <reset_hour> <reset_minute> on current date
        else:
            reset_dt = today.replace(
                day = today.day + 1, 
                hour = cls._RESET_HOUR, 
                minute = cls._RESET_MINUTE,
                second = 0,
                microsecond = 0
            )
        cls._RATELIMIT_DAY_RESET = reset_dt.timestamp()

    @classmethod
    def set_reset_time_minute(cls):
        """ Method to calculate reset time for per-minute ratelimit
        """
        cls._RATELIMIT_MINUTE_RESET = datetime.today().timestamp() + 61 
        cls._RATELIMIT_MINUTE_REMAINING = cls._RATELIMIT_MINUTE

    @classmethod
    def get_ratelimit(cls):
        """ Method to check and respond to API rate limit status before subsequent call.
        """
        # Check PER-MINUTE RATELIMIT

        # update per-minute ratelimit reset time if passed
        if cls._RATELIMIT_MINUTE_RESET and cls._RATELIMIT_MINUTE_RESET <= dt.today().timestamp():
            cls.set_reset_time_minute()

        # If the number of requests remaining for per-minute rate limit hits 0, sleep until reset time + one second
        if cls._RATELIMIT_MINUTE_REMAINING and cls._RATELIMIT_MINUTE_REMAINING == 0:
            sleep(cls._RATELIMIT_MINUTE_RESET - dt.today().timestamp() + 1)
            cls._RATELIMIT_MINUTE_REMAINING = cls._RATELIMIT_MINUTE # reset request remaining

        # Check DAILY RATELIMIT

        # update daily ratelimit reset time if passed
        if cls._RATELIMIT_DAY_RESET and cls._RATELIMIT_DAY_RESET <= datetime.today().timestamp():
            cls.set_reset_time_day()

        # If the number of requests remaining for daily rate limit hits 0, sleep until reset time + one second
        if cls._RATELIMIT_DAY_REMAINING and cls._RATELIMIT_DAY_REMAINING == 0:
            sleep(cls._RATELIMIT_DAY_RESET - datetime.today().timestamp() + 1)

        
    @classmethod
    def set_ratelimit(cls, headers):
        """ Method to check and respond to API rate limit status before subsequent call.
        """
        # DAILY RATELIMIT
        # If daily ratelimit has not been set, set it 
        if !cls._RATELIMIT_DAY:
            cls._RATELIMIT_DAY = headers.get('X-RateLimit-requests-Limit')
        # Always update requests remaining for daily ratelimit
        cls._RATELIMIT_DAY_REMAINING = headers.get('X-RateLimit-requests-Remaining')
        # Set daily ratelimit reset time on first request
        if !cls._RATELIMIT_DAY_RESET:
            cls.set_reset_time_day()
            
        # PER-MINUTE RATELIMIT
        # Always update requests remaining for daily ratelimit
        cls._RATELIMIT_MINUTE_REMAINING -= 1 # decrement remaining requests
        # Set per-minute ratelimit reset time on first request
        if cls._RATELIMIT_MINUTE_REMAINING == cls._RATELIMIT_MINUTE:
            cls.set_reset_time_minute()

    def make_call(self, parameter):
        """ Method to make API call.
            Arguments:
                parameter :: specific location in endpoint for API call (optional)
        """
        # View ratelimit before proceeding, sleep if needed
        self.get_ratelimit()
        # Make API request
        api_response = get(f"{self._API_URL}{self.endpoint}", headers=self._HEADERS)
        # Update ratelimit
        self.set_ratelimit(api_response.headers)

        if api_response.status_code != 200:
            print("**TO-DO** create a log of redo requests")

        return api_response.json()

    def process_response(self, response_data, **kwargs):
        """ Method to process the response of an API call, altering fields and adding foreign key if needed.
        Implement in child classes.
            Arguments:
                response_data :: data returned by API 
                foreign_key   :: ID corresponding to higher-level API object (optional)
        """

        pass

    def update(self, parameter = "", **kwargs):
        """ Method to gather, process, and store API data.
            Arguments:
                parameter   :: specific location in endpoint for API call (optional)
                foreign_key :: ID corresponding to higher-level API object (optional)
        """
        api_response = self.make_call(parameter)
        response_data = api_response.get("api").get(self.orm_class.__name__.lower())

        return self.process_response(response_data, kwargs)


class LeaguesRequest(Request):
    """ Class defining methods used during the collection and processing of data through API requests regarding
    Leagues data.
    """
    _REGISTER  = True
    _ORM_CLASS = Leagues

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = f"/leagues/{self.current_season_short}"

    def process_response(self, response_data, **kwargs):
        """ Method to process the response of API call, altering fields and adding foreign key if needed.
        """
        filtered_leagues = []
        for league in leagues_data.get("api").get("leagues"):
            if f"{league.get('name')},{league.get('country')}" in cls._CURRENT_LEAGUES:
                # python3.6 functionality
                league.set("season_start", datetime.strptime(league.get("season_start"), "%Y-%m-%d").date())
                # python3.8 functionality
                #league.set("season_start", date.fromisoformat(league.get("season_start"))) 
                # python3.6 functionality
                league.set("season_end", datetime.strptime(league.get("season_end"), "%Y-%m-%d").date())
                # python3.8 functionality
                #league.set("season_end", date.fromisoformat(league.get("season_end")))
                league.set("is_current", bool(league.get("is_current")))
                filtered_leagues.append(league)

        return filtered_leagues


class TeamsRequest(Request):
    """ Class defining methods used during the collection and processing of data through API requests regarding
    Teams data.
    """

    _REGISTER  = True
    _ORM_CLASS = Teams

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.league_id = kwargs.get("foreign_key")
        self.endpoint = f"teams/league/{self.team_id}"

    def process_response(self, response_data, **kwargs):
        """ Method to process the response of API call, altering fields and adding foreign key if needed.
        """
        league_id = self.league_id 
        # ...
        return teams


class PlayersRequest(Request):
    """ Class defining methods used during the collection and processing of data through API requests regarding
    Teams data.
    """    

    _REGISTER  = True
    _ORM_CLASS = Players

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.team_id = kwargs.get("foreign_key")
        self.endpoint = f"players/team/{self.team_id}/{self.current_season_short}"

    def process_response(self, response_data, **kwargs):
        """ Method to process the response of API call, altering fields and adding foreign key if needed.
        """
        team_id = self.team_id
        # ...
        return players


