#!/usr/bin/env python3
import pathlib
import os.path

def config_exists():
    current_path = pathlib.Path(__file__).parent.absolute()
    config_path = pathlib.PurePath.joinpath(current_path, "config.ini")
    return pathlib.Path.exists(config_path)

def read_config():
    """ Function for reading configuration information from config.ini """
    current_path = pathlib.Path(__file__).parent.absolute()
    config_args = {}
    with open(f"{current_path}/config.ini", "r") as f:
        for line in f.readlines():
            key_value_list = line.strip().split("=")
            config_args[key_value_list[0]] = key_value_list[1]
    return config_args

def write_config(args):
    """ Function for writing configuration information from config.ini """
    current_path = pathlib.Path(__file__).parent.absolute()
    with open(f"{current_path}/config.ini", "w") as f:
        for key,value in args.items():
            f.write(f"{key}={value}\n")

def get_config_arg(config_arg):
    """ Function for reading IDs from config.ini """
    config_args = read_config()
    if config_args.get(config_arg):
        return config_args.get(config_arg)
    else:
        return None

def set_config_arg(config_arg, value):
    """ Function for writing IDs to config.ini """
    config_args = read_config()
    config_args[config_arg] = value
    write_config(config_args)


