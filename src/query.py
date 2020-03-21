import os
import pathlib
import sqlite3
from typing import List, Tuple, Optional, Dict

from .orm import Leagues, Teams, Players
from .config import get_config_arg

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
        db_tables = ["players","teams","leagues"]
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
        db_tables = ["players","teams","leagues"]
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

    def __init__(self, db_path: str, statement: Statement) -> None:
        assert os.path.isfile(db_path) and os.path.splitext(db_path)[1] == ".db",\
            "ERROR: invalid DB path supplied to Query."
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

def check_col(col):
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

def get_max(db_path: str, stat: str) -> float:
    assert os.path.isfile(db_path) and os.path.splitext(db_path)[1] == ".db",\
        "ERROR: invalid DB path supplied to Query."
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(f"SELECT max({stat}) FROM players;")
    query_result = cursor.fetchall()[0][0]
    connection.commit()
    connection.close()
    return query_result

def get_by(
        db_path: str, 
        col1: str, 
        table1: str, 
        where_param: str, 
        col2: str, 
        table2: str
    ) -> Dict[str, List[str]]:
    assert os.path.isfile(db_path) and os.path.splitext(db_path)[1] == ".db",\
        "ERROR: invalid DB path supplied to Query."
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    result = dict() 
    cursor.execute(f"SELECT DISTINCT {col2} FROM {table2};")
    values = [tup[0] for tup in cursor.fetchall()]
    connection.commit()
    for value in values:
        query_string = f"SELECT DISTINCT {col1} FROM {table1} WHERE {where_param}=\"{value}\";"
        cursor.execute(query_string)
        result[value] = [tup[0] for tup in cursor.fetchall()]
        connection.commit()
    connection.close()
    return result

def get_column(db_path: str, col: str, table: str) -> List[str]:
    assert os.path.isfile(db_path) and os.path.splitext(db_path)[1] == ".db",\
        "ERROR: invalid DB path supplied to Query."
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(f"SELECT DISTINCT {col} FROM {table};")
    query_result = [tup[0] for tup in cursor.fetchall()]
    connection.commit()
    connection.close()
    return query_result

