import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, current_app, redirect


def index(cursor, connection):
    args = dict()
    args["title"] = "Главная страница"
    args["приветствие"] = "Привет!"
    if request.method == "GET":
        return render_template("index.html", args=args)
    elif request.method == "POST":
        return render_template("index.html")