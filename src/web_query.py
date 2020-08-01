from query import Query, Statement, grab_columns
from query_utils import get_pct_stats, get_float_stats

default_select_fields = ["teams.logo", "players.name", "players.id", "teams.name", "leagues.name"]
floats = get_float_stats()
pcts = get_pct_stats()


def stmt(select_fields, filter_fields, order_field):
    select_fields = default_select_fields + select_fields
    # compile select fields and filter fields
    fields = []
    if filter_fields is not None:
        for filter_field in filter_fields[0][0]:
            filter_column = filter_field[0]
            fields.append(filter_column)
    fields += select_fields
    # grab table names (besides stats) from fields
    temp_table_names = []
    for sel_field in fields:
        columns = grab_columns(sel_field)
        for column in columns:
            table = column.split(".")[0]
            if table != "stats":
                temp_table_names.append(table)
    # dedup table names
    temp_table_names = list(set(temp_table_names))
    # create table_names list 
    table_names = ("stats", temp_table_names)
    stmt = Statement(
                table_names = table_names,
                select_fields = select_fields, 
                filter_fields = filter_fields, 
                order_field = order_field
           )
    return stmt

# only needed if division is being done
def field_logical(field):
    lops = ["/"]
    for lop in lops:
        if lop in field:
            return True
    return False

def result_dict(query_result, fields):
    result = dict()
    for index in range(len(fields)):
        result[fields[index]] = query_result[index]
    return result 

def format_result(query_result, fields):
    id_dict = dict()
    for idx in range(len(query_result)):
        query_result[idx] = result_dict(query_result[idx], fields) 
        # NEED TO AGGREGATE STATS AND MAKE SURE THIS WORKS PER 90
        # AAAND HOPEFULLY GET CURRENT TEAM FOR TEAM NAME/LOGO 
    return query_result

def rank_response(select_fields, filter_fields, order_field):
    fields = default_select_fields + select_fields
    query_result_raw = Query(stmt(select_fields, filter_fields, order_field)).query_db()
    query_result = format_result(query_result_raw, fields)
    order_by_field = order_field[0][0]
    desc = order_field[1]

    count = 0
    rank = 0
    prev_result = float("inf") if desc is True else -1.0 * float("inf")
    ranked_result = { "header": fields, "data": []}
    for idx in range(len(query_result)):
        player = query_result[idx]

        # fix player name
        split_name = player.get("players.name").split(" ")
        if len(split_name) == 2 and len(split_name[0]) > 2:
            name = split_name[0][0] + ". " + split_name[1]
        else:
            name = player.get("players.name")

        # handle stats
        stats = []
        for field in select_fields:
            stat = player.get(field)

            # values of 0 are only n/a if stats are presented descending
            if stat is None:
               value = "n/a" 
            elif float(stat) == 0.0:
                value = "n/a"
            elif field in floats or field_logical(field):
                value = str(round(float(stat), 2)).ljust(4,"0")
            else:
                value = round(float(stat))

            # add % at the end if needed
            if field in pcts and value != "n/a":
                value = f"{value}%"

            stats.append(value)

        # can only order by selected fields
        assert order_by_field in fields,\
            f"ERROR: invalid order_by_field supplied {order_by_field}"
        order_by_value = player.get(order_by_field) 
        if order_by_value is None:
            order_by_stat = "n/a"
        else:
            order_by_stat = float(order_by_value)
            if order_by_stat == 0.0:
                order_by_stat = "n/a"

        # rank
        if order_by_stat != "n/a":
            count += 1
            if desc is True and round(order_by_stat, 3) < prev_result:
                rank = count
            elif desc is False and round(order_by_stat, 3) > prev_result:
                rank = count
            prev_result = round(order_by_stat, 3)
        else:
            rank = "N/A."

        # return
        ranked_tup = {
            "rank": (str(rank) + ".").ljust(3," ") if rank != "N/A." else rank,
            "name": name,
            "id": player.get("players.id"),
            "league_name": player.get("leagues.name"),
            "team_name": player.get("teams.name"),
            "team_logo": player.get("teams.logo"),
            "stats": stats
        }
        ranked_result["data"].append(ranked_tup)
    return ranked_result


