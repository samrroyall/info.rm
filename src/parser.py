#!/usr/bin/env python3

import sys
import argparse

num_to_league = {
    1: "Premier League,England",
    2: "Bundesliga 1,Germany",
    3: "Primera Division,Spain",
    4: "Ligue 1,France",
    5: "Serie A,Italy"
}

def initialize_parser():
    parser = argparse.ArgumentParser(description="""
            _       ____                     
           (_)___  / __/___    _________ ___ 
          / / __ \/ /_/ __ \  / ___/ __ `__ \ 
         / / / / / __/ /_/ / / /  / / / / / /
        /_/_/ /_/_/  \____(_)_/  /_/ /_/ /_/ 
        """, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "action",
        type = str,
        choices = [
            "setup",
            "insert_leagues",
            "insert_teams",
            "insert_players",
            "update_players",
        ],
        help = "procedure to be run by info.rm"
    )
    parser.add_argument(
        "-t",
        "--token",
        type = str,
        dest = "token",
        help = "(setup only) the user's API-Football access token"
    )
    parser.add_argument(
        "-s",
        "--season",
        type = str,
        dest = "current_season",
        help = "(setup only) the season the user desires data on: 'YYYY-YYYY'"
    )
    parser.add_argument(
        "-st",
        "--subscription-time",
        type = str,
        dest = "subscription_time",
        help = "(setup only) the hour and minute a user's API-Football subscription began: 'HH:MM'"
    )    
    parser.add_argument(
        "-l",
        "--leagues",
        type = int,
        nargs = "*",
        choices = [1,2,3,4,5],
        dest = "leagues",
        help = "(setup only) leagues to be tracked:\n\t1 - Premier League,\n\t2 - Bundesliga,\n\t3 - La Liga,\n\t4 - Ligue 1\n\t5 - Serie A"
    )
    args = parser.parse_args()
    if args.action == "setup":
        assert args.token and args.current_season and args.subscription_time and args.leagues, \
            "info.rm.py: error: setup procedure requires the following arguments: -t/--token, -s/--season, and -st/--subscription-time"
        setattr(args, "leagues", [num_to_league.get(num) for num in getattr(args, "leagues")])
    else: 
        assert not args.token and not args.current_season and not args.subscription_time, \
            f"info.rm.py: error: {args.action} procedure takes no additional arguments"
    return args

