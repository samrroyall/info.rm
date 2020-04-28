import os
import pathlib
import sqlite3
#import unicodedata
import unidecode
from typing import List, Tuple, Optional, Dict, Any

from .config import get_config_arg
from .orm import Leagues, Teams, Players, Stats

file_path = pathlib.Path(__file__).parent.absolute()
db_path = os.path.join(str(file_path), f"../db/info.rm.db")

# make this automated
FLOAT_STATS = [
    "stats.rating",
]
PCT_STATS = [
    "stats.shots_on_pct",
    "stats.passes_accuracy",
    "stats.duels_won_pct",
    "stats.dribbles_succeeded_pct",
    "stats.penalties_scored_pct",
]
TOP_5 = ["Bundesliga 1", "Ligue 1", "Premier League", "Primera Division", "Serie A"]

###########################
###### Query Classes ######
###########################

class Filter:
    _OPS = ["=", "<", "<=", ">", ">=", "IN"]

    def __init__(self, properties: Tuple[str, str, str]) -> None:
        cls = self.__class__
        field, operator, value = properties
        assert operator in cls._OPS, \
            f"ERROR: Filter accepts following operations: {str(cls._OPS)[1:-1]}."
        self.field, self.operator, self.value = self.check_tables_values(field, operator, value)

    def check_value(self, value, orm_schema, column_name):
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
        return value

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
        if operator == "IN":
            new_value = "("
            for val in value:
                new_value += self.check_value(val, orm_schema, column_name)
                new_value += ","
            value = new_value[:-1] + ")"
        else:
            value = self.check_value(value, orm_schema, column_name)
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
            table_names: Tuple[str, List[str]], 
        ) -> None:
        self.select_fields = select_fields
        assert len(table_names) > 0,\
            "ERROR: Statement class requires at least one table."
        assert len(table_names) < 4,\
            "ERROR: Statement class cannot take more than four tables."
        self.check_tables(table_names)

    def check_tables(self, table_names: Tuple[str, List[str]]) -> None:
        db_tables = ["stats", "players", "teams", "leagues"]
        # handle tables
        # for now, all queries go through stats
        table_one = table_names[0]
        assert table_one == "stats", \
            f"ERROR: Expected stats as primary table. Got: {table_one}."
        join_tables = table_names[1]
        for table in join_tables:
            assert table != "stats", \
                f"ERROR: Received stats as a join table."
            assert table in db_tables, \
                "ERROR: Invalid table name supplied."
        self.primary_table = table_one
        self.join_tables = join_tables

    def to_str(self) -> str:
        select_list = ", ".join(self.select_fields)
        query_string = f"SELECT {select_list} FROM {self.primary_table}"
        for table in self.join_tables:
            query_string += f" JOIN {table} ON {self.primary_table}.{table[:-1]}_id = {table}.id"
        return query_string


