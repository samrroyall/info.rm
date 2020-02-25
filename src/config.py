#!/usr/bin/env python3
import pathlib

def read_config():
    """ Function for reading configuration information from config.ini """
    current_path = pathlib.Path(__file__).parent.absolute()
    config_args = {}
    with open(f"{current_path}/config.ini", "r") as f:
        for line in f.readlines():
            key_value_list = line.strip().split("=")
            config_args.update({key_value_list[0]:key_value_list[1]})
    return config_args

def write_config(kwargs):
    """ Function for writing configuration information from config.ini """
    current_path = pathlib.Path(__file__).parent.absolute()
    with open(f"{current_path}/config.ini", "w") as f:
        for key,value in kwargs.items():
            f.write(f"{key}={value}\n")

def get_ids(action, config_args):
    """ Function for reading IDs from config.ini """
    # handle team and player insert/update operations differently
    sub_action = action.split("_")[1]
    if sub_action == "teams":
        key_string = "league_ids"
    elif sub_action == "players":
        key_string = "team_ids"
    else:
        key_string = None
    if key_string and key_string in config_args:
        return eval(config_args.get(key_string))
    else:
        return None

def set_ids(id_dict):
    """ Function for writing IDs to config.ini """
    current_path = pathlib.Path(__file__).parent.absolute()
    config_args = read_config()
    config_args.update(id_dict)
    write_config(config_args)


