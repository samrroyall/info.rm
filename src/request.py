#!/usr/bin/env python3

from datetime import datetime, date
from hashlib import md5
from requests import get
from time import sleep
from typing import Type, Dict, Set, Any, Optional, List, Tuple

from config import get_config_arg
from manifest import get_manifest_arg
from orm import Leagues, Teams, Players, Stats
from query_utils import get_world_leagues

####################################################
########### GLOBAL PROCESSING VARIABLES ############
####################################################

WORLD_LEAGUES = None

flags_dict = {
    "Afghanistan": "AF",
    "Albania": "AL",
    "Algeria": "DZ",
    "American Samoa": "AS",
    "Andorra": "AD",
    "Angola": "AO",
    "Anguilla": "AI",
    "Antigua and Barbuda": "AG",
    "Argentina": "AR",
    "Armenia": "AM",
    "Aruba": "AW",
    "Australia": "AU",
    "Austria": "AT",
    "Azerbaijan": "AZ",
    "Bahamas": "BS",
    "Bahrain": "BH",
    "Bangladesh": "BD",
    "Barbados": "BB",
    "Belarus": "BY",
    "Belgium": "BE",
    "Belize": "BZ",
    "Benin": "BJ",
    "Bermuda": "BM",
    "Bhutan": "BT",
    "Bolivia": "BO",
    "Bonaire": "BQ",
    "Bosnia and Herzegovina": "BA",
    "Botswana": "BW",
    "Bouvet Island": "BV",
    "Brazil": "BR",
    "Brunei": "BN",
    "Bulgaria": "BG",
    "Burkina Faso": "BF",
    "Burundi": "BI",
    "Cambodia": "KH",
    "Cameroon": "CM",
    "Canada": "CA",
    "Cape Verde Islands": "CV",
    "Cayman Islands": "KY",
    "Central African Republic": "CF",
    "Chad": "TD",
    "Chile": "CL",
    "China PR": "CN",
    "Colombia": "CO",
    "Comoros": "KM",
    "Congo": "CG",
    "Congo DR": "CD",
    "Cook Islands": "CK",
    "Costa Rica": "CR",
    "Croatia": "HR",
    "Cuba": "CU",
    "Curaçao": "CW",
    "Cyprus": "CY",
    "Czech Republic": "CZ",
    "Côte d'Ivoire": "CI",
    "Denmark": "DK",
    "Djibouti": "DJ",
    "Dominica": "DM",
    "Dominican Republic": "DO",
    "Ecuador": "EC",
    "Egypt": "EG",
    "El Salvador": "SV",
    "Equatorial Guinea": "GQ",
    "England": "GB",
    "Eritrea": "ER",
    "Estonia": "EE",
    "Ethiopia": "ET",
    "Falkland Islands": "FK",
    "Faroe Islands": "FK",
    "Fiji": "FJ",
    "Finland": "FI",
    "France": "FR",
    "French Guiana": "GF",
    "French Polynesia": "PF",
    "FYR Macedonia": "MK",
    "Gabon": "GA",
    "Gambia": "GM",
    "Georgia": "GE",
    "Germany": "DE",
    "Ghana": "GH",
    "Gibraltar": "GI",
    "Greece": "GR",
    "Greenland": "GL",
    "Grenada": "GD",
    "Guadeloupe": "GP",
    "Guam": "GU",
    "Guinea": "GN",
    "Guinea-Bissau": "GW",
    "Guyana": "GY",
    "Haiti": "HT",
    "Honduras": "HN",
    "Hong Kong": "HK",
    "Hungary": "HU",
    "Iceland": "IS",
    "India": "IN",
    "Indonesia": "ID",
    "Iran": "IR",
    "Iraq": "IQ",
    "Ireland": "IE",
    "Ireland Republic": "IE",
    "Isle of Man": "IM",
    "Israel": "IL",
    "Italy": "IT",
    "Jamaica": "JM",
    "Japan": "JP",
    "Jordan": "JO",
    "Kazakhstan": "KZ",
    "Kenya": "KE",
    "Kiribati": "KI",
    "Korea Republic": "KR",
    "Korea DPR": "KP",
    "Kuwait": "KW",
    "Kyrgyzstan": "KG",
    "Laos": "LA",
    "Latvia": "LV",
    "Lebanon": "LB",
    "Lesotho": "LS",
    "Liberia": "LR",
    "Libya": "LY",
    "Liechtenstein": "LI",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Macao": "MO",
    "Macedonia": "MK",
    "Madagascar": "MG",
    "Malawi": "MW",
    "Malaysia": "MW",
    "Maldives": "MV",
    "Mali": "ML",
    "Malta": "MT",
    "Marshall Islands": "MH",
    "Martinique": "MQ",
    "Mauritania": "MR",
    "Mauritius": "MU",
    "Mayotte": "YT",
    "Mexico": "MX",
    "Micronesia": "FM",
    "Moldova": "MD",
    "Monaco": "MC",
    "Mongolia": "MN",
    "Montenegro": "ME",
    "Montserrat": "MS",
    "Morocco": "MA",
    "Mozambique": "MZ",
    "Myanmar": "MM",
    "Namibia": "NA",
    "Nauru": "NR",
    "Nepal": "NP",
    "Netherlands": "NL",
    "New Caledonia": "NC",
    "New Zealand": "NZ",
    "Nicaragua": "NI",
    "Niger": "NE",
    "Nigeria": "NG",
    "Niue": "NU",
    "Norfolk Island": "NF",
    "Northern Mariana Islands": "MP",
    "North Macedonia": "MK",
    "Northern Ireland": "GB",
    "Norway": "NO",
    "Oman": "OM",
    "Pakistan": "PK",
    "Palau": "PW",
    "Palestine": "PS",
    "Panama": "PA",
    "Papau New Guinea": "PA",
    "Paraguay": "PY",
    "Peru": "PE",
    "Philippines": "PH",
    "Pitcairn": "PN",
    "Poland": "PL",
    "Portugal": "PT",
    "Puerto Rico": "PR",
    "Qatar": "QA",
    "Republic of Ireland": "IE",
    "Romania": "RO",
    "Russia": "RU",
    "Rwanda": "RW",
    "Réunion": "RE",
    "Saint Barthelemy": "BL",
    "Saint Helena": "SH",
    "Saint Kitts and Nevis": "KN",
    "Saint Lucia": "LC",
    "Saint Martin": "MF",
    "Saint Pierre and Miquelon": "PM",
    "Saint Vincent and the Grenadines": "VC",
    "Samoa": "WS",
    "San Marino": "SM",
    "Sao Tome and Principe": "ST",
    "Saudi Arabia": "SA",
    "Scotland": "GB",
    "Senegal": "SN",
    "Serbia": "RS",
    "Seychelles": "SC",
    "Sierra Leone": "SL",
    "Singapore": "SG",
    "Sint Maarten": "SX",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Solomon Islands": "ZA",
    "Somalia": "SO",
    "South Africa": "ZA",
    "South Georgia and the South Sandwich Islands": "GS",
    "South Sudan": "SS",
    "Spain": "ES",
    "Sri Lanka": "LK",
    "Sudan": "SD",
    "Suriname": "SR",
    "Svalbard and Jan Mayen": "SJ",
    "Swaziland": "SE",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Syria": "SY",
    "Taiwan": "TW",
    "Tajikistan": "TJ",
    "Tanzania": "TZ",
    "Thailand": "TH",
    "Timor-Leste": "TL",
    "Togo": "TG",
    "Tokelau": "TK",
    "Tonga": "TO",
    "Trinidad and Tobago": "TT",
    "Tunisia": "TN",
    "Turkey": "TR",
    "Turkmenistan": "TM",
    "Turks and Caicos Islands": "TC",
    "Tuvalu": "TV",
    "Uganda": "UG",
    "Ukraine": "UA",
    "United Arab Emirates": "AE",
    "Uruguay": "UY",
    "USA": "US",
    "United States": "US",
    "Uzbekistan": "UZ",
    "Vanuatu": "VU",
    "Venezuela": "VE",
    "Vietnam": "VN",
    "British Virgin Islands": "VG",
    "US Virgin Islands": "VI",
    "Wallis and Futuna": "WF",
    "Wales": "GB",
    "Yemen": "YE",
    "Zambia": "ZM",
    "Zimbabwe": "ZW",
}

