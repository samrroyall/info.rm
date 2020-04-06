import os
import pathlib
import sqlite3
from typing import List, Tuple, Optional, Dict

from .config import get_config_arg
from .orm import Leagues, Teams, Players

file_path = pathlib.Path(__file__).parent.absolute()
db_path = os.path.join(str(file_path), f"../db/info.rm.db")

###########################
###### Query Classes ######
###########################

class Filter:
    _OPS = ["=", "<", "<=", ">", ">="]

    def __init__(self, properties: Tuple[str, str, str]) -> None:
        cls = self.__class__
        field, operator, value = properties
        assert operator in cls._OPS, \
            f"ERROR: Filter accepts following operations: {str(cls._OPS)[1:-1]}."
        self.field, self.operator, self.value = self.check_tables_values(field, operator, value)

    def check_tables_values(self, field, operator, value):
        db_tables = ["stats", "players","teams","leagues"]
        column = grab_columns(field)[0]
        split_column = column.split(".")
        table_name = split_column[0]
        column_name = split_column[1]
        # check table
        assert table_name in db_tables, "ERROR: Invalid table name supplied."
        # check field
        orm_class = eval(table_name.capitalize())
        orm_schema = orm_class._TYPES
        assert column_name in orm_schema.keys(),\
            "ERROR: Invalid column name supplied."
        # check value
        expected_value = str(orm_schema.get(column_name)).split("'")[1]
        if expected_value == "str":
            expected_chars = [" ","."]
            for char in value:
                if (char not in expected_chars and
                    (not char.isalpha() and not char.isdecimal)):
                    assert False, f"ERROR: Invalid string value supplied. {value}"
            value = f"\"{value}\""
        elif expected_value == "int":
            if "." in value:
                split_value = value.split(".")
                assert int(split_value[1]) == 0,\
                    "ERROR: Invalid int value supplied."
                value = split_value[0]
            assert value.isdecimal(), "ERROR: Invalid int value supplied."
        elif expected_value == "float":
            if value[0] == ".":
                value = "0" + value
            elif value.isdecimal():
                value = value + ".0"
            split_value = value.split(".")
            assert split_value[0].isdecimal() and split_value[1].isdecimal(),\
                "ERROR: Invalid float value supplied."
        return field, operator, value


    def to_str(self) -> str:
        return f"{self.field} {self.operator} {self.value}"


class FilterList:
    _LOPS = ["AND", "OR"]

    def __init__(
        self,
        properties: Tuple[List[Tuple[str,str,str]], str],
    ) -> None:
        cls = self.__class__
        filters, logical_operator = properties
        assert len(filters) == 1 or logical_operator in cls._LOPS, \
            f"ERROR: FilterList accepts following operators: {str(cls._LOPS)[1:-1]}"
        self.logical_operator = logical_operator
        self.filters = [ Filter(filter_tuple) for filter_tuple in filters ]

    def to_str(self) -> str:
        filter_strings = [ filter.to_str() for filter in self.filters ]
        return f" {self.logical_operator} ".join(filter_strings)


class Order:

    def __init__(
            self,
            order_field: Tuple[List[str], bool]
        ) -> None:
        self.order_field, self.desc = order_field

    def to_str(self) -> str:
        order_list = ", ".join(self.order_field)
        query_string = f" ORDER BY {order_list}"
        if self.desc:
            query_string += " DESC"
        query_string += " LIMIT 50"
        return query_string

class Select:

    def __init__(
            self,
            select_fields: List[str],
            table_names: List[Tuple[str,str]], # table name and join parameter
        ) -> None:
        self.select_fields = select_fields
        assert len(table_names) > 0,\
            "ERROR: Statement class requires at least one table."
        assert len(table_names) < 3,\
            "ERROR: Statement class cannot take more than two tables."
        self.check_tables(table_names)

    def check_tables(self, table_names: List[Tuple[str,str]]) -> None:
        db_tables = ["stats", "players", "teams","leagues"]
        # handle tables
        if len(table_names) == 1:
            self.table_names = [table_names[0][0]]
        elif len(table_names) == 2:
            assert table_names[0][0] != table_names[1][0], \
                "ERROR: Cannot perform join on the same table."
            self.table_names = [table_names[0][0], table_names[1][0]]
            self.join_params = [table_names[0][1], table_names[1][1]]
        for table in table_names:
            assert table[0] in db_tables, "ERROR: Invalid table name supplied."

    def to_str(self) -> str:
        select_list = ", ".join(self.select_fields)
        if len(self.table_names) == 1:
            query_string = f"SELECT {select_list} FROM {self.table_names[0]}"
        else:
            query_string = f"SELECT {select_list} FROM {self.table_names[0]} JOIN {self.table_names[1]}"
            join_param_one = f"{self.table_names[0]}.{self.join_params[0]}"
            join_param_two = f"{self.table_names[1]}.{self.join_params[1]}"
            query_string += f" ON {join_param_one} = {join_param_two}"
        return query_string


