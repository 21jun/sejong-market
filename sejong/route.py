
from pathlib import Path
from flask import request, Response
from sejong import app
import json
import datetime

def myconverter(o):
    if isinstance(o, datetime.date):
        return o.__str__()
    elif isinstance(o, datetime.timedelta):
        return o.__str__()

@app.route("/")
def main():
    return "hello world 2"

