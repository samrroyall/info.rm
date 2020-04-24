#!/usr/bin/env python3

import sys
import argparse

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
    args = parser.parse_args()
    assert len(args.current_season.split("-")) == 2, \
        "info.rm.py: error: -s/--season must be in form YYYY-YYYY."
    if args.action == "setup":
        assert args.token and args.current_season and args.subscription_time, \
            "info.rm.py: error: setup procedure requires the following arguments: -t/--token, -s/--season, and -st/--subscription-time"
        assert len(args.subscription_time.split(":")) == 3, \
            "info.rm.py: error: -st/--subscription-time must be in form HH:MM:SS."
    else: 
        assert not args.token and not args.subscription_time, \
            f"info.rm.py: error: {args.action} procedure only takes -s/--season as an argument"
        assert args.current_season, \
            f"info.rm.py: error: {args.action} procedure requires -s/--season as an argument"
    return args

