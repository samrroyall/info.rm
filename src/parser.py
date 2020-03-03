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
            "insert_all",
            "insert_leagues",
            "insert_teams",
            "insert_players",
            "update_players",
            "query_db"
        ],
        help = "procedure to be run by info.rm"
    )
    #parser.add_argument(
    #    "-p",
    #    "--password",
    #    type = str,
    #    dest = "password",
    #    help = "user's password used to encrypt the DB"
    #)
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
    if args.action == "setup" and (not args.token or not args.current_season or not args.subscription_time):
        print("info.rm.py: error: setup procedure requires the following arguments: -t/--token, -s/--season, and -st/--subscription-time")
        parser.print_help()
        sys.exit(1)
    elif args.action != "setup" and (args.token or args.current_season or args.subscription_time):
        print(f"info.rm.py: error: {args.action} procedure takes no additional arguments")
        parser.print_help()
        sys.exit(1)
    else:
        return args

