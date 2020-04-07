from .query import Query, Statement, grab_columns, get_pct_stats, get_float_stats

default_select_fields = ["teams.logo", "players.name", "players.id", "teams.name"]
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
    temp_table_names = list(set(table_names))

    # create table_names list 
    table_names = ["stats", temp_table_names]

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

def rank_response(select_fields, filter_fields, order_field):
    query_result = Query(stmt(select_fields, filter_fields, order_field)).query_db()
    order_by_field = order_field[0][0]
    desc = order_field[1]
    fields = default_select_fields + select_fields

    count = 0
    rank = 0
    prev_result = float("inf") if desc is True else -1.0 * float("inf")
    ranked_result = { "header": fields, "data": []}
    for idx in range(len(query_result)):
        tup = query_result[idx]

        # handle defaults
        team_logo = tup[0]
        # fix player name
        split_name = tup[1].split(" ")
        if len(split_name) == 2 and len(split_name[0]) > 2:
            name = split_name[0][0] + ". " + split_name[1]
        else:
            name = tup[1]
        id = tup[2]
        team_name = tup[3]

        # handle stats
        stats = []
        for stat_idx in range(len(default_select_fields),len(fields)):
            stat = tup[stat_idx]

            # values of 0 are only n/a if stats are presented descending
            if stat is None:
               value = "n/a" 
            elif float(stat) == 0.0:
                value = "n/a"
            elif fields[stat_idx] in floats or field_logical(fields[stat_idx]):
                value = str(round(float(tup[stat_idx]), 2)).ljust(4,"0")
            else:
                value = round(float(tup[stat_idx]))

            # add % at the end if needed
            if fields[stat_idx] in pcts and value != "n/a":
                value = f"{value}%"

            stats.append(value)

        # can only order by selected fields
        assert order_by_field in fields,\
            f"ERROR: invalid order_by_field supplied {order_by_field}"
        order_by_idx = fields.index(order_by_field)
        if tup[order_by_idx] is None:
            order_by_stat = "n/a"
        else:
            order_by_stat = float(tup[order_by_idx])
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
            "id": id,
            "team_name": team_name,
            "team_logo": team_logo,
            "stats": stats
        }
        ranked_result["data"].append(ranked_tup)
    return ranked_result


