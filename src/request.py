#!/usr/bin/env python3

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
    _REGISTRY = {} # Dict[str:class]

    def __new__(cls, *args, **kwargs):
        new_class = super().__new__(cls, *args, **kwargs)
        if new_class._REGISTER:
            cls._REGISTRY[new_class.__name__] = new_class
        return new_class

    def get_registry(cls):
        return dict(cls._REGISTRY)

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
        cls = self.__class__
        self.current_season_short = kwargs.get("current_season").split('-')[0]
        self.current_season_long = kwargs.get("current_season") 
        self.reset_hour = int(kwargs.get("subscription_time").split(':')[0])
        self.reset_minute = int(kwargs.get("subscription_time").split(':')[1])
        self.headers = {"x-rapidapi-key":kwargs.get("token")}
        self.headers.update(cls._HEADERS)
        
    def set_reset_time_day(self):
        """ Method to calculate reset time for daily ratelimit.
        """
        cls = self.__class__
        today = datetime.today()
        # If past <reset_hour> <reset_minute> on current date set reset time to tomorrow
        if (today.hour > self.reset_hour or today.hour == self.reset_hour and 
                today.minute >= self.reset_minute):
            reset_dt = today.replace( 
                hour = self.reset_hour, 
                minute = self.reset_minute,
                second = 0,
                microsecond = 0 
            )
        # Set reset time to <reset_hour> <reset_minute> on current date
        else:
            reset_dt = today.replace(
                day = today.day + 1, 
                hour = self.reset_hour, 
                minute = self.reset_minute,
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

    def set_ratelimit(self, headers):
        """ Method to check and respond to API rate limit status before subsequent call.
        """
        cls = self.__class__
        # DAILY RATELIMIT
        # If daily ratelimit has not been set, set it 
        if not cls._RATELIMIT_DAY:
            cls._RATELIMIT_DAY = headers.get('X-RateLimit-requests-Limit')
        # Always update requests remaining for daily ratelimit
        cls._RATELIMIT_DAY_REMAINING = headers.get('X-RateLimit-requests-Remaining')
        # Set daily ratelimit reset time on first request
        if not cls._RATELIMIT_DAY_RESET:
            self.set_reset_time_day()
            
        # PER-MINUTE RATELIMIT
        # Always update requests remaining for daily ratelimit
        cls._RATELIMIT_MINUTE_REMAINING -= 1 # decrement remaining requests
        # Set per-minute ratelimit reset time on first request
        if cls._RATELIMIT_MINUTE_REMAINING == cls._RATELIMIT_MINUTE:
            cls.set_reset_time_minute()

    def get_ratelimit(self):
        """ Method to check and respond to API rate limit status before subsequent call.
        """
        cls = self.__class__

        # Check PER-MINUTE RATELIMIT
        # update per-minute ratelimit reset time if passed
        if cls._RATELIMIT_MINUTE_RESET and cls._RATELIMIT_MINUTE_RESET <= datetime.today().timestamp():
            cls.set_reset_time_minute()
        # If per-minute ratelimit requests remaining hits 0, sleep until reset time + one second
        if cls._RATELIMIT_MINUTE_REMAINING and cls._RATELIMIT_MINUTE_REMAINING == 0:
            sleep(cls._RATELIMIT_MINUTE_RESET - dt.today().timestamp() + 1)
            cls._RATELIMIT_MINUTE_REMAINING = cls._RATELIMIT_MINUTE # reset request remaining

        # Check DAILY RATELIMIT
        # update daily ratelimit reset time if passed
        if cls._RATELIMIT_DAY_RESET and cls._RATELIMIT_DAY_RESET <= datetime.today().timestamp():
            self.set_reset_time_day()
        # If daily ratelimit requests remaining hits 0, sleep until reset time + one second
        if cls._RATELIMIT_DAY_REMAINING and cls._RATELIMIT_DAY_REMAINING == 0:
            sleep(cls._RATELIMIT_DAY_RESET - datetime.today().timestamp() + 1)
    
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
        if api_response.status_code != 200:
            print(f"ERROR: HTTP Request '{url}' Failed. Status: {api_response.status_code}.")
            print(f"\tDescription: {api_response.json().get('message')}")
        return api_response.json()

    def process_response(self, response_data):
        """ Method to process the response of an API call, altering fields and adding foreign key if 
        needed. Implement in child classes.
            Arguments:
                response_data :: data returned by API 
        """
        pass

    def update(self):
        """ Method to gather, process, and store API data. """
        api_response = self.make_call()
        response_data = api_response.get("api").get(self.orm_class.__name__.lower())
        return self.process_response(response_data) 


class LeaguesRequest(Request):
    """ Class defining methods used during the collection and processing of data through API requests 
    regarding Leagues data.
    """
    _REGISTER  = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = f"leagues/season/{self.current_season_short}"
        self.orm_class = Leagues

    def process_response(self, leagues_data):
        cls = self.__class__
        filtered_leagues = []
        league_ids = []
        for league in leagues_data:
            if f"{league.get('name')},{league.get('country')}" in cls._CURRENT_LEAGUES:
                league["season_start"] = datetime.strptime(league.get("season_start"),"%Y-%m-%d").date()
                league["season_end"] = datetime.strptime(league.get("season_end"),"%Y-%m-%d").date()
                league["is_current"] = bool(league.get("is_current"))
                league_ids.append({"name":league.get("name"),"id":league.get("league_id")})
                filtered_leagues.append(self.orm_class().from_json(league))
        return {"ids":league_ids,"orm_data":filtered_leagues}


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

    def process_response(self, teams_data):
        team_ids = []
        for idx in range(len(teams_data)):
            team = teams_data[idx]
            team["league_id"] = self.league_id 
            team_ids.append({"league_name":self.league_name,"team_name":team.get("name"),"id":team.get("team_id")})
            teams_data[idx] = self.orm_class().from_json(team)
        return {"ids":team_ids,"orm_data":teams_data}


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
        self.endpoint = f"players/team/{self.team_id}/{self.current_season_long}"
        self.orm_class = Players

    def process_response(self, players_data):
        orm_instances = []
        for idx in range(len(players_data)):
            player = players_data[idx]
            if player.get("league") == self.league_name:
                player["uid"] = md5((f"{player.get('player_id')}{player.get('team_id')}{player.get('league')}").encode()).hexdigest()
                if player.get("weight"):
                    player["weight"] = float(player.get("weight").split(" ")[0]) * 0.393701
                else:
                    player["weight"] = None
                if player.get("height"):
                    player["height"] = float(player.get("height").split(" ")[0]) * 2.20462
                else:
                    player["height"] = None
                if player.get("rating"):
                    player["rating"] = float(player.get("rating"))
                else:
                    player["rating"] = None
                if player.get("captain"):
                    player["captain"] = bool(player.get("captain"))
                else:
                    player["captain"] = None
                if player.get("birth_date"):
                    player["birth_date"] = datetime.strptime(player.get("birth_date"), "%d/%m/%Y").date()
                else:
                    player["birth_date"] = None
                if player.get("position"):
                    player["position"] = player.get("position").lower()
                else:
                    player["position"] = None
                # shots
                player["shots_on"] = player.get("shots").get("on")
                player["shots"] = player.get("shots").get("total")
                if player.get("shots") and player.get("shots") > 0:
                    player["shots_on_pct"] = round(100.0 * player.get("shots_on") / player.get("shots"))
                else:
                    player["shots_on_pct"] = None
                # goals
                player["goals_conceded"] = player.get("goals").get("conceded")
                player["assists"] = player.get("goals").get("assists")
                player["goals"] = player.get("goals").get("total")
                # passes
                player["passes_key"] = player.get("passes").get("key")
                player["passes_accuracy"] = player.get("passes").get("accuracy")
                player["passes"] = player.get("passes").get("total")
                # tackles
                player["blocks"] = player.get("tackles").get("blocks")
                player["interceptions"] = player.get("tackles").get("interceptions")
                player["tackles"] = player.get("tackles").get("total")
                # duels
                player["duels_won"] = player.get("duels").get("won")
                player["duels"] = player.get("duels").get("total")
                if player.get("duels") and player.get("duels") > 0:
                    player["duels_won_pct"] = round(100.0 * player.get("duels_won") / player.get("duels"))
                else:
                    player["duels_won_pct"] = None
                # dribbles
                player["dribbles_attempted"] = player.get("dribbles").get("attempted")
                player["dribbles_succeeded"] = player.get("dribbles").get("success")
                if player.get("dribbles_attempted") and player.get("dribbles_attempted") > 0:
                    player["dribbles_succeeded_pct"] = round(100.0 * player.get("dribbles_succeeded") / 
                                                                player.get("dribbles_attempted"))
                else:
                    player["dribbles_succeeded_pct"] = None
                # fouls
                player["fouls_drawn"] = player.get("fouls").get("drawn")
                player["fouls_committed"] = player.get("fouls").get("committed")
                # cards
                player["cards_yellow"] = player.get("cards").get("yellow")
                player["cards_red"] = player.get("cards").get("red")
                player["cards_second_yellow"] = player.get("cards").get("yellowred")
                player["cards_straight_red"] = player.get("cards_red") - player.get("cards_second_yellow") 
                # pentalties
                player["penalties_won"] = player.get("penalty").get("won")
                player["penalties_committed"] = player.get("penalty").get("commited") # [sic]
                player["penalties_saved"] = player.get("penalty").get("saved")
                player["penalties_scored"] = player.get("penalty").get("success")
                player["penalties_missed"] = player.get("penalty").get("missed")
                if player.get("penalties_scored_pct") and player.get("penalties_scored_pct") > 0:
                    player["penalties_scored_pct"] = round(100.0 * player.get("penalties_scored") / 
                                                                (player.get("penalties_scored") + 
                                                                player.get("penalties_missed")))
                else:
                    player["penalties_scored_pct"] = None
                # games
                player["games_appearances"] = player.get("games").get("appearences") # [sic]
                player["minutes_played"] = player.get("games").get("appearences") # [sic]
                player["games_started"] = player.get("games").get("lineups") # [sic]
                player["games_bench"] = player.get("substitutes").get("bench") # [sic]
                player["substitutions_in"] = player.get("substitutes").get("in")
                player["substitutions_out"] = player.get("substitutes").get("out")
                orm_instances.append(self.orm_class().from_json(player))
        return {"ids":[],"orm_data":orm_instances}


