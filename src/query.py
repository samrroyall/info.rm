import os
import pathlib
import sqlite3
from typing import List, Tuple, Optional

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
        assert len(field.split(".")) == 2, \
            "ERROR: Field table not specified."
        self.field, self.operator, self.value = self.check_properties(field, operator, value)

    def check_properties(self, field, operator, value) -> None:
        table_strings = ["leagues", "teams", "players"]
        leagues = [league.split(",")[0] for league in eval(get_config_arg("leagues"))]
        field_table = field.split(".")[0]
        field_name = field.split(".")[1]
        assert field_table in table_strings, \
            "ERROR: Field table is incorrect."
        expected_value_type = eval(field_table.capitalize())().get_type(field_name)
        if expected_value_type == str:
            if field_name == "league_name":
                assert value in leagues, "ERROR: Invalid league name sent."
            else:
                assert value.isalpha(), "ERROR: Field value is incorrect."
            value = f"\'{value}\'"
        elif expected_value_type == int:
            assert value.isdecimal(), "ERROR: Field value is incorrect."
        elif expected_value_type == float:
            assert len(value.split(".")) == 2, "ERROR: Field value is incorrect."
            for half in value.split("."):
                assert half.isdecimal(), "ERROR: Field value is incorrect."
        elif expected_value_type == bool:
            assert value == "true" or value == "false", \
                "ERROR: Field value is incorrect."
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
        assert logical_operator in cls._LOPS, \
            f"ERROR: FilterList accepts following operators: {str(cls._LOPS)[1:-1]}"
        self.logical_operator = logical_operator
        self.filters = [ Filter(filter_tuple) for filter_tuple in filters ]

    def to_str(self) -> str:
        filter_strings = [ filter.to_str() for filter in self.filters ]
        return f" {self.logical_operator} ".join(filter_strings)
                                   

class Order:

    def __init__(
            self, 
            order_fields: Tuple[List[str], bool]
        ) -> None:
        self.order_fields, self.desc = order_fields

    def to_str(self) -> str:
        order_list = ", ".join(self.order_fields)
        query_string = f" ORDER BY {order_list}"
        if self.desc:
            query_string += " DESC"
        query_string += " LIMIT 50"
        return query_string

class Select:

    def __init__(
            self, 
            select_fields: List[str],
            table_names: List[Tuple[str,str]],
        ) -> None:
        self.select_fields = select_fields
        assert len(table_names) > 0,\
            "ERROR: Statement class requires at least one table."
        assert len(table_names) < 3,\
            "ERROR: Statement class cannot take more than two tables."
        if len(table_names) == 1:
            self.table_names = [table_names[0][0]]
        elif len(table_names) == 2:
            assert table_names[0][0] != table_names[1][0], \
                "ERROR: Cannot perform join on the same table."
            self.table_names = [table_names[0][0], table_names[1][0]]
            self.join_params = [table_names[0][1], table_names[1][1]]

    def check_tables(self) -> None:
        db_tables = ["leagues", "teams", "players"]
        tables = self.table_names
        for table in tables:
            assert table in db_tables, "ERROR: Invalid table name supplied."
        value_tables = list(set([column.split(".")[0] for column in self.select_fields]))
        for table in value_tables:
            assert table in tables, "ERROR: Invalid select param table name supplied"

    def to_str(self) -> str:
        select_list = ", ".join(self.select_fields)
        self.check_tables()
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
        order_fields: Optional[List[str]], 
        filter_fields: Optional[List[Tuple[List[Tuple[str,str,str]], str]]]
    ) -> None:
        self.select_stmt = Select(select_fields, table_names)
        if order_fields:
            self.order_fields = Order(order_fields)
        if filter_fields:
            self.filter_fields = [ FilterList(field) for field in filter_fields ]

    def to_str(self) -> str:
        query_string = self.select_stmt.to_str()
        if hasattr(self, "filter_fields"):
            filter_string = " AND ".join([ f"({filter.to_str()})" for filter in self.filter_fields ])
            query_string += f" WHERE {filter_string}"
        if hasattr(self, "order_fields"):
            query_string += f" {self.order_fields.to_str()}"
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

