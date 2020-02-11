import requests
import time
from datetime import datetime as dt

class Request:
    ''' Method to check and respond to API rate limit status before subsequent call.
        Class variables initialized:
            ratelimit_day              :: Total number of requests allowed per day
            ratelimit_day_remaining    :: Total number of requests remaining for the current day
            ratelimit_day_start        :: Time for daily ratelimit start
            ratelimit_day_reset        :: Time for daily ratelimit reset
            ratelimit_minute           :: Total number of requests allowed per minute
            ratelimit_minute_remaining :: Total number of requests remaining for the current minute
            ratelimit_minute_start     :: Time for per-minute ratelimit start
            ratelimit_minute_reset     :: Time for per-minute ratelimit reset
    '''

    # CLASS VARIABLES
    API_URL = "https://api-football-v1.p.rapidapi.com/v2/"
    CURRENT_SEASON = "2019-2020" # necessary, should become a CLI parameter
    reset_hour = 17 # necessary, should become a CLI parameter
    reset_minute = 50 # necessary, should become a CLI parameter
    self.ratelimit_day              = None
    self.ratelimit_day_remaining    = None
    self.ratelimit_day_reset        = None
    self.ratelimit_day_start        = None
    self.ratelimit_minute           = 30
    self.ratelimit_minute_remaining = 30
    self.ratelimit_minute_reset     = None
    self.ratelimit_minute_start     = None


    # CLASS METHODS
    def __init__(self, endpoint, token):
        ''' Method initializing instance variables.
                endpoint            :: API endpoint to be queried for Request instance
                headers             :: API request headers
                token               :: API token to be used for Request instance
        '''
        self.endpoint = endpoint
        self.token    = token
        # specify rate limit variables
        self.headers  = {
            'x-rapidapi-host':API_URL[8:API_URL.index(".com")], # API-URL without HTTP protocol specified
            'x-rapidapi-key':self.token    # **TO-DO** figure out if demo api requires token
        }
        
    def get_ratelimit(self):
        ''' Method to check and respond to API rate limit status before subsequent call.
        '''
        # deal with daily rate limit
        if self.ratelimit_day_remaining and self.ratelimit_day_remaining == 0:
            current_time = time.time() # current time (epoch)
            time.sleep(self.ratelimit_day_reset-current_time + 1) # sleep until reset time plus one second

        # deal with per-minute rate limit
        if self.ratelimit_minute_remaining and self.ratelimit_minute_remaining == 0:
            current_time = time.time() # current time (epoch)
            time.sleep(self.ratelimit_minute_reset - current_time + 1) # sleep until reset time plus one second

    def set_reset_time_day(self):
        ''' Method to calculate reset time for daily ratelimit
        '''
        today = dt.today()
        # check if past today's reset time
        reset_dt = dt(today.year, today.month, today.day, reset_hour, reset_minute)
        reset_dt_epoch = reset_dt.timestamp()
        if reset_dt_epoch < time.time():            
            self.ratelimit_day_reset = dt(today.year, today.month, today.day + 1, reset_hour, reset_minute).timestamp()
        else:
            self.ratelimit_day_reset = reset_dt_epoch

    def set_ratelimit(self, headers):
        ''' Method to check and respond to API rate limit status before subsequent call.
        '''
        # deal with daily rate limit
        if !self.ratelimit_day:
            self.ratelimit_day = headers.get('X-RateLimit-requests-Limit') # on first request set ratelimit
        self.ratelimit_day_remaining = headers.get('X-RateLimit-requests-Remaining') # update ratelimit remaining

        # on first request set daily ratelimit reset time
        if !self.ratelimit_day_reset:
            self.set_reset_time_day()
            
        # deal with per-minute rate limit
        if self.ratelimit_minute_remaining == self.ratelimit_minute:
            self.ratelimit_minute_start         = time.time()
            self.ratelimit_minute_reset         = self.ratelimit_day_start + 61 # minute plus one second after the first request was made
        else:
            self.ratelimit_minute_remaining -= 1 # decrement remaining requests

    def store_result(self):
        ''' Method to update SQLite DB with API response data.
        '''
        return "To be implemented at instance-level"

    def process_result(self):
        ''' Method to process API response data.
        '''
        return "To be implemented at instance-level"

    def make_call(self):
        ''' Method to make API call.
        '''
        # Query rate limit before proceeding, sleep if needed
        get_ratelimit()

        # Make API request
        api_response = requests.get(f"{API_URL}{self.endpoint}", headers=self.headers)
        api_response_headers = api_response.headers
        api_response_json = api_reponse.json()

        # Query rate limit before proceeding, give user option to sleep or incur charges
        set_ratelimit(api_response_headers)

        if api_response.status_code != 200:
            return "To be implemented..." # **TO-DO** create a log of redo requests

