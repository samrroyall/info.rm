import os
import pathlib
import sqlite3
from __future__ import annotations
from orm import Leagues, Teams, Players
from typing import List, Tuple, Optional

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
        self.check_properties(field, operator, value)
        self.field = field
        self.operator = operator
        self.value = value

    def check_properties(self, field, operator, value) -> None:
        table_strings = ["Leagues", "Teams", "Players"]
        field_table = field.split(".")[0]
        field_name = field.split(".")[1]
        assert field_table in table_strings, \
            "ERROR: Field table is incorrect."
        expected_value_type = eval(field_table).get_type(field_name)
        if expected_value_type == str:
            assert value.isalpha(), "ERROR: Field value is incorrect."
        elif expected_value_type == int:
            assert value.isdecimal(), "ERROR: Field value is incorrect."
        elif expected_value_type == float:
            assert len(value.split(".")) == 2, "ERROR: Field value is incorrect."
            for half in value.split("."):
                assert half.isdecimal(), "ERROR: Field value is incorrect."
        elif expected_value_type == bool:
            assert value == "true" or value == "false", \
                "ERROR: Field value is incorrect."

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

    def __init__(self, order_fields: List[str]) -> None:
        self.order_fields = order_fields

    def to_str(self) -> str:
        return ", ".join(self.order_fields)

class Select:

    def __init__(self, select_fields: List[str]) -> None:
        self.select_fields = select_fields

    def to_str(self) -> str:
        return ", ".join(self.select_fields)


class Statement:

    def __init__(
        self, 
        table_name: str, 
        select_fields: List[str], 
        order_fields: Optional[List[str]], 
        filter_fields: Optional[List[Tuple[List[Tuple[str,str,str]], str]]]
    ) -> None:
        self.table_name = table_name
        self.select_fields = Select(select_fields)
        if order_fields:
            self.order_fields = Order(order_fields)
        if filter_fields:
            self.filter_fields = [ FilterList(field) for field in filter_fields ]

    def to_str(self) -> str:
        query_string = f"SELECT {self.select_fields.to_str()} FROM {self.table_name}"
        if hasattr(self, "filter_fields"):
            filter_string = " AND ".join([ f"({filter.to_str()})" for filter in self.filter_fields ])
            query_string += f" WHERE {filter_string}"
        if hasattr(self, "order_fields"):
            query_string += f" ORDER BY {self.order_fields.to_str()}"
        return f"{query_string};"


class Query:

    def __init__(self, db_path: str, statement: Statement) -> None:
        if os.path.isfile(db_path) and os.path.splitext(db_path) == ".db":
            self.db_path = db_path
        else:
            print("ERROR: Query class requires db_path to be a path to an existing sqlite DB.")
        if isinstance(statement, Statement):
            self.statement = statement
        else:
            print("ERROR: Query class requires statement to be an instance of the Statement class.")

    def query_db(self) -> None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()


