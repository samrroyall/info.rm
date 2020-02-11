from requests import get
from time import sleep
from datetime import datetime as dt

class Request:
    ''' Class defining methods used during the collection of data through API requests. 
        Child classes:
            LeagueRequest :: Request all league data for current season (leagues/season/<2019>)
            TeamRequest   :: Request all team data for current league (teams/league/<league_id>)
            PlayerRequest :: Request all player data for current team/season (players/team/<team_id>/<2019-2020>)
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

    # RATELIMIT VARIABLES
    _RATELIMIT_DAY              = None
    _RATELIMIT_DAY_REMAINING    = None
    _RATELIMIT_DAY_RESET        = None
    _RATELIMIT_MINUTE           = 30
    _RATELIMIT_MINUTE_REMAINING = 30
    _RATELIMIT_MINUTE_RESET     = None


    def __init__(self, endpoint):
        ''' Method initializing instance variables.
                endpoint            :: API endpoint to be queried for Request instance
        '''
        self.endpoint = endpoint

    @classmethod
    def set_reset_time_day(cls):
        ''' Method to calculate reset time for daily ratelimit
        '''
        # Set reset time to <reset_hour> <reset_minute> on current date
        today = dt.today()
        reset_dt = dt(today.year, today.month, today.day, cls._RESET_HOUR, cls._RESET_MINUTE)
        reset_dt_epoch = reset_dt.timestamp()
        # If past <reset_hour> <reset_minute> on current date set reset time to the same time tomorrow
        if reset_dt_epoch <= dt.today().timestamp():            
            reset_dt_epoch = reset_dt.replace(day=reset_dt.day + 1).timestamp()
        cls._RATELIMIT_DAY_RESET = reset_dt_epoch

    @classmethod
    def set_reset_time_minute(cls):
        ''' Method to calculate reset time for per-minute ratelimit
        '''
        cls._RATELIMIT_MINUTE_RESET = dt.today().timestamp() + 61 
        cls._RATELIMIT_MINUTE_REMAINING = cls._RATELIMIT_MINUTE

    @classmethod
    def get_ratelimit(cls):
        ''' Method to check and respond to API rate limit status before subsequent call.
        '''
        # update daily ratelimit reset time if passed
        if cls._RATELIMIT_DAY_RESET and cls._RATELIMIT_DAY_RESET <= dt.today().timestamp():
            cls.set_reset_time_day()

        # If the number of requests remaining for daily rate limit hits 0, sleep until reset time + one second
        if cls._RATELIMIT_DAY_REMAINING and cls._RATELIMIT_DAY_REMAINING == 0:
            sleep(cls._RATELIMIT_DAY_RESET - dt.today().timestamp() + 1)

        # update per-minute ratelimit reset time if passed
        if cls._RATELIMIT_MINUTE_RESET and cls._RATELIMIT_MINUTE_RESET <= dt.today().timestamp():
            cls.set_reset_time_minute()

        # If the number of requests remaining for per-minute rate limit hits 0, sleep until reset time + one second
        if cls._RATELIMIT_MINUTE_REMAINING and cls._RATELIMIT_MINUTE_REMAINING == 0:
            sleep(cls._RATELIMIT_MINUTE_RESET - dt.today().timestamp() + 1)
            cls._RATELIMIT_MINUTE_REMAINING = cls._RATELIMIT_MINUTE # reset request remaining

    @classmethod
    def set_ratelimit(cls, headers):
        ''' Method to check and respond to API rate limit status before subsequent call.
        '''
        # DAILY RATELIMIT
        # If daily ratelimit has not been set, set it 
        if !cls._RATELIMIT_DAY:
            cls._RATELIMIT_DAY = headers.get('X-RateLimit-requests-Limit') # on first request set ratelimit
        # Always update requests remaining for daily ratelimit
        cls._RATELIMIT_DAY_REMAINING = headers.get('X-RateLimit-requests-Remaining') # update ratelimit remaining
        # Set daily ratelimit reset time on first request
        if !cls._RATELIMIT_DAY_RESET:
            cls.set_reset_time_day()
            
        # PER-MINUTE RATELIMIT
        # Always update requests remaining for daily ratelimit
        cls._RATELIMIT_MINUTE_REMAINING -= 1 # decrement remaining requests
        # Set per-minute ratelimit reset time on first request
        if cls._RATELIMIT_MINUTE_REMAINING == cls._RATELIMIT_MINUTE:
            cls.set_reset_time_minute()

    def make_call(self, path):
        ''' Method to make API call.
        '''
        # View ratelimit before proceeding, sleep if needed
        self.get_ratelimit()

        # Make API request
        api_response = get(f"{self._API_URL}{self.endpoint}{path}", headers=self._HEADERS)

        # Update ratelimit
        self.set_ratelimit(api_response.headers)

        if api_response.status_code != 200:
            print("**TO-DO** create a log of redo requests")

        return api_response.json()

    def process_response(self):
        ''' Method to process the response of API call. Implement in child classes.
        '''
        pass

    def store_response(self):
        ''' Method to store processed response of API call. Implement in child classes.
        '''
        pass
    
