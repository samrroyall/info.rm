import requests

class Request:
    ''' Method to check and respond to API rate limit status before subsequent call.
    '''

    # CLASS VARIABLES
    API-DEMO-URL = "https://www.api-football.com/demo/api/v2/" # for testing
    API-PRODUCTION-URL = "https://api-football-v1.p.rapidapi.com/v2/"
    API-URL = API-DEMO-URL # change once testing is done

    # CLASS METHODS
    def __init__(self, endpoint, token):
        ''' Method initializing instance variables.
                endpoint :: API endpoint to be queried for Request instance
                headers  :: API request headers
                token    :: API token to be used for Request instance
        '''
        self.endpoint = endpoint
        self.token    = token
        self.headers  = {
                'x-rapidapi-host':API-URL[8:], # API-URL without HTTP protocol specified
                'x-rapidapi-key':self.token    # **TO-DO** figure out if demo api requires token
            }

    def check_ratelimit(self):
        ''' Method to check and respond to API rate limit status before subsequent call.
        '''
        return "To be implemented..."

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
        check_ratelimit()

        # Make API request
        api-response = requests.get(f"{API-URL}{self.endpoint}", headers=self.headers)
        api-response-headers = api-response.headers
        api-response-status = api-response.status_code
        api-response-json = api-reponse.json()
