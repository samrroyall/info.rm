#!/usr/bin/env python3
import pathlib
from typing import Dict, Union, Any

def read_config() -> Dict[str,str]:
    """ Function for reading configuration information from config.ini """
    current_path = pathlib.Path(__file__).parent.absolute()
    config_args = {}
    with open(f"{current_path}/config.ini", "r") as f:
        for line in f.readlines():
            key_value_list = line.strip().split("=")
            config_args.update({key_value_list[0]:key_value_list[1]})
    return config_args

def write_config(args: Dict[str,Union[str,int]]) -> None:
    """ Function for writing configuration information from config.ini """
    current_path = pathlib.Path(__file__).parent.absolute()
    with open(f"{current_path}/config.ini", "w") as f:
        for key,value in kwargs.items():
            f.write(f"{key}={value}\n")

def get_config_arg(config_arg: str) -> Any:
    """ Function for reading IDs from config.ini """
    config_args = read_config()
    assert config_args.get(config_arg), \
        f"ERROR: Config file does not have argument {config_arg}."
    return config_args.get(config_arg)

def set_config_arg(config_arg: str, value: Any) -> None:
    """ Function for writing IDs to config.ini """
    config_args = read_config()
    assert config_args.get(config_arg), \
        f"ERROR: Config file does not have argument {config_arg}."
    config_args[config_arg] = value
    write_config(config_args)


