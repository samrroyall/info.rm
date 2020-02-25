#!/usr/bin/env python3

from flask import Flask, render_template

info_rm = Flask(__name__)

@info_rm.route("/")
def all_leagues():
    return render_template("/web/index.html")

if __name__ == "__main__":
    info_rm.run(debug=True)
