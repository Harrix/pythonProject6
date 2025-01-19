import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, current_app, redirect

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
    args["title"] = "Главная страница"
    args["приветствие"] = "Привет!"
    if request.method == "GET":
        return render_template("index.html", args=args)
    elif request.method == "POST":
        return render_template("index.html")


@app.route("/addatm", endpoint="addatm", methods=["GET", "POST"])
@connect_db
def addatm(cursor, connection):
    args = dict()
    args["title"] = "Добавить банкомат"
    if request.method == "GET":
        return render_template("addatm.html", args=args)
    elif request.method == "POST":
        deviceid=request.form.get("deviceid", "")
        ll=request.form.get("ll", "")
        if not deviceid:
            args["error"] = "Не ввели Device ID"
            return render_template("error.html", args=args)
        query = (
            f"INSERT INTO atm (device_id, ll, status) VALUES ('{deviceid}', '{ll}', 1);"
        )
        cursor.execute(query)
        connection.commit()

        return redirect(f"/listatm", 301)


@app.route("/listatm", endpoint="listatm", methods=["GET", "POST"])
@connect_db
def listatm(cursor, connection):
    args = dict()
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


@app.route("/deleteatm", endpoint="deleteatm", methods=["GET", "POST"])
@connect_db
def deleteatm(cursor, connection):
    args = dict()
    args["title"] = "Удалить банкомат"
    id = request.args.get("id")
    if not id:
        args["error"] = "Номер банкомата пустой"
        return render_template("error.html", args=args)

    query = (
        f"DELETE FROM atm WHERE id={id};"
    )
    cursor.execute(query)
    connection.commit()

    return redirect(f"/listatm", 301)



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