####################################
########## CLASS REGISTRY ##########
####################################

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

####################################
########## REQUEST CLASS ###########
####################################

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

    def __init__(self, season: str) -> None:
        cls = self.__class__
        subscription_time = get_config_arg("subscription_time")
        token = get_config_arg("token")
        self.reset_hour: int = int(subscription_time.split(':')[0])
        self.reset_minute: int = int(subscription_time.split(':')[1])
        self.reset_second: int = int(subscription_time.split(':')[2])
        self.season: str = season
        self.headers: Dict[str,str] = {
            "x-rapidapi-key": token,
            "x-rapidapi-host": cls._API_HOST
        }
        self.endpoint: str
        self.foreign_key: Optional[int]
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
            print("INFO: Ratelimit Reached. Sleeping...")
            sleep(cls._RATELIMIT_RESET - datetime.today().timestamp() + 1)

    def make_call(self, endpoint = None, params = None) -> Dict[str, Dict[str, Any]]:
        """ Method to make API call. """
        cls = self.__class__

        # View ratelimit before proceeding, sleep if needed
        self.get_ratelimit()

        # Make API request
        if endpoint:
          url = f"{cls._API_URL}{endpoint}"
          if params:
            api_response = get(url, headers=self.headers, params=params)
          else:
            api_response = get(url, headers=self.headers)
        else:
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
        # Ensure that HTTP request is successful
        assert request_code == 200, \
            f"""ERROR: HTTP Request '{url}' Failed. Status: {request_code}.
    Description: {request_content.get('message')}"""
        # Format API request content as JSON

        request_content = api_response.json()
        return request_content
    
    def check_types(self, response_data, attributes):
        """ Function to fix response data types and remove unnecessary keys. """
        # cast keys to correct types, discard unneeded keys
        unneeded_keys = []
        for k, v in response_data.items():
            if k in attributes:
                type_func = attributes.get(k)
                if type_func != date and v is not None:
                    response_data[k] = attributes.get(k)(v)
            else:
                unneeded_keys.append(k)
    
        # remove unneeded keys
        for key in unneeded_keys:
            del response_data[key]
        return response_data

    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """ Method to process API response. Implemented in subclasses. """
        pass
        
    def update(self) -> Dict[str, Any]:
        """ Method to gather, process, and store API data. """
        api_response = self.make_call()
        return self.process_response(api_response)

