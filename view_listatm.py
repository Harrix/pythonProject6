import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, current_app, redirect

def listatm(cursor, connection, args):
    # args = dict()
    args["title"] = "Список банкоматов"

    query = (
        f"SELECT * FROM atm;"
    )
    cursor.execute(query)
    atms = cursor.fetchall()
    args["atms"] = atms

    if request.method == "GET":
        return render_template("listatm.html", args=args)
    elif request.method == "POST":
        return render_template("listatm.html", args=args)