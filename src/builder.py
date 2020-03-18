import os
import pathlib

from .query import Query, Statement, get_max, grab_columns

file_path = pathlib.Path(__file__).parent.absolute()
DB_PATH = os.path.join(str(file_path), "../db/info.rm.db")
default_select_fields = ["teams.logo", "players.name", "teams.name"]
join_params = {
        "players": "team_id",
        "teams": "id",
    }
floats = [
        "players.rating",
        "players.shots_on_pct",
        "players.passes_accuracy",
        "players.duels_won_pct",
        "players.dribbles_succeeded_pct",
        "players.penalties_scored_pct"
    ]

def dashboard_stmt(select_fields, filter_fields, order_fields):
    select_fields = default_select_fields + select_fields
    table_names = []
    for sel_field in select_fields:
        for field in grab_columns(sel_field):
            table_names.append((
                    field.split(".")[0],
                    join_params.get(field.split(".")[0])
                ))
    table_names = list(set(table_names))
    stmt = Statement(
        table_names = table_names,
        select_fields = select_fields,
        filter_fields = filter_fields,
        order_fields = order_fields
    )
    return stmt

def rank_result(query_result, fields, order_by_field, desc=True):
    count = 0
    rank = 0
    prev_result = float("inf") if desc == True else -1.0 * float("inf")
    fields = default_select_fields + fields
    ranked_result = { "header": fields, "data": []}
    for idx in range(len(query_result)):
        tup = query_result[idx]

        # handle defaults
        split_name = tup[1].split(" ")
        if len(split_name) == 2 and len(split_name[0]) > 2:
            name = split_name[0][0] + ". " + split_name[1]
        else:
            name = tup[1]
        team_logo = tup[0]
        team_name = tup[2]

        # handle stats
        stats = []
        for stat_idx in range(3,len(fields)):
            stat = tup[stat_idx]
            if fields[stat_idx] in floats:
                value = round(float(tup[stat_idx]), 2)
            else:
                value = round(float(tup[stat_idx]))
            stats.append(value)

        assert order_by_field in fields,\
            "ERROR: invalid order_by_field supplied"
        order_by_idx = fields.index(order_by_field)
        order_by_stat = float(tup[order_by_idx])
        # rank
        count += 1
        if desc == True and round(order_by_stat, 3) < prev_result:
            rank = count
        elif desc == False and round(order_by_stat, 3) > prev_result:
            rank = count
        prev_result = round(order_by_stat, 3)

        # return
        ranked_tup = {
            "rank": rank,
            "name": name,
            "team_name": team_name,
            "team_logo": team_logo,
            "stats":  stats
        }
        ranked_result["data"].append(ranked_tup)
    return ranked_result

def default_stats():
    select_fields = [
        "players.rating",
        "players.goals",
        "players.assists",
        "players.tackles"
    ]
    max_minutes_played = get_max(DB_PATH, "players.minutes_played")
    filter_fields = [
        ([("players.minutes_played",">",str(max_minutes_played/3))],"")
    ]
    order_fields = (["players.rating"], True)
    query_result = Query(DB_PATH, dashboard_stmt(select_fields, filter_fields, order_fields)).query_db()
    ranked_result = rank_result(query_result, select_fields, "players.rating")
    return ranked_result