#######################################
########## LEAGUES SUBCLASS ###########
#######################################

class LeaguesRequest(Request):
    """ Class defining methods used during the collection and processing of
    data through API requests regarding Leagues data. """
    _REGISTER: bool = True

    def __init__(self, season: str) -> None:
        super().__init__(season)
        self.endpoint: str = "leagues"
        self.foreign_key: Optional[int] = None
        self.params: Dict[str, int] = { "season": self.season }

    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        leagues = response_data.get("response")
        """ Function to process the API response regarding league data. """
        orm_class = Leagues
        attributes = getattr(orm_class, "_TYPES")
        covered_leagues = get_manifest_arg("leagues")
        current_leagues = get_manifest_arg("league_ids")
    
        league_ids = dict()
        filtered_leagues = []
        for idx in range(len(leagues)):
            league = leagues[idx]
            league_name = league.get("league").get("name")
            league_country = league.get("country").get("name")
            if f"{league_name},{league_country}" in covered_leagues:
                if current_leagues is not None and league.get("league").get("id") in current_leagues:
                    continue
                temp_league = dict()
    
                # league data
                temp_league["name"] = league_name
                temp_league["id"] = league.get("league").get("id")
                temp_league["logo"] = league.get("league").get("logo")
                temp_league["type"] = league.get("league").get("type")
    
                # country data
                temp_league["country"] = league_country
                if temp_league.get("country") == "World":
                    temp_league["flag"] = temp_league.get("logo")
                else:
                    league_flag = league.get("country").get("flag")
                    temp_league["flag"] = "#" if league_flag is None else league_flag
    
                # generate output dict
                league_ids[temp_league.get("id")] = temp_league.get("name")
                filtered_leagues.append(self.check_types(temp_league, attributes))

        return {"ids":league_ids,"processed_data":filtered_leagues}

#####################################
########## TEAMS SUBCLASS ###########
#####################################

