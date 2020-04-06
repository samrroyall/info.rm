#!/usr/bin/env python3

from datetime import datetime, date
from hashlib import md5

from config import get_config_arg
from orm import Leagues, Teams, Players, Stats
import sys

###########################
####### FLAGS DICT ########
###########################

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
###########################
##### PROCESS HELPERS #####
###########################

def get_alternative_league(league_name):
    if league_name == "Bundesliga 1":
        return "Bundesliga"
    elif league_name == "Primera Division":
        return "La Liga"
    else:
        return None

def process_height_weight(height, weight):
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

def process_birthdate(birthdate_str) -> date:
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

# no type checking on functions dealing with JSON data
def check_keys(response_data, attributes):
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

def not_null(value):
    """ Function to turn quantitative stats to 0 if currently null. """
    return 0 if value is None else value

def generate_uid(id, season, team_id):
    text = f"{id}{season}{team_id}"
    ciphertext = md5(text.encode()).hexdigest()
    return ciphertext

# no type checking on functions dealing with JSON data
def process_stats(stats, temp_player, previous_data):
    # games
    player_game_info = stats.get("games")
    temp_player["position"] = player_game_info.get("position")
    temp_player["rating"] = player_game_info.get("rating")
    temp_player["minutes_played"] = not_null(player_game_info.get("minutes"))
    temp_player["games_appearances"] = not_null(player_game_info.get("appearences")) #sic
    temp_player["games_started"] = not_null(player_game_info.get("lineups"))
    # substitutes
    player_sub_info = stats.get("substitutes")
    temp_player["games_bench"] = not_null(player_sub_info.get("bench"))
    temp_player["substitutions_in"] = not_null(player_sub_info.get("in"))
    temp_player["substitutions_out"] = not_null(player_sub_info.get("out"))
    # shots
    player_shot_info = stats.get("shots")
    temp_player["shots"] = not_null(player_shot_info.get("total"))
    temp_player["shots_on"] = not_null(player_shot_info.get("on"))
    temp_player["shots_on_pct"] = None
    
    # goals
    player_goal_info = stats.get("goals")
    temp_player["goals"] = not_null(player_goal_info.get("total"))
    temp_player["goals_conceded"] = not_null(player_goal_info.get("conceded"))
    temp_player["assists"] = not_null(player_goal_info.get("assists"))
    # passes
    player_pass_info = stats.get("passes")
    temp_player["passes"] = not_null(player_pass_info.get("total"))
    temp_player["passes_key"] = not_null(player_pass_info.get("key"))
    temp_player["passes_accuracy"] = player_pass_info.get("accuracy")
    # tackles
    player_tackle_info = stats.get("tackles")
    temp_player["tackles"] = not_null(player_tackle_info.get("total"))
    temp_player["blocks"] = not_null(player_tackle_info.get("blocks"))
    temp_player["interceptions"] = not_null(player_tackle_info.get("interceptions"))
    # duels
    player_duel_info = stats.get("duels")
    temp_player["duels"] = not_null(player_duel_info.get("total"))
    temp_player["duels_won"] = not_null(player_duel_info.get("won"))
    
    # dribbles
    player_dribble_info = stats.get("dribbles")
    temp_player["dribbles_past"] = not_null(player_dribble_info.get("past"))
    temp_player["dribbles_attempted"] = not_null(player_dribble_info.get("attempts"))
    temp_player["dribbles_succeeded"] = not_null(player_dribble_info.get("success"))
    
    # fouls
    player_foul_info = stats.get("fouls")
    temp_player["fouls_drawn"] = not_null(player_foul_info.get("drawn"))
    temp_player["fouls_committed"] = not_null(player_foul_info.get("committed"))
    # cards
    player_card_info = stats.get("cards")
    temp_player["cards_yellow"] = not_null(player_card_info.get("yellow"))
    temp_player["cards_red"] = not_null(player_card_info.get("red"))
    
    # penalty
    player_pen_info = stats.get("penalty")
    temp_player["penalties_won"] = not_null(player_pen_info.get("won"))
    temp_player["penalties_scored"] = not_null(player_pen_info.get("scored"))
    temp_player["penalties_missed"] = not_null(player_pen_info.get("missed"))
    temp_player["penalties_saved"] = not_null(player_pen_info.get("saved"))
    temp_player["penalties_committed"] = not_null(player_pen_info.get("commited")) #sic


    if previous_data:
        static_keys = ([
            "id", "player_id", "name", "firstname", "lastname", 
            "league_name", "team_id", "team_name", "season",
            "rating", "position"
        ])
        for key, value in previous_data.items():   
            if key not in static_keys and key in temp_player.keys():
                if value is not None:
                    current_value = temp_player.get(key)
                    if current_value is None:
                        current_value = 0
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
        temp_player["dribbles_succeeded_pct"] = round(
                                            temp_player.get("dribbles_succeeded")
                                            / temp_player.get("dribbles_attempted")
                                            * 100
                                        )

    temp_player["penalties_scored_pct"] = None
    if (temp_player.get("penalties_scored") > 0 or
        temp_player.get("penalties_missed") > 0):
        temp_player["penalties_scored_pct"] = round(
                                            temp_player.get("penalties_scored") /
                                            (temp_player.get("penalties_scored")
                                                + temp_player.get("penalties_missed"))
                                            * 100
                                        )

    return temp_player

