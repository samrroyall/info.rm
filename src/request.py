#!/usr/bin/env python3

from typing import Type, Dict, Set, Any, Optional
from requests import get
from time import sleep
from datetime import datetime
from config import get_config_arg

from process import process_leagues, process_teams, process_players


class Registry(type):
    """ Class defining Subclass registry. All metaclasses of registry will be 
    listed in _REGISTRY as (class_name, class) key-value pairs. """
    _REGISTRY: Dict[str, Any] = dict()

    @classmethod
    def __new__(cls, *args, **kwargs) -> Any:
        new_class = super().__new__(*args, **kwargs)
        if new_class._REGISTER:
            cls._REGISTRY[new_class.__name__] = new_class
        return new_class

    @classmethod
    def get_registry(cls) -> Any:
        return cls._REGISTRY


class Request(metaclass=Registry):
    """ Class defining methods used during the collection and processing of 
    data through API requests. """

    # CLASS VARIABLES - change some of these to CLI arguments
    _REGISTER: bool = False
    #_API_URL: str = "https://api-football-v1.p.rapidapi.com/v2/"
    _API_URL: str = "https://api-football-beta.p.rapidapi.com/"
    _API_HOST: str = "api-football-beta.p.rapidapi.com"
    _API_RATELIMIT_HEADER: str = "x-ratelimit-requests-limit"
    _API_RATELIMIT_REMAINING_HEADER: str = "x-ratelimit-requests-remaining"
    _RATELIMIT: Optional[int] = None
    _RATELIMIT_REMAINING: Optional[int] = None
    _RATELIMIT_RESET: Optional[float] = None

    def __init__(self) -> None:
        cls = self.__class__
        subscription_time = get_config_arg("subscription_time")
        current_season = get_config_arg("current_season")
        token = get_config_arg("token")
        self.reset_hour: int = int(subscription_time.split(':')[0])
        self.reset_minute: int = int(subscription_time.split(':')[1])
        self.reset_second: int = int(subscription_time.split(':')[2])
        self.current_season_long: str = current_season
        self.current_season_short: int = current_season.split('-')[0]
        self.headers: Dict[str,str] = { 
            "x-rapidapi-key": token,
            "x-rapidapi-host": cls._API_HOST
        }
        self.endpoint: str
        self.foreign_key: int
        self.params: Dict[str, int]
        
    def set_reset_time_day(self) -> None:
        """ Method to calculate reset time for daily ratelimit. """
        cls = self.__class__
        today = datetime.today()
        # If past reset time on current date, set reset time to tomorrow
        if (today.hour > self.reset_hour or (today.hour == self.reset_hour and 
                today.minute >= self.reset_minute) or (today.hour == self.reset_hour
                and today.minute == self.reset_minute and today.second >= self.reset_second)):
            reset_datetime = today.replace( 
                hour = self.reset_hour, 
                minute = self.reset_minute,
                second = self.reset_second,
                microsecond = 0 
            )
        # Set reset time to <reset_hour> <reset_minute> on current date
        else:
            reset_datetime = today.replace(
                day = today.day + 1, 
                hour = self.reset_hour, 
                minute = self.reset_minute,
                second = self.reset_second,
                microsecond = 0
            )
        cls._RATELIMIT_RESET = reset_datetime.timestamp()

    def set_ratelimit(self, headers: Dict[str, str]) -> None:
        """ Method to update API rate limit status. """
        cls = self.__class__
        # If daily ratelimit has not been set, set it 
        if not cls._RATELIMIT:
            cls._RATELIMIT = int(headers.get(cls._API_RATELIMIT_HEADER))
        # Always update requests remaining for daily ratelimit
        cls._RATELIMIT_REMAINING = int(headers.get(cls._API_RATELIMIT_REMAINING_HEADER))
        # Set daily ratelimit reset time on first request
        if not cls._RATELIMIT_RESET:
            self.set_reset_time_day()

    def get_ratelimit(self) -> None:
        """ Method to check and respond to API rate limit status. """
        cls = self.__class__
        # update daily ratelimit reset time if passed
        if (cls._RATELIMIT_RESET and cls._RATELIMIT_RESET <= 
                datetime.today().timestamp()):
            self.set_reset_time_day()
        # If requests remaining hits 0, sleep until reset time + one second
        if cls._RATELIMIT_REMAINING and cls._RATELIMIT_REMAINING == 0:
            sleep(cls._RATELIMIT_RESET - datetime.today().timestamp() + 1)
    
    def make_call(self) -> Dict[str, Dict[str, Any]]:
        """ Method to make API call. """
        cls = self.__class__ 
        # View ratelimit before proceeding, sleep if needed
        self.get_ratelimit()
        # Make API request
        url = f"{cls._API_URL}{self.endpoint}" 
        api_response = get(url, headers=self.headers, params=self.params)
        # Update ratelimit
        headers_lower = dict([(k.lower(),v) for k,v in dict(api_response.headers).items()])
        self.set_ratelimit(headers_lower)
        # Deal with API response status code
        request_code = api_response.status_code
        if request_code == 429:
            print("INFO: Minute Ratelimit Reached. Sleeping Now...")
            sleep(61)
            return self.make_call()
        # Format API request content as JSON
        request_content = api_response.json()
        # Ensure that HTTP request is successful
        assert request_code == 200, \
            f"""ERROR: HTTP Request '{url}' Failed. Status: {request_code}.
            \tDescription: {request_content.get('message')}"""
        return request_content 

    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        response_type = self.__class__.__name__.lower().split("request")[0]
        process_func = eval(f"process_{response_type}")
        return process_func(response_data.get("response"), self.foreign_key)

    def update(self) -> Dict[str, Any]:
        """ Method to gather, process, and store API data. """
        api_response = self.make_call()
        return self.process_response(api_response) 


class LeaguesRequest(Request):
    """ Class defining methods used during the collection and processing of 
    data through API requests regarding Leagues data. """
    _REGISTER: bool = True

    def __init__(self) -> None:
        super().__init__()
        self.endpoint: str = "leagues"
        self.foreign_key: Optional[int] = None
        self.params: Dict[str, int] = {"season": self.current_season_short}


class TeamsRequest(Request):
    """ Class defining methods used during the collection and processing of 
    data through API requests regarding Teams data. """
    _REGISTER: bool = True

    def __init__(self, league_id: int) -> None:
        super().__init__()        
        self.endpoint: str = "teams"
        self.foreign_key: int = league_id
        self.params: Dict[str, int] = {
            "league": league_id,
            "season": self.current_season_short
        }


class PlayersRequest(Request):
    """ Class defining methods used during the collection and processing of
    data through API requests regarding Teams data. """    
    _REGISTER: bool = True

    def __init__(self, team_id: int) -> None:
        super().__init__()        
        self.endpoint: str = "players"
        self.foreign_key: int = team_id
        self.params: Dict[str, int] = {
            "team": team_id,
            "season": self.current_season_short
        }

