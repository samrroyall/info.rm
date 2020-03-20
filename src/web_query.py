from .query import Statement, grab_columns

default_select_fields = ["teams.logo", "players.name", "teams.name"]
join_params = {
        "players": "team_id",
        "teams": "id",
    }
floats = [
        "players.rating",
    ]

def stmt(select_fields, filter_fields, order_field):
    select_fields = default_select_fields + select_fields
    table_names = []
    fields = []
    if len(filter_fields) > 0:
        filter_columns = filter_fields[0][0]
        fields += filter_columns
    fields += select_fields
    for sel_field in fields:
        for field in grab_columns(sel_field):
            table_names.append((
                    field.split(".")[0],
                    join_params.get(field.split(".")[0])
                ))
    table_names = list(set(table_names))
    if len(filter_fields) == 0:
        stmt = Statement(
            table_names = table_names,
            select_fields = select_fields,
            order_field = order_field
        )
    else:
        stmt = Statement(
            table_names = table_names,
            select_fields = select_fields,
            filter_fields = filter_fields,
            order_field = order_field
        )
    return stmt

def field_logical(field):
    lops = ["/","*","+","-"]
    for lop in lops:
        if lop in field:
            return True
    return False

def rank(query_result, fields, order_by_field, desc=True):
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
            if fields[stat_idx] in floats or field_logical(fields[stat_idx]):
                value = round(float(tup[stat_idx]), 2)
            else:
                value = round(float(tup[stat_idx]))
            stats.append(value)

        assert order_by_field in fields,\
            f"ERROR: invalid order_by_field supplied {order_by_field}"
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


