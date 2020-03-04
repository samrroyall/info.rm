#!/usr/bin/env python3

from flask import Flask, render_template

#####################
### QUERY HELPERS ###
#####################

info_rm = Flask(__name__)

class Filter:
    _OPS = ["=", "<", "<=", ">", ">="]

    def __init__(self, field, operation, value):
        cls = self.__class__
        self.field = field
        if operation in cls._OPS:
            self.operation = operation
        else:
            print(f"ERROR: Filter class only accepts the following operation values: {str(cls._OPS)[1:-1]}")
        self.value = value

    def to_str(self):
        return "{self.field} {self.operation} {self.value}"


class FilterList:
    _LOPS = ["AND", "OR"]

    def __init__(self, filters, logical_operator):
        cls = self.__class__
        if logical_operator in cls._LOPS:
            self.logical_operator = logical_operator
        else:
            print("ERROR: FilterList class only accepts the following logical operator values: {str(cls._LOPS)[1:-1])}")
        if isinstance(filters, list):
            self.filters = filters
        else:
            print("ERROR: FilterList class attribute filters must be a list.")

    def to_str(self):
        cls = self.__class__
        return f" {self.logical_operator} ".join([filter.to_str() for filter in self.filters])

class OrderBy:

    def __init(self, ordering_fields):
        if isinstance(self.ordering_fields, list) or isinstance(self.ordering_fields, str):
            self.ordering_fields = ordering_fields
        else:
            print("ERROR: OrderBy class only accepts lists and strings as values for the ordering_fields attribute.")

    def to_str(self):
        if isinstance(self.ordering_fields, list):
            return ", ".join(self.ordering_fields)
        else:
            return self.ordering_fields

class Select:

    def __init(self, selection_fields):
        if isinstance(self.selection_fields, list) or isinstance(self.selection_fields, str):
            self.selection_fields = selection_fields
        else:
            print("ERROR: Select class only accepts lists and strings as values for the selection_fields attribute.")

    def to_str(self):
        if isinstance(self.selection_fields, list):
            return ", ".join(self.selection_fields)
        else:
            return self.selection_fields


class Statement:

    def __init__(self, **kwargs)
        if kwargs.get("table_name") and kwargs.get("selections"):
            self.table_name = kwargs.get("table_name")
            self.selection_fields = kwargs.get("selections")
        else:
            print("ERROR: Fields table_name and selection_fields are required for instances of the Statement class.")
        if kwargs.get("orderings"):
            self.ordering_fields = kwargs.get("orderings")
        if kwargs.get("filters"):
            self.filter_statements = kwargs.get("filters")

    def to_str(self):
            query_string = f"SELECT {self.selection_fields.to_str()} FROM {self.table_name}"
        if hasattr(self, filter_statements):
            query_string += f" WHERE {self.filter_statements.to_str()}"

        if hasattr(self, order_fields):
            query_string += f" ORDER BY {self.ordering_fields.to_str()}"
        return f"{query_string};"
            

def query_db(**kwargs):
    query_string = Statement(**kwargs).to_str()
    
def generate_card(rank, player_name, team_name, logo_url, value):
    f"""<li class="list-group-item">
          <div class="row h-100 justify-content-center align-items-center">
            <div class="col-3 text-left float-left">
              <img src="{logo_url}" height="30px"/>
            </div>
            <div class="col-6 text-left float-center">
              <div class="row">
                <strong>{rank}. {player_name}</strong>
              </div>
              <div class="row">
                {team_name}
              </div>
            </div>
            <div class="col-3 text-right float-right">
              <strong>{value}</strong>
            </div>
          </div>
        </li>
    """

@info_rm.route("/")
def all_leagues():
    return render_template("index.html")

@info_rm.route("/bundesliga")
def bundesliga():
    return render_template("index.html")

@info_rm.route("/ligue-1")
def ligue_1():
    return render_template("index.html")

@info_rm.route("/la-liga")
def la_liga():
    return render_template("index.html")

@info_rm.route("/premier-league")
def premier_league():
    return render_template("index.html")

@info_rm.route("/serie-a")
def serie_a():
    return render_template("index.html")

if __name__ == "__main__":
    : info_rm.run(debug=True)
