#!/usr/bin/env python3
import pathlib

current_path = pathlib.Path(__file__).parent.absolute()
CONFIG_PATH = pathlib.PurePath.joinpath(current_path, f"config.ini")

def config_exists():
    return pathlib.Path.exists(CONFIG_PATH)

def read_config():
    """ Function for reading configuration information from config.ini """
    assert config_exists(), "config.ini does not exist"
    config_args = {}
    with open(CONFIG_PATH, "r") as f:
        for line in f.readlines():
            key_value_list = line.strip().split("=")
            config_args[key_value_list[0]] = key_value_list[1]
    return config_args

def write_config(args):
    """ Function for writing configuration information from config.ini """
    with open(CONFIG_PATH, "w") as f:
        for key,value in args.items():
            f.write(f"{key}={value}\n")

def get_config_arg(arg):
    """ Function for reading IDs from manifest """
    assert config_exists(), "config.ini does not exist."
    config_args = read_config()
    if arg in config_args:
        return config_args.get(arg)
    else:
        return None

