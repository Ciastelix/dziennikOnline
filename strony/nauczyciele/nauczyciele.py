from flask import (
    Flask,
    redirect,
    url_for,
    render_template,
    request,
    session,
    flash,
    Blueprint,
)
import mysql.connector

nauczyciele = Blueprint(
    "nauczyciele", __name__, static_folder="static", template_folder="templates"
)


@nauczyciele.route("/")
def listaNauczycieli():
    if "user" not in session:
        return redirect(url_for("login"))
    elif "klasa" not in session:
        return redirect(url_for("wyborKlasy"))
    else:
        stworzKusory()
        kursor.execute("SELECT Imie, Nazwisko from Nauczyciele order by Nazwisko asc")
        return render_template("lista_nauczycieli.html", va=kursor)


@nauczyciele.errorhandler(404)
def page_not_found(e):
    flash("Strona nie istnieje")
    return render_template("index.html"), 404


def stworzKusory(baza="oceny"):
    global kursor
    global db

    if "user" in session:
        if session["user"] == "root":
            db = mysql.connector.connect(
                host="localhost",
                user=session["user"],
                passwd=session["password"],
                database=f"{baza}",
            )
            kursor = db.cursor(buffered=True)
        else:
            db = mysql.connector.connect(
                host="localhost", user="root", passwd="", database=f"{baza}",
            )
            kursor = db.cursor(buffered=True)
    else:
        db = mysql.connector.connect(
            host="localhost", user="root", passwd="", database=f"{baza}",
        )
        kursor = db.cursor(buffered=True)