class TeamsRequest(Request):
    """ Class defining methods used during the collection and processing of
    data through API requests regarding Teams data. """
    _REGISTER: bool = True

    def __init__(self, league_id: int, season: str) -> None:
        super().__init__(season)
        self.endpoint: str = "teams"
        self.foreign_key: Optional[int] = league_id
        self.params: Dict[str, int] = {
            "league": league_id,
            "season": self.season
        }

    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """ Function to process the API response regarding team data. """
        teams = response_data.get("response")
        orm_class = Teams
        attributes = getattr(orm_class, "_TYPES")

        # get team IDs
        current_teams = get_manifest_arg("team_ids")
        if current_teams and current_teams.get(self.season):
            current_teams = current_teams.get(self.season) 
    
        team_ids = dict()
        for idx in range(len(teams)):
            if current_teams is not None and team.get("team").get("id") in current_teams:
                continue
            team = teams[idx]
            temp_team = dict()
    
            # team
            temp_team["id"] = team.get("team").get("id")
            temp_team["name"] = team.get("team").get("name")
            temp_team["logo"] = team.get("team").get("logo")
    
            # generate output dict
            teams[idx] = self.check_types(temp_team, attributes)
            team_ids[temp_team.get("id")] = {
                "team_name":temp_team.get("name"),
            }
        return { "ids": team_ids, "processed_data": teams }

#######################################
########## PLAYERS SUBCLASS ###########
#######################################

