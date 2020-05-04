#!/usr/bin/env python3
import pathlib

current_path = pathlib.Path(__file__).parent.parent.absolute()
MANIFEST_PATH = pathlib.PurePath.joinpath(current_path, f"MANIFEST")

def manifest_exists():
    return pathlib.Path.exists(MANIFEST_PATH)

def read_manifest():
    """ Function for reading manifest """
    assert manifest_exists(), "MANIFEST does not exist."
    manifest_args = {}
    with open(MANIFEST_PATH, "r") as f:
        for line in f.readlines():
            key_value_list = line.strip().split("=")
            manifest_args[key_value_list[0]] = key_value_list[1]
    return manifest_args

def write_manifest(args):
    """ Function for writing to the manifest """
    with open(MANIFEST_PATH, "w") as f:
        for key,value in args.items():
            f.write(f"{key}={value}\n")

def get_arg(arg, season=None):
    """ Function for reading IDs from manifest """
    assert manifest_exists(), "MANIFEST does not exist."
    manifest_args = read_manifest()
    if arg in manifest_args:
        result = eval(manifest_args.get(arg))
        if season is not None:
            assert isinstance(result, dict), "MANIFEST argument is not a dict"
            if season in result.keys():
                return result.get(season)
            else:
                return None
        else:
            return result
    else:
        return None

def set_arg(arg, value, season=None):
    """ Function for writing IDs to  manifest """
    if manifest_exists():
        manifest_args = read_manifest()
    else:
        manifest_args = dict()
    if arg in manifest_args:
        result = manifest_args.get(arg) 
        if season is None:
            manifest_args[arg] = value
        else:
            assert isinstance(result, dict)
            manifest_args[arg][season] = value
    else:
        if season is None:
            manifest_args[arg] = value
        else:
            manifest_args[arg] = dict()
            manifest_args[arg][season] = value

    write_manifest(manifest_args)

