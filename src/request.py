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

    _REGISTER: bool = False
    _API_URL: str = "https://api-football-beta.p.rapidapi.com/"
    _API_HOST: str = "api-football-beta.p.rapidapi.com"
    #_API_RATELIMIT_HEADER: str = "x-ratelimit-requests-limit"
    #_API_RATELIMIT_REMAINING_HEADER: str = "x-ratelimit-requests-remaining"
    
    def __init__(self, season: str) -> None:
        cls = self.__class__
        subscription_time = get_config_arg("subscription_time")
        token = get_config_arg("token")
        self.season: str = season
        self.headers: Dict[str,str] = {
            "x-rapidapi-key": token,
            "x-rapidapi-host": cls._API_HOST
        }
        self.endpoint: str
        self.foreign_key: Optional[int]
        self.params: Dict[str, int]

    def make_call(self, endpoint = None, params = None) -> Tuple[Dict[str, Dict[str, Any]], Optional[int]]:
        """ Method to make API call. """
        # Set API request parameters
        url = f"{self.__class__._API_URL}{endpoint}" if endpoint else f"{self.__class__._API_URL}{self.endpoint}"
        if params is not None:
            params.update(self.params)
            call_params = params
        else:
            call_params = self.params

        # Make API request
        api_response = get(url, headers=self.headers, params=call_params)

        # Ensure that Minute ratelimit is not reached
        request_code = api_response.status_code
        if request_code == 429:
            print("INFO: Minute Ratelimit Reached. Sleeping Now...")
            sleep(61)
            print("INFO: Retrying Call...")
            return self.make_call(endpoint, params)

        # Ensure that HTTP request is successful
        assert request_code == 200, \
            f"""ERROR: HTTP Request '{url}' Failed. Status: {request_code}.
    Description: {request_content.get('message')}"""
        # Format API request content as JSON
        request_content = api_response.json()

        # Check pagination
        current_page = request_content.get("paging").get("current")
        num_pages = request_content.get("paging").get("total")
        if current_page < num_pages:
            next_page = current_page + 1
        else:
            next_page = None

        return request_content, next_page

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
        """ Method to process API response. Implemented in child classes. """
        pass

    def update(self) -> Dict[str, Any]:
        """ Method to gather, process, and store API data. """
        # obtain API response
        api_response, next_page = self.make_call()

        # handle pagination
        while next_page:
            print(f"INFO: Calling Next Response Page ({next_page})...")
            new_response, next_page = self.make_call(params = {"page": next_page})
            api_response["response"] += new_response.get("response")

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
        attributes = getattr(Leagues, "_TYPES")
        covered_leagues = get_manifest_arg("leagues")
        current_leagues = get_manifest_arg("league_ids")

        league_ids = dict()
        filtered_leagues = []
        for idx in range(len(leagues)):
            league = leagues[idx]
            if f"{league.get('league').get('name')},{league.get('country').get('name')}" in covered_leagues:
                if current_leagues is not None and league.get("league").get("id") in current_leagues:
                    continue
                temp_league = dict()

                # league data
                for key in ["name", "id", "logo", "type"]:
                    temp_league[key] = league.get("league").get(key)

                # country data
                temp_league["country"] = league.get("country").get("name")
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
        attributes = getattr(Teams, "_TYPES")

        # get team IDs 
        current_teams = get_manifest_arg("team_ids")
        if current_teams and self.season in current_teams:
            current_teams = current_teams.get(self.season)

        team_ids = dict()
        for idx in range(len(teams)):
            if current_teams is not None and team.get("team").get("id") in current_teams:
                continue
            team = teams[idx]
            temp_team = dict()

            # team
            for key in ["id", "name", "logo"]:
                temp_team[key] = team.get("team").get(key)

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

    _STAT_KEYS = {
        "position": "position",
        "rating": "rating",
        "shots": "total",
        "shots_on": "on",
        "goals": "total",
        "goals_conceded": "conceded",
        "assists": "assists",
        "passes": "total",
        "passes_key": "key",
        "passes_accuracy": "accuracy",
        "tackles": "total",
        "blocks": "blocks",
        "interceptions": "interceptions",
        "duels": "total",
        "duels_won": "won",
        "dribbles_past": "past",
        "dribbles_attempted": "attempts",
        "dribbles_succeeded": "success",
        "fouls_drawn": "drawn",
        "fouls_committed": "committed",
        "cards_yellow": "yellow",
        "cards_red": "red",
        "penalties_won": "won",
        "penalties_committed": "commited", #sic
        "penalties_scored": "scored",
        "penalties_missed": "missed",
        "penalties_saved": "saved",
        "minutes_played": "minutes",
        "games_appearances": "appearences", #sic
        "games_started": "lineups",
        "games_bench": "bench",
        "substitutions_in": "in",
        "substitutions_out": "out"
    }

    _FLAGS_DICT = {
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

    _WORLD_LEAGUES = None

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
        if self.__class__._WORLD_LEAGUES is None:
            self.__class__._WORLD_LEAGUES = get_world_leagues()

        players = response_data.get("response") # api response
        leagues_dict = get_manifest_arg("league_ids") # leagues processed
        current_players = get_manifest_arg("player_ids") # players processed
        attributes = getattr(Stats, "_TYPES") # variable types

        for idx in range(len(players)):
            player = players[idx]

            # grab player stats from response
            player_stats = player.get("statistics") if isinstance(player.get("statistics"), list) else [player.get("statistics")]

            for stats in player_stats:
                temp_player = dict()

                # ensure only player stats for current leagues are being processed
                if stats.get("league").get("id") not in leagues_dict.keys():
                    continue

                # only store statistics on players that have played
                if (not stats.get("games").get("minutes") or float(stats.get("games").get("minutes")) == 0.0):
                    continue

                # player info needed for players table
                player_info = player.get("player")
                temp_player["player_id"] = player.get("player").get("id")
                temp_player["name"] = player_info.get("name").replace("&apos;","'")
                temp_player["firstname"] = player_info.get("firstname")
                temp_player["lastname"] = player_info.get("lastname")

                # only store one record in players table... ensure player is not in DB
                if (current_players is None or (current_players is not None
                    and temp_player.get("player_id") not in current_players
                    and temp_player.get("player_id") not in self.processed_players.keys())):

                    # get player flag
                    country_abbrev = self.__class__._FLAGS_DICT.get(player_info.get("nationality"))
                    if country_abbrev is None:
                        print(f"INFO: No Flag Found For {player_info.get('nationality')}...")
                        flag = "#"
                    else:
                        flag = f"https://media.api-sports.io/flags/{country_abbrev.lower()}.svg"

                    # get player height and weight
                    height, weight = self.process_height_weight(player_info.get("height"), player_info.get("weight"))

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
                temp_player["league_id"] = stats.get("league").get("id")
                temp_player["league_name"] = leagues_dict.get(stats.get("league").get("id"))
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
                    temp_player = self.process_stats(stats, temp_player, None)
                processed_player = self.check_types(temp_player, attributes)
                self.processed_stats[processed_player.get("id")] = processed_player
        return self.processed_players, self.processed_stats

    def process_stats(self, stats, temp_player, previous_data):
        # Change later
        temp_player["is_current"] = True

        stat_sections = [
            ("games", ["position", "rating", "minutes_played", "games_appearances", "games_started"]),
            ("substitutes", ["games_bench", "substitutions_in", "substitutions_out"]),
            ("shots", ["shots", "shots_on"]),
            ("goals", ["goals", "goals_conceded", "assists"]),
            ("passes", ["passes", "passes_key", "passes_accuracy"]),
            ("tackles", ["tackles", "blocks", "interceptions"]),
            ("dribbles", ["dribbles_past", "dribbles_attempted", "dribbles_succeeded"]),
            ("duels", ["duels", "duels_won"]),
            ("penalty", ["penalties_won", "penalties_scored", "penalties_missed", "penalties_saved", "penalties_committed"])
        ]

        # get values
        for values_key, keys in stat_sections:
            temp_player = self.grab_stat_values(keys,stats.get(values_key),temp_player)

        # if there is another stat for the player with the same uid aggregate values that are different
        if previous_data is not None:
            static_keys = ([
                "id", "player_id", "name", "firstname", "lastname", "league_name",
                "team_id", "team_name", "season", "rating", "position", "is_current"
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

        # ensure >= 0 shots taken
        if temp_player.get("shots") > 0:
            temp_player["shots_on_pct"] = round(
                temp_player.get("shots_on") * 100
                / temp_player.get("shots")
            )
        # ensure >= 0 duels
        if temp_player.get("duels") and temp_player.get("duels") > 0:
            temp_player["duels_won_pct"] = round(
                temp_player.get("duels_won") * 100
                / temp_player.get("duels")
            )
        # ensure >= 0 dribbles_attempted
        if temp_player.get("dribbles_attempted") > 0:
            temp_player["dribbles_succeeded_pct"] = round(
                temp_player.get("dribbles_succeeded") * 100
                / temp_player.get("dribbles_attempted")
            )
        # ensure >= 0 penalties taken
        if (temp_player.get("penalties_scored") > 0 or temp_player.get("penalties_missed") > 0):
            temp_player["penalties_scored_pct"] = round(
                temp_player.get("penalties_scored") * 100
                / (temp_player.get("penalties_scored") + temp_player.get("penalties_missed"))
            )
        return temp_player

    ##########################################
    ######## PROCESS HELPER FUNCTIONS ########
    ##########################################

    def process_height_weight(self, height, weight):
        if height and len(height) > 0:
            height = height[:height.find(" ")]
            height_in = float(height) * 0.393701
            height = f"{int(height_in // 12)}'{round(height_in % 12)}\""
        else:
            height = "N/A"
        if weight and len(weight) > 0:
            weight = weight[:weight.find(" ")]
            weight = f"{round(float(weight) * 2.20462)} lbs"
        else:
            weight = "N/A"
        return height, weight

    def process_birthdate(self, birthdate_str):
        if birthdate_str is None or len(birthdate_str) == 0:
            return date(1900, 1, 1)
        split_char = [char for char in ["/", "-"] if char in birthdate_str]
        assert len(split_char) == 1, f"ERROR: Unrecognized Birthdate format: {birthdate_str}"
        split_date = birthdate_str.split(split_char[0])
        year_idx = [idx for idx in list(range(len(split_date))) if len(split_date[idx]) == 4]
        assert len(year_idx) == 1, f"ERROR: Unrecognized Birthdate format: {birthdate_str}"
        assert year_idx[0] == 0 or year_idx[0] == 2, f"ERROR: Unrecognized Birthdate format: {birthdate_str}"
        if year_idx[0] == 0:
            split_date[1] = split_date[1].rjust(2,"0")
            split_date[2] = split_date[2].rjust(2,"0")
            birthdate_str = "/".join(split_date)
            try:
                return datetime.strptime(birthdate_str, "%Y/%m/%d").date()
            except:
                return datetime.strptime(birthdate_str, "%Y/%d/%m").date()
        else:
            split_date[0] = split_date[0].rjust(2,"0")
            split_date[1] = split_date[1].rjust(2,"0")
            birthdate_str = "/".join(split_date)
            try:
                return datetime.strptime(birthdate_str, "%m/%d/%Y").date()
            except:
                return datetime.strptime(birthdate_str, "%d/%m/%Y").date()

    def grab_stat_values(self, keys, values, temp_player) -> Dict[str, Any]:
        for key in keys:
            temp_player[key] = self.not_null(values.get(self.__class__._STAT_KEYS.get(key)))
        return temp_player

    def not_null(self, value):
        """ Function to turn quantitative stats to 0 if currently null. """
        return 0 if value is None else value

    def generate_uid(self, id: int, season: int, team_id: int, league_id: int) -> str:
        """ Function to calculate and return a player's UID. """
        return md5(f"{id}{season}{team_id}{league_id}".encode()).hexdigest()