class Statement:

    def __init__(
        self,
        table_names: Tuple[str, List[str]],
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
        query_string = self.statement.to_str()
        cursor.execute(query_string)
        query_result = cursor.fetchall()
        connection.commit()
        connection.close()
        return query_result

#######################
#### Query Helpers ####
#######################

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

#################################
#### Public Function Helpers ####
#################################

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

static_keys = [
        "id", 
        "player_id",
        "name", 
        "firstname", 
        "lastname", 
        "season", 
        "league_id", 
        "league_name", 
        "team_id", 
        "team_name", 
        "position", 
        "rating"
    ]

pct_keys = [
        "shots_on_pct", 
        "passes_accuracy", 
        "duels_won_pct", 
        "dribbles_succeeded_pct",
        "penalties_scored_pct"
    ]
        

# format query result into a dict
def result_to_dict(
        query_result: List[str], 
        index_dict: Dict[int, str]
    ) -> Dict[str,str]:
    result = dict()
    for index, colname in index_dict.items():
        result[colname] = query_result[index]
    return result

def stats_to_per90( 
        formatted_result: List[str]
    ) -> Dict[str,Any]:
    minutes_played = float(formatted_result.get("minutes_played"))
    for key, value in formatted_result.items():
        if (key not in static_keys and
            key not in pct_keys and
            key != "minutes_played"):
            formatted_result[key] = float(value) / (minutes_played / 90.0)
    return formatted_result

##########################
#### Public Functions ####
##########################

# used for default queries 
def get_max(
        stat: str,
        season: str
    ) -> float:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(f"SELECT max({stat}) FROM stats WHERE season = {season};")
    query_result = list(cursor.fetchall()[0])[0]
    connection.commit()
    connection.close()
    return query_result

# used for player pages
def get_player_data(
        id: str,
        per_90: bool
    ) -> Dict[str, Any]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    result = dict() 

    # player info 
    cursor.execute(f"SELECT * FROM players WHERE id = {id};")
    player_result = list(cursor.fetchall()[0])
    connection.commit()
    if len(player_result) == 0:
        return None
    result["player"] = result_to_dict(player_result, players_keys)


    result["stats"] = dict()

    cursor.execute(f"SELECT * FROM stats WHERE player_id = {id};")
    stats_result = [list(stat) for stat in cursor.fetchall()]
    connection.commit()

    current_season = None
    current_index = None
    for i in range(len(stats_result)):
        stats_row = list(stats_result[i])
        formatted_row = result_to_dict(stats_row, stats_keys)
        # divide relevant stats by minutes played / 90
        if per_90 is True:
            formatted_row = stats_to_per90(formatted_row)

        # get season and set up result dictionary structure
        season = formatted_row.get("season")
        if season != current_season:
            current_season = season
            current_index = 0
            result["stats"][current_season] = dict()
        else:
            current_index += 1

        result["stats"][current_season][current_index] = dict()

        # get team logo
        team_id = formatted_row.get("team_id")
        cursor.execute(f"SELECT logo FROM teams WHERE id = {team_id};")
        team_logo = cursor.fetchall()[0][0]
        connection.commit()

        # get league flag
        league_id = formatted_row.get("league_id")
        cursor.execute(f"SELECT flag FROM leagues WHERE id = {league_id};")
        league_flag = cursor.fetchall()[0][0]
        connection.commit()

        result["stats"][current_season][current_index]["stats"] = formatted_row
        result["stats"][current_season][current_index]["team"] = {"logo": team_logo}
        result["stats"][current_season][current_index]["league"] = {"flag": league_flag}


    connection.close()
    return result

# used for builder form select fields
def get_select_data() -> Dict[str, Any]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    result = dict()

    # leagues stay static
    cursor.execute("SELECT DISTINCT name FROM leagues;")
    leagues_result = [tup[0] for tup in cursor.fetchall()]
    connection.commit()
    leagues_result.sort()
    result["leagues"] = leagues_result
    
    seasons = get_seasons()

    # clubs
    result["clubs"] = dict()
    for season in seasons:
        result["clubs"][season] = dict()
        for league in result.get("leagues"):
            # leagues stay static
            cursor.execute(f"SELECT DISTINCT team_name FROM stats WHERE season = {season} AND league_name = \"{league}\";")
            clubs_result = [tup[0] for tup in cursor.fetchall()]
            connection.commit()
            clubs_result.sort()
            result["clubs"][season][league] = clubs_result

    # get all nations
    cursor.execute("SELECT DISTINCT nationality FROM players;")
    nations_result = [tup[0] for tup in cursor.fetchall()]
    connection.commit()
    nations_result.sort()
    result["nations"] = nations_result

    return result

def get_leagues() -> List[str]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get leagues
    cursor.execute("SELECT DISTINCT name FROM leagues;")
    leagues_result = [tup[0] for tup in cursor.fetchall()]
    connection.commit()
    return leagues_result 

def get_positions() -> List[str]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get positions
    cursor.execute("SELECT DISTINCT position FROM stats;")
    position_result = [tup[0] for tup in cursor.fetchall()]
    connection.commit()
    return position_result

def get_seasons() -> List[str]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get seasons
    cursor.execute("SELECT DISTINCT season FROM stats;")
    season_result = [str(tup[0]) for tup in cursor.fetchall()]
    connection.commit()
    return season_result 

def get_current_season() -> str:
    seasons = get_seasons()
    int_seasons = [int(season) for season in seasons]
    return str(max(int_seasons))

def get_players() -> Dict[str, int]:
    # open DB connection
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # get players names and IDs
    cursor.execute("SELECT players.firstname, players.lastname, players.id FROM players ORDER BY players.firstname;")
    player_result = cursor.fetchall()
    connection.commit()

    player_dict = dict()
    for tup in player_result:
        name = f"{tup[0]} {tup[1]}"
        decoded_name = unidecode.unidecode(name.lower())
        id = tup[2]

        if decoded_name in player_dict:
            player_dict[decoded_name].append( id )
        else:
            player_dict[decoded_name] = [ id ]

    return player_dict

#################################
### Global Variable Functions ###
#################################

def get_top_five() -> List[str]:
    return TOP_5

def get_pct_stats() -> List[str]:
    return PCT_STATS

def get_float_stats() -> List[str]:
    return FLOAT_STATS