class PlayersRequest(Request):
    """ Class defining methods used during the collection and processing of
    data through API requests regarding Teams data. """
    _REGISTER: bool = True

    def __init__(
            self, 
            team_id: int, 
            processed_players: Dict[str, Any], 
            processed_stats: Dict[str, Any],
            season: str
        ) -> None:
        super().__init__(season)
        self.endpoint: str = "players"
        self.foreign_key: Optional[int] = team_id
        self.params: Dict[str, int] = {
            "team": team_id,
            "season": self.season
        }
        self.processed_players = processed_players
        self.processed_stats = processed_stats

    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """ Function to process the API response regarding player data. """
        global WORLD_LEAGUES
    
        if WORLD_LEAGUES is None:
            WORLD_LEAGUES = get_world_leagues()
    
        players = response_data.get("response")
        leagues_dict = get_manifest_arg("league_ids")
        current_players = get_manifest_arg("player_ids")
        orm_class = Stats
        attributes = getattr(orm_class, "_TYPES")
    
        for idx in range(len(players)):
            player = players[idx]
    
            #grab player stats from response
            if isinstance(player.get("statistics"), list):
                player_stats = player.get("statistics")
            else:
                player_stats = [player.get("statistics")]
    
            for stats in player_stats:
                temp_player = dict()
                # ensure only player stats for current leagues are being processed
                temp_league_id = stats.get("league").get("id")
                if temp_league_id not in leagues_dict.keys():
                    continue
    
                # only store statistics on players that have played
                if (not stats.get("games").get("minutes") or
                    float(stats.get("games").get("minutes")) == 0.0):
                    continue
    
                # player info needed for players table
                player_info = player.get("player")
                temp_player["player_id"] = player.get("player").get("id")  
                temp_player["name"] = player_info.get("name").replace("&apos;","'")
                temp_player["firstname"] = player_info.get("firstname")
                temp_player["lastname"] = player_info.get("lastname")
    
                # only store one record in players table
                # ensure player is not in DB
                if ((current_players is None or current_players is not None) 
                    and temp_player.get("player_id") not in current_players
                    and temp_player.get("player_id") not in self.processed_players.keys()):
                    # get player flag
                    country_abbrev = flags_dict.get(player_info.get("nationality"))
                    if country_abbrev is None:
                        print(f"INFO: No Flag Found For {player_info.get('nationality')}.")
                        flag = "#"
                    else:
                        flag = f"https://media.api-sports.io/flags/{country_abbrev.lower()}.svg"
    
                    # get player height and weight
                    height, weight = self.process_height_weight(
                                         player_info.get("height"),
                                         player_info.get("weight")
                                     )
    
                    # update processed_players
                    self.processed_players[temp_player.get("player_id")] = {
                            "id": temp_player.get("player_id"),
                            "name": temp_player.get("name"),
                            "firstname": temp_player.get("firstname"),
                            "lastname": temp_player.get("lastname"),
                            "age": player_info.get("age"),
                            "birth_date": self.process_birthdate(player_info.get("birth").get("date")),
                            "nationality": player_info.get("nationality"),
                            "flag": flag,
                            "height": height,
                            "weight": weight
                    }
    
                # player stat info
                temp_player["league_id"] = temp_league_id 
                temp_player["league_name"] = leagues_dict.get(temp_league_id)
                temp_player["team_id"] = stats.get("team").get("id")
                temp_player["team_name"] = stats.get("team").get("name")
                temp_player["season"] = stats.get("league").get("season")
                temp_player["id"] = self.generate_uid(
                                        temp_player.get("player_id"),
                                        temp_player.get("season"),
                                        temp_player.get("team_id"),
                                        temp_player.get("league_id")
                                    )
    
                # process player stats information
                if temp_player.get("id") in self.processed_stats.keys():
                    temp_player = self.process_stats(
                                            stats, 
                                            temp_player, 
                                            self.processed_stats.get(temp_player.get("id"))
                                        )
                else:
                    temp_player = self.process_stats(
                                            stats,
                                            temp_player, 
                                            None
                                        )
                processed_player = self.check_types(temp_player, attributes)
                self.processed_stats[processed_player.get("id")] = processed_player
        return self.processed_players, self.processed_stats

    def process_stats(self, stats, temp_player, previous_data):
        # Change later
        temp_player["is_current"] = True
    
        # games
        player_game_info = stats.get("games")
        temp_player["position"] = player_game_info.get("position")
        temp_player["rating"] = player_game_info.get("rating")
        temp_player["minutes_played"] = self.not_null(player_game_info.get("minutes"))
        temp_player["games_appearances"] = self.not_null(player_game_info.get("appearences")) #sic
        temp_player["games_started"] = self.not_null(player_game_info.get("lineups"))
        # substitutes
        player_sub_info = stats.get("substitutes")
        temp_player["games_bench"] = self.not_null(player_sub_info.get("bench"))
        temp_player["substitutions_in"] = self.not_null(player_sub_info.get("in"))
        temp_player["substitutions_out"] = self.not_null(player_sub_info.get("out"))
        # shots
        player_shot_info = stats.get("shots")
        temp_player["shots"] = self.not_null(player_shot_info.get("total"))
        temp_player["shots_on"] = self.not_null(player_shot_info.get("on"))
        temp_player["shots_on_pct"] = None
        
        # goals
        player_goal_info = stats.get("goals")
        temp_player["goals"] = self.not_null(player_goal_info.get("total"))
        temp_player["goals_conceded"] = self.not_null(player_goal_info.get("conceded"))
        temp_player["assists"] = self.not_null(player_goal_info.get("assists"))
        # passes
        player_pass_info = stats.get("passes")
        temp_player["passes"] = self.not_null(player_pass_info.get("total"))
        temp_player["passes_key"] = self.not_null(player_pass_info.get("key"))
        temp_player["passes_accuracy"] = player_pass_info.get("accuracy")
        # tackles
        player_tackle_info = stats.get("tackles")
        temp_player["tackles"] = self.not_null(player_tackle_info.get("total"))
        temp_player["blocks"] = self.not_null(player_tackle_info.get("blocks"))
        temp_player["interceptions"] = self.not_null(player_tackle_info.get("interceptions"))
        # duels
        player_duel_info = stats.get("duels")
        temp_player["duels"] = self.not_null(player_duel_info.get("total"))
        temp_player["duels_won"] = self.not_null(player_duel_info.get("won"))
        
        # dribbles
        player_dribble_info = stats.get("dribbles")
        temp_player["dribbles_past"] = self.not_null(player_dribble_info.get("past"))
        temp_player["dribbles_attempted"] = self.not_null(player_dribble_info.get("attempts"))
        temp_player["dribbles_succeeded"] = self.not_null(player_dribble_info.get("success"))
        
        # fouls
        player_foul_info = stats.get("fouls")
        temp_player["fouls_drawn"] = self.not_null(player_foul_info.get("drawn"))
        temp_player["fouls_committed"] = self.not_null(player_foul_info.get("committed"))
        # cards
        player_card_info = stats.get("cards")
        temp_player["cards_yellow"] = self.not_null(player_card_info.get("yellow"))
        temp_player["cards_red"] = self.not_null(player_card_info.get("red"))
        
        # penalty
        player_pen_info = stats.get("penalty")
        temp_player["penalties_won"] = self.not_null(player_pen_info.get("won"))
        temp_player["penalties_scored"] = self.not_null(player_pen_info.get("scored"))
        temp_player["penalties_missed"] = self.not_null(player_pen_info.get("missed"))
        temp_player["penalties_saved"] = self.not_null(player_pen_info.get("saved"))
        temp_player["penalties_committed"] = self.not_null(player_pen_info.get("commited")) #sic
    
    
        # if there is another stat for the player with the same team, league, and season
        # aggregate values that are different
        if previous_data is not None:
            static_keys = ([
                "id", "player_id", "name", "firstname", "lastname", 
                "league_name", "team_id", "team_name", "season",
                "rating", "position", "is_current"
            ])
            for key, value in previous_data.items():   
                if key not in static_keys and key in temp_player.keys():
                    if value is not None:
                        current_value = temp_player.get(key)
                        if current_value is None:
                            current_value = 0
                        # if current and previous values differ, aggregate
                        if value != float(current_value):
                            temp_player[key] = current_value + value
    
        # Calculate values
    
        # ensure >= 0 shots
        if temp_player.get("shots") > 0:
            temp_player["shots_on_pct"] = round(temp_player.get("shots_on") * 100
                                                / temp_player.get("shots"))
        temp_player["duels_won_pct"] = None
        # ensure >= 0 duels
        if temp_player.get("duels") > 0:
            temp_player["duels_won_pct"] = round(temp_player.get("duels_won") * 100
                                                 / temp_player.get("duels"))
    
        temp_player["dribbles_succeeded_pct"] = None
        # ensure >= 0 dribbles_attempted
        if temp_player.get("dribbles_attempted") > 0:
            temp_player["dribbles_succeeded_pct"] = round(temp_player.get("dribbles_succeeded") * 100
                                                          / temp_player.get("dribbles_attempted"))
    
        temp_player["penalties_scored_pct"] = None
        if (temp_player.get("penalties_scored") > 0 or
            temp_player.get("penalties_missed") > 0):
            temp_player["penalties_scored_pct"] = round(temp_player.get("penalties_scored") * 100
                                                        / (temp_player.get("penalties_scored")
                                                           + temp_player.get("penalties_missed")))
    
        return temp_player

    def process_height_weight(self, height, weight):
        if height and height != "":
            split_height = height.split(" ")
            if len(split_height) == 1:
                height_in = float(height) * 0.393701
                feet = int(height_in // 12)
                inches = round(height_in % 12)
                height = f"{feet}'{inches}\""
            elif len(split_height) == 2:
                height_in = float(split_height[0]) * 0.393701
                feet = int(height_in // 12)
                inches = round(height_in % 12)
                height = f"{feet}'{inches}\""
            else:
                print(height)
                height = "NULL"

        if weight and weight != "":
            split_weight = weight.split(" ")
            if len(split_weight) == 1:
                weight_lb = round(float(weight) * 2.20462)
                weight = f"{weight_lb} lbs"
            if len(split_weight) == 2:
                weight_lb = round(float(split_weight[0]) * 2.20462)
                weight = f"{weight_lb} lbs"
            else:
                print(weight)
                weight = "NULL"
        return height, weight

    def process_birthdate(self, birthdate_str):
        if birthdate_str:
            split_date = birthdate_str.split("/")
            split_date[0] = split_date[0].rjust(2,"0")
            split_date[1] = split_date[1].rjust(2,"0")
            split_date[2] = split_date[2]
            birthdate_str = "/".join(split_date)
            try:
                birthdate_date = datetime.strptime(
                                        birthdate_str,
                                        "%d/%m/%Y"
                                    ).date()
                return birthdate_date
            except:
                try:
                    birthdate_date = datetime.strptime(
                                            birthdate_str,
                                            "%m/%d/%Y"
                                        ).date()
                    return birthdate_date
                except:
                    birthdate_date = datetime.strptime(
                                            birthdate_str,
                                            "%Y/%m/%d"
                                        ).date()
                    return birthdate_date    

    
    def not_null(self, value):
        """ Function to turn quantitative stats to 0 if currently null. """
        return 0 if value is None else value
    
    def generate_uid(self, id, season, team_id, league_id):
        text = f"{id}{season}{team_id}{league_id}"
        ciphertext = md5(text.encode()).hexdigest()
        return ciphertext
    