class Statement:

    def __init__(
        self,
        table_names: List[Tuple[str,str]],
        select_fields: List[str],
        order_field: Tuple[List[str], bool],
        filter_fields: Optional[List[Tuple[List[Tuple[str,str,str]], str]]] = None
    ) -> None:
        self.select_stmt = Select(select_fields, table_names)
        if order_field:
            self.order_field = Order(order_field)
        if filter_fields is not None:
            self.filter_fields = [ FilterList(field) for field in filter_fields ]

    def to_str(self) -> str:
        query_string = self.select_stmt.to_str()
        if hasattr(self, "filter_fields"):
            filter_string = " AND ".join([ f"({filter.to_str()})" for filter in self.filter_fields ])
            query_string += f" WHERE {filter_string}"
        if hasattr(self, "order_field"):
            query_string += f" {self.order_field.to_str()}"
        return f"{query_string};"



class Query:

    def __init__(
        self,
        statement: Statement,
    ) -> None:
        self.db_path = db_path 
        assert isinstance(statement, Statement),\
            "ERROR: Query class not supplied with Statement object."
        self.statement = statement

    def query_db(self) -> None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute(self.statement.to_str())
        query_result = cursor.fetchall()
        connection.commit()
        connection.close()
        return query_result

##########################
#### Public Functions ####
##########################

def check_col(col: str) -> bool:
    if "." not in col:
        return False
    else:
        table = col.split(".")[0]
        col = col.split(".")[1]
        if table.isdecimal() and col.isdecimal():
            return False
    return True

def grab_columns(string: str) -> List[str]:
    chars = ['/','*','+','-','(',')',' ']
    result = []
    temp_col = ""
    for char in string:
        if char not in chars:
            temp_col += char
        else:
            if temp_col != "":
                if check_col(temp_col):
                    result.append(temp_col)
                temp_col = ""
    if temp_col != "":
        if check_col(temp_col):
            result.append(temp_col)
    return result

################################
#### Public Query Functions ####
################################

stats_keys = {
        0: "id", 
        1: "player_id",
        2: "name", 
        3: "firstname", 
        4: "lastname", 
        5: "season", 
        6: "league_id", 
        7: "league_name", 
        8: "team_id", 
        9: "team_name", 
        10: "position", 
        11: "rating", 
        12: "shots", 
        13: "shots_on", 
        14: "shots_on_pct",
        15: "goals",
        16: "goals_conceded",
        17: "assists",
        18: "passes",
        19: "passes_key",
        20: "passes_accuracy",
        21: "tackles",
        22: "blocks",
        23: "interceptions",
        24: "duels",
        25: "duels_won",
        26: "duels_won_pct",
        27: "dribbles_past",
        28: "dribbles_attempted",
        29: "dribbles_succeeded",
        30: "dribbles_succeeded_pct",
        31: "fouls_drawn",
        32: "fouls_committed",
        33: "cards_yellow",
        34: "cards_red",
        35: "penalties_won",
        36: "penalties_committed",
        37: "penalties_scored",
        38: "penalties_missed",
        39: "penalties_scored_pct",
        40: "penalties_saved",
        41: "games_appearances",
        42: "minutes_played",
        43: "games_started",
        44: "substitutions_in",
        45: "substitutions_out",
        46: "games_bench"
    }

players_keys = {
        0: "id",
        1: "name",
        2: "firstname",
        3: "lastname",
        4: "age",
        5: "birth_date",
        6: "nationality",
        7: "flag",
        8: "height",
        9: "weight"
    }

teams_keys = {
        0: "id",
        1: "name",
        2: "league_id",
        3: "league_name",
        4: "logo"
    }

leagues_keys = {
        0: "id",
        1: "name",
        2: "type",
        3: "country",
        4: "logo",
        5: "flag"
    }

def get_max(
        stat: str,
        season: str = CURRENT_SEASON
    ) -> float:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(f"SELECT max({stat}) FROM stats WHERE season = {season};")
    query_result = cursor.fetchall()[0][0]
    connection.commit()
    connection.close()
    return query_result

def get_player_data(
        id: str,
        season: str = CURRENT_SEASON
    ) -> List[str]:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM players WHERE id = {id};")
    player_result = cursor.fetchall()
    player_result = list(player_result[0])
    connection.commit()

    cursor.execute(f"SELECT * FROM stats WHERE player_id = {id};")
    stats_result = list(cursor.fetchall())

    data = dict() 
    for stat_result in stats_result:
        season = 
        team = 
        

    connection.commit()

    team_id = player_result[3]
    cursor.execute(f"SELECT * FROM teams WHERE id = {team_id};")
    team_result = list(cursor.fetchall()[0])
    connection.commit()

    league_id = player_result[1]
    cursor.execute(f"SELECT * FROM leagues WHERE id = {league_id};")
    league_result = list(cursor.fetchall()[0])
    connection.commit()


    connection.close()
    return player_result, team_result, league_result
