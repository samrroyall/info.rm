#!/usr/bin/env python3
import pathlib

current_path = pathlib.Path(__file__).parent.parent.absolute()

def config_exists(season):
    config_path = pathlib.PurePath.joinpath(current_path, f"config/config-{season}.ini")
    return pathlib.Path.exists(config_path)

def read_config(season):
    """ Function for reading configuration information from config.ini """
    config_path = pathlib.PurePath.joinpath(current_path, f"config/config-{season}.ini")
    config_args = {}
    with open(config_path, "r") as f:
        for line in f.readlines():
            key_value_list = line.strip().split("=")
            config_args[key_value_list[0]] = key_value_list[1]
    return config_args

def write_config(args):
    """ Function for writing configuration information from config.ini """
    season = args.get("current_season").split("-")[0]
    config_path = pathlib.PurePath.joinpath(current_path, f"config/config-{season}.ini")
    with open(config_path, "w") as f:
        for key,value in args.items():
            f.write(f"{key}={value}\n")

def get_config_arg(config_arg, season):
    """ Function for reading IDs from config-XXXX.ini """
    config_args = read_config(season)
    if config_args.get(config_arg):
        return config_args.get(config_arg)
    else:
        return None

def set_config_arg(config_arg, value, season):
    """ Function for writing IDs to config.ini """
    config_args = read_config(season)
    config_args[config_arg] = value
    write_config(config_args)


