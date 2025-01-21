import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, current_app, redirect

def command(cursor, connection):
    args = dict()
    args["title"] = "Комманда"

    cursor.execute(f"SELECT * FROM atm;")
    atms = cursor.fetchall()
    args["atms"] = atms

    cursor.execute(f"SELECT * FROM cars;")
    cars = cursor.fetchall()
    args["cars"] = cars

    cursor.execute(f"SELECT * FROM messages;")
    messages = cursor.fetchall()
    args["messages"] = cars

    cursor.execute(f"SELECT * FROM mechanics;")
    mechanics = cursor.fetchall()
    args["mechanics"] = cars

    cursor.execute(f"SELECT * FROM users;")
    users = cursor.fetchall()
    args["users"] = cars

    if request.method == "GET":
        return render_template("command.html", args=args)
    elif request.method == "POST":
        return render_template("command.html", args=args)