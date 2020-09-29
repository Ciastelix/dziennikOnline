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

test = Blueprint("test", __name__, static_folder="static", template_folder="templates")

ocena = 0


@test.route("/", methods=["POST", "GET"])
def tescik():
    global pytania
    pytania = []
    stworzKusory("e")
    kursor.execute("SELECT COUNT(*) from w")
    maxLiczba = kursor.fetchall()
    if request.method == "POST":
        liczba = int(request.form["liczbaPytan"])
        kursor.execute(f"SELECT * from w order by RAND() LIMIT {liczba}")
        for i in kursor:
            pytania.append(list(i))
        return redirect(url_for("test.pytanie"))
    else:
        return render_template("test.html", liczbaMax=maxLiczba)


@test.route("/pytania/", methods=["POST", "GET"])
def pytanie():
    global ocena
    if request.method == "POST":
        a = []
        for i in pytania:
            i[0] = str(i[0])
            a.append(request.form[f"{i[0]}"])
        i = 0
        wynik = 0
        while i < len(pytania):
            if pytania[i][6].lower() == "a".lower():
                if a[i] == pytania[i][2]:
                    wynik += 1
            elif pytania[i][6].lower() == "b".lower():
                if a[i] == pytania[i][3]:
                    wynik += 1
            elif pytania[i][6].lower() == "c".lower():
                if a[i] == pytania[i][4]:
                    wynik += 1
            else:
                if a[i] == pytania[i][5]:
                    wynik += 1
            i += 1
        wynik /= len(pytania)
        if wynik < 0.31:
            ocena = 1
        elif wynik > 0.30 and wynik < 0.46:
            ocena = 2
        elif wynik > 0.45 and wynik < 0.61:
            ocena = 3
        elif wynik > 0.60 and wynik < 0.76:
            ocena = 4
        elif wynik > 0.75 and wynik < 0.91:
            ocena = 5
        else:
            ocena = 6
        return redirect(url_for("test.czyDodac"))
    else:

        return render_template("pytanie.html", pytania=pytania)


@test.route("/pytania/wynik", methods=["POST", "GET"])
def czyDodac():
    if request.method == "POST":
        if request.form["dodawanie"] == "DODAJ":
            return redirect(url_for("dodaj.dodajOcene"))
        else:
            return redirect(url_for("test.tescik"))
    else:
        return render_template("wynik.html")


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


@test.errorhandler(404)
def page_not_found(e):
    flash("Strona nie istnieje")
    return render_template("index.html"), 404
