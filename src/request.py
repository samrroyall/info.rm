from requests import get
from time import sleep
from datetime import datetime

from .orm import Leagues, league_from_json, Teams, team_from_json, Players, player_from_json

class Request:
    ''' Class defining methods used during the collection of data through API requests. 
        Class variables:
            _RATELIMIT_DAY              :: Total number of requests allowed per day
            _RATELIMIT_DAY_REMAINING    :: Total number of requests remaining for the current day
            _RATELIMIT_DAY_RESET        :: Time for daily ratelimit reset
            _RATELIMIT_MINUTE           :: Total number of requests allowed per minute
            _RATELIMIT_MINUTE_REMAINING :: Total number of requests remaining for the current minute
            _RATELIMIT_MINUTE_RESET     :: Time for per-minute ratelimit reset
    '''

    # CLASS VARIABLES - change some of these to CLI arguments
    _CURRENT_SEASON = 2019
    _RESET_HOUR = 17
    _RESET_MINUTE = 50
    _API_URL = "https://api-football-v1.p.rapidapi.com/v2/"
    _HEADERS = {
        'x-rapidapi-host':"api-football-v1.p.rapidapi.com",
        'x-rapidapi-key':"e5d1ceda67mshdfe4d820b3e6835p1187fbjsn9c760f31342c"
    }
    _CURRENT_LEAGUES = {"Premier League,England"}
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

    def __init__(self, endpoint, type):
        self.path = endpoint
        self.path = type

    @classmethod
    def set_reset_time_day(cls):
        ''' Method to calculate reset time for daily ratelimit
        '''
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
        ''' Method to calculate reset time for per-minute ratelimit
        '''
        cls._RATELIMIT_MINUTE_RESET = datetime.today().timestamp() + 61 
        cls._RATELIMIT_MINUTE_REMAINING = cls._RATELIMIT_MINUTE

    @classmethod
    def get_ratelimit(cls):
        ''' Method to check and respond to API rate limit status before subsequent call.
        '''
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
        ''' Method to check and respond to API rate limit status before subsequent call.
        '''
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
        ''' Method to make API call.
        '''
        # View ratelimit before proceeding, sleep if needed
        self.get_ratelimit()

        # Make API request
        api_response = get(f"{self._API_URL}{self.endpoint}{parameter}", headers=self._HEADERS)

        # Update ratelimit
        self.set_ratelimit(api_response.headers)

        if api_response.status_code != 200:
            print("**TO-DO** create a log of redo requests")

        return api_response.json()

    @classmethod
    def filter_leagues(cls, leagues_data):
        ''' Method to filter the response of league API call to only include current leagues.
        '''
        filtered_data = []

        for league in leagues_data.get("api").get("leagues"):
            if f"{league.get('name')},{league.get('country')}" in cls._CURRENT_LEAGUES:
                filtered_data.append(league)

        return filtered_data

    def orm_from_json(self, datum, id)
        ''' Method to convert datum of API response data to its corresponding ORM object.
        '''

        if self.type == "Leauges":
            return league_from_json(datum)
        elif self.type == "Teams":
            return team_from_json(datum, id)
        elif self.type == "Players":
            return player_from_json(datum, id)

    def process_response(self, response_data, id):
        ''' Method to process the response of API call, turning JSON response into list of ORM class instances.
        '''
        orm_class = eval(self.type)

        if self.type == "Leagues":
            response_data = self.filter_leagues(response_data)
        else:
            response_data = response_data.get("api").get(self.type.lower())

        # return list of ORM instances derived from API output
        return [self.orm_from_json(datum, id) for datum in response_data]

    def update(self, parameter = "", id = None):
        ''' Method to gather, process, and store API data.
        '''

        return self.process_response(self.make_call(parameter), id)