#############################
##### PROCESS FUNCTIONS #####
#############################

# no type checking on functions dealing with JSON data
def process_leagues(leagues, _, season):
    """ Function to process the API response regarding league data. """
    orm_class = Leagues
    attributes = getattr(orm_class, "_TYPES")
    current_leagues = eval(get_config_arg("leagues", season))

    league_ids = dict()
    filtered_leagues = []
    for idx in range(len(leagues)):
        league = leagues[idx]
        league_name = league.get("league").get("name")
        league_country = league.get("country").get("name")
        if f"{league_name},{league_country}" in current_leagues:
            temp_league = dict()

            # league
            temp_league["name"] = league_name
            temp_league["id"] = league.get("league").get("id")
            temp_league["logo"] = league.get("league").get("logo")
            temp_league["type"] = league.get("league").get("type")

            # country
            temp_league["country"] = league_country
            temp_league["flag"] = league.get("country").get("flag")

            # generate output dict
            league_ids[temp_league.get("id")] = temp_league.get("name")
            filtered_leagues.append(check_keys(temp_league, attributes))
    return {"ids":league_ids,"processed_data":filtered_leagues}

# no type checking on functions dealing with JSON data
def process_teams(teams, league_id, season):
    """ Function to process the API response regarding team data. """
    league_name = eval(get_config_arg("league_ids", season)).get(league_id)
    orm_class = Teams
    attributes = getattr(orm_class, "_TYPES")

    team_ids = dict()
    for idx in range(len(teams)):
        team = teams[idx]
        temp_team = dict()
        temp_team["league_id"] = league_id
        temp_team["league_name"] = league_name

        # team
        temp_team["id"] = team.get("team").get("id")
        temp_team["name"] = team.get("team").get("name")
        temp_team["logo"] = team.get("team").get("logo")

        # generate output dict
        teams[idx] = check_keys(temp_team, attributes)
        team_ids[temp_team.get("id")] = {
            "team_name":temp_team.get("name"),
            "league_name":league_name,
            "league_id":league_id
        }
    return {"ids":team_ids,"processed_data":teams}

def process_players(players, team_id, season, filtered_players, filtered_stats, request_instance):
    """ Function to process the API response regarding player data. """
    config_values = eval(get_config_arg("team_ids", season)).get(team_id)
    league_name = config_values.get("league_name", season)
    alt_league_name = get_alternative_league(league_name)
    orm_class = Stats
    attributes = getattr(orm_class, "_TYPES")

    for idx in range(len(players)):
        player = players[idx]

        if isinstance(player.get("statistics"), list):
            player_stats = player.get("statistics")
        else:
            player_stats = [player.get("statistics")]

        for stats in player_stats:
            temp_player = dict()

            # ensure only player stats for current leagues are being processed
            temp_league_name = stats.get("league").get("name")
            if temp_league_name != league_name and (alt_league_name is None or
                temp_league_name != alt_league_name):
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
            if temp_player.get("player_id") not in filtered_players.keys() :

                # get player flag
                country_abbrev = flags_dict.get(player_info.get("nationality"))
                if country_abbrev is None:
                    print(f"INFO: No Flag Found For {player_info.get('nationality')}.")
                    flag = "#"
                else:
                    flag = f"https://media.api-sports.io/flags/{country_abbrev.lower()}.svg"

                # get player height and weight
                height, weight = process_height_weight(
                                            player_info.get("height"),
                                            player_info.get("weight")
                                        )

                # update filtered_players
                filtered_players[temp_player.get("player_id")] = {
                        "id": temp_player.get("player_id"),
                        "name": temp_player.get("name"),
                        "firstname": temp_player.get("firstname"),
                        "lastname": temp_player.get("lastname"),
                        "age": player_info.get("age"),
                        "birth_date": process_birthdate(
                                            player_info.get("birth").get("date")
                                        ),
                        "nationality": player_info.get("nationality"),
                        "flag": flag,
                        "height": height,
                        "weight": weight
                    }

            # player info
            temp_player["league_id"] = stats.get("league").get("id")
            temp_player["league_name"] = league_name
            temp_player["team_id"] = stats.get("team").get("id")
            temp_player["team_name"] = stats.get("team").get("name")
            temp_player["season"] = int(season)
            temp_player["id"] = generate_uid(
                                    temp_player.get("player_id"),
                                    temp_player.get("season"),
                                    temp_player.get("team_id")
                                )

            if temp_player.get("id") in filtered_stats.keys():
                temp_player = process_stats(stats, temp_player, filtered_stats.get(temp_player.get("id")))
            else:
                temp_player = process_stats(stats, temp_player, None)
            processed_player = check_keys(temp_player, attributes)
            filtered_stats[processed_player.get("id")] = processed_player
    return filtered_players, filtered_stats
