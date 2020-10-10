#!/usr/bin/env python3

from search import insert, search
from query_utils import get_players

PLAYER_DICT = None

def get_prefixes(name):
    split_name = name.split(" ")
    prefix_list = []
    for idx in range(len(split_name)):
        chunk = split_name[idx:]
        prefix_list.append(" ".join(chunk))
    return prefix_list

def generate_tree():
    global PLAYER_DICT
    PLAYER_DICT = get_players()
    for name in PLAYER_DICT.keys():
        prefixes = get_prefixes(name)
        for prefix in prefixes:
            insert(prefix, name)

def search_tree(search_key):
    result = []
    split_key = search_key.split(" ")
    for idx in range(len(split_key)):
        key = split_key[idx]
        if len(key) == 0:
            break
        search_result = search(key)
        if idx == 0:
            result += search_result
        else:
            result = set(result) & set(search_result)
    result_with_ids = []
    for name in result:
        id_list = PLAYER_DICT.get(name)
        for id in id_list: 
            result_with_ids.append( (id, name) )
    return sorted(result_with_ids, key=lambda elem: elem[1])

