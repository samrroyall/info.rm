import os
from typing import List
import logging

# API URL
# api_url: str = "https://api-football-v1.p.rapidapi.com/v3/" # v3 url
api_url: str = "https://api-football-beta.p.rapidapi.com/" # beta url
# API HOST
api_host: str = "api-football-beta.p.rapidapi.com"
api_host_header: str = "x-rapidapi-host"
# API KEY
assert "API_KEY" in os.environ, "'API_KEY' is not defined as an environment variable"
api_key: str = os.environ.get("API_KEY")
api_key_header: str = "x-rapidapi-key"
# CURRENT LEAGUES
top_five_league_ids: List[int] = [
    78, # Bundesliga 1, Germany
    61, # Ligue 1, France
    39, # Premier League, England
    140, # Primera Division, Spain
    135 # Serie A, Italy
]
other_league_ids: List[int] = [
    2, # UEFA Champions League
    3, # UEFA Europa League
    94, # Primeira Liga, Portugal
    235, # Premier League, Russia
    88, # Eredivisie, Netherlands
    203, # Super Lig, Turkey
    218, # Tipp3 Bundesliga, Austria
    119 # Superligaen, Denmark
]
initial_league_ids: List[int] = top_five_league_ids + other_league_ids
international_league_ids: List[int] = [
    2, # UEFA Champions League
    3, # UEFA Europa League
]
# List of allowable log levels
LogLevel = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]