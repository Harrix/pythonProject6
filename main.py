import os
import sqlite3
from functools import wraps
import datetime
from flask import Flask, render_template, request, current_app, redirect, session
import csv

from view_addatm import *
from view_listatm import *
from view_command import *

app = Flask(
    __name__, static_url_path="", static_folder="static", template_folder="templates"
)
app.secret_key = "sdfgasdf"


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


def authorization(func):
    def wrapper(cursor, connection):
        args = {}
        args['access'] = 0
        name = session.get("name", "")
        password = session.get("password", "")
        if not (name and password):
            return render_template("login.html", args=args)
        name = name.lower()
        cursor.execute(f"SELECT * FROM users WHERE LOWER(name)='{name}' AND password='{password}';")
        row = cursor.fetchone()
        if row:
            args['access'] = 1
            print("Вход успешен")
            return func(cursor, connection, args)
        else:
            return render_template("login.html", args=args)

    return wrapper


@app.route("/", endpoint="index", methods=["GET", "POST"])
@connect_db
def index_route(cursor, connection):
    args = {}
    args["access"] = 0
    args["title"] = "Главная страница"
    args["приветствие"] = "Привет!"

    remember = False
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        remember = request.form.get("remember", False)
    else:
        name = session.get("name", "")
        password = session.get("password", "")
    if not (name and password):
        return render_template("login.html", args=args)
    select_all_rows = (
        f"SELECT * FROM users WHERE LOWER(name)='{name}' AND password='{password}';"
    )
    cursor.execute(select_all_rows)
    row = cursor.fetchone()
    if row:
        args["access"] = 1
        session["name"] = name
        session["password"] = password
        if remember:
            session.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(days=7)
        else:
            session.permanent = False
        return render_template("index.html", args=args)
    else:
        return render_template("login.html", args=args)


@app.route("/addatm", endpoint="addatm", methods=["GET", "POST"])
@connect_db
@authorization
def addatm_route(cursor, connection, args):
    return addatm(cursor, connection, args)


@app.route("/listatm", endpoint="listatm", methods=["GET", "POST"])
@connect_db
@authorization
def listatm_route(cursor, connection, args):
    return listatm(cursor, connection, args)


@app.route("/command", endpoint="command", methods=["GET", "POST"])
@connect_db
@authorization
def command_route(cursor, connection, args):
    return command(cursor, connection, args)


@app.route("/deleteatm", endpoint="deleteatm", methods=["GET", "POST"])
@connect_db
@authorization
def deleteatm(cursor, connection, args):
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


@app.route("/editatm", endpoint="editatm", methods=["GET", "POST"])
@connect_db
@authorization
def editatm(cursor, connection, args):
    args = dict()
    args["title"] = "Редактировать карту"
    if request.method == "GET":
        id = request.args.get("id")
        if not id:
            args["error"] = "Номер банкомата пустой"
            return render_template("error.html", args=args)

        args["id"] = id
        return render_template("editatm.html", args=args)
    elif request.method == "POST":
        ll=request.form.get("ll", "")
        id=request.form.get("id", "")
        if not ll:
            args["error"] = "Не ввели Device ID"
            return render_template("error.html", args=args)
        query = (
            f"UPDATE atm SET ll = '{ll}' WHERE id={id};"
        )
        cursor.execute(query)
        connection.commit()

        return redirect(f"/listatm", 301)


@app.route("/clearmessages", endpoint="clearmessages", methods=["GET", "POST"])
@connect_db
@authorization
def clearmessages(cursor, connection, args):
    query = "DELETE FROM messages;"
    cursor.execute(query)
    connection.commit()
    return redirect(f"/list-messages", 301)


@app.route("/list-messages", endpoint="listmessages", methods=["GET", "POST"])
@connect_db
@authorization
def listmessages(cursor, connection, args):
    args["title"] = "Список сообщений"

    query = (
        f"SELECT * FROM messages ;"
    )
    cursor.execute(query)
    messages = cursor.fetchall()
    args["count"] = len(messages)
    args["messages"] = messages[:1000]

    if request.method == "GET":
        return render_template("listmessages.html", args=args)
    elif request.method == "POST":
        return render_template("listmessages.html", args=args)


@app.route("/load-csv", endpoint="loadcsv", methods=["GET", "POST"])
@connect_db
@authorization
def loadcsv(cursor, connection, args):
    args = dict()
    args["title"] = "Загрузить CSV"
    if request.method == "GET":
        return render_template("loadcsv.html", args=args)
    elif request.method == "POST":
        if 'file' not in request.files:
            args["error"] = "No file part"
            return render_template("error.html", args=args)
        file = request.files['file']
        if file.filename == '':
            args["error"] = "No selected file"
            return render_template("error.html", args=args)
        if file and file.filename.endswith('.csv'):
            file_data = file.read().decode('utf-8')
            csv_reader = csv.reader(file_data.splitlines())
            rows = list(csv_reader)
            # Печать массива строк в консоль (можно обработать по-другому)
            # for row in rows:
            #     print(row)
            lines = []
            for i, row in enumerate(rows):
                if i == 0:
                    continue
                eventype = row[1]
                timestamp = row[2]
                device_id = row[3]
                user_id = row[4]
                details = row[5]
                if len(row) > 6:
                    value = row[6]
                else:
                    value=" "
                lines.append(f'("{eventype}", "{timestamp}", "{device_id}", "{user_id}", "{details}", "{value}")')
            query = f'INSERT INTO messages (eventype, timestamp, device_id, user_id, details, value) VALUES {", ".join(lines)};'
            cursor.execute(query)
            connection.commit()
            return redirect(f"/list-messages", 301)
        else:
            args["error"] = "Invalid file type. Only CSV files are allowed."
            return render_template("error.html", args=args)



@app.route("/map", endpoint="map", methods=["GET", "POST"])
@connect_db
@authorization
def listmessages(cursor, connection, args):
    args["title"] = "Карта"

    query = (
        f"SELECT * FROM atm ;"
    )
    cursor.execute(query)
    atms = cursor.fetchall()
    lines=[]
    for atm in atms:
        lines.append(atm["ll"].replace("%2C", ","))


    url = f"https://static-maps.yandex.ru/v1?ll=37.620070,55.753630&lang=ru_RU&size=450,450&z=10&pt={"~".join(lines)}&apikey=f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
    print(url)
    # url = f"https://static-maps.yandex.ru/v1?ll=37.620070,55.753630&lang=ru_RU&size=450,450&z=13&pt=37.620070,55.753630~37.623664,55.76094&apikey=f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
    args['image_url'] = url

    return render_template("map.html", args=args)

@app.route("/exit")
def exit_from_profile():
    session.pop("email", None)
    session.pop("name", None)
    session.pop("password", None)
    return redirect("/", 301)

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
