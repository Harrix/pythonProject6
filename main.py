import os
import sqlite3
import pymysql
from functools import wraps
from flask import Flask, render_template, request, current_app

app = Flask(
    __name__, static_url_path="", static_folder="static", template_folder="templates"
)


def connect_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            db_path = os.path.join(current_app.root_path, 'db', 'main.db')
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            print("Успешно подключились к SQLite БД.")
            try:
                cursor = connection.cursor()
                result = func(cursor, connection, *args, **kwargs)
            finally:
                connection.close()
                print("Соединение с SQLite БД закрыто.")
        except Exception as ex:
            print("Не удалось подключиться к SQLite БД.")
            print(ex)
        return result

    return wrapper


@app.route("/", endpoint="index", methods=["GET", "POST"])
@connect_db
def index(cursor, connection):
    args = dict()
    args["title"] = "Проект такой-то"
    args["приветствие"] = "Привет!"
    if request.method == "GET":
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
        result=[]
        for user in users:
            result.append(user["name"])
        args["users"] = result
        return render_template("index.html", args=args)
    elif request.method == "POST":
        return render_template("index.html")


@app.route("/bla", endpoint="bla", methods=["GET", "POST"])
@connect_db
def bla(cursor, connection):
    args = dict()
    args["title"] = "Проект такой-то"
    if request.method == "GET":
        return render_template("hello.html", args=args)
    elif request.method == "POST":
        return render_template("hello.html", args=args)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
