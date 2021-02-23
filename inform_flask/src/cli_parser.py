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
            "leagues",
            "teams",
            "players",
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
    args = parser.parse_args()
    
    if args.action == "setup":
        assert args.token, \
            "info.rm.py: error: setup procedure requires the following arguments: -t/--token"
    else: 
        assert not args.token, \
            f"info.rm.py: error: {args.action} procedure requires the following arguments: -s/--season"
        assert args.current_season, \
            f"info.rm.py: error: {args.action} procedure requires the following arguments: -s/--season"
        assert len(args.current_season.split("-")) == 2, \
            "info.rm.py: error: -s/--season must be in form YYYY-YYYY."
    return args

