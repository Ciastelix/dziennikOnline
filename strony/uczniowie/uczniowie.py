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

uczniowie = Blueprint(
    "uczniowie", __name__, static_folder="static", template_folder="templates"
)


@uczniowie.route("/")
def listaUczniow():
    if "user" not in session:
        return redirect(url_for("login"))
    elif "klasa" not in session:
        return redirect(url_for("wyborKlasy"))
    else:
        stworzKusory()
        kursor.execute(
            f"SELECT Uczniowie.Nazwisko, Uczniowie.Imie, Uczniowie.IdUcznia from Uczniowie, Klasa where Uczniowie.IDKlasy = {session['klasa']} and Klasa.IdKlasy = Uczniowie.IDKlasy"
        )

        return render_template("lista_uczniow.html", va=kursor)


@uczniowie.route("/oceny/<ide>/", methods=["POST", "GET"])
def ocenyUcznia(ide):
    if request.method == "POST":
        idOceny = int(request.form.get("usuwanie"))
        kursor.execute(f"DELETE from Oceny where IdOceny = {idOceny}")
        db.commit()
        return redirect(url_for("listaUczniow"))
    else:
        global idd
        stworzKusory()
        ide = int(ide)
        idd = ide
        a = []
        kursor.execute("SELECT max(IdPrzedmiotu) from Przedmioty")
        z = kursor.fetchall()
        kursor.execute(
            f"SELECT DISTINCT Oceny.IdPrzedmiotu, Przedmioty.Przedmiot from Oceny, Przedmioty where Oceny.IdUcznia={ide} and Przedmioty.IdPrzedmiotu=Oceny.IdPrzedmiotu"
        )
        przedmioty = kursor.fetchall()
        for num in range(1, z[0][0] + 1):
            kursor.execute(
                f"SELECT COUNT(IdPrzedmiotu) from Oceny WHERE IdUcznia={ide} and IdPrzedmiotu={num}"
            )
            f = kursor.fetchall()
            if f[0][0] == 0:
                continue
            kursor.execute(
                f"SELECT Oceny.IdOceny, Oceny.Ocena, Oceny.IdPrzedmiotu, Przedmioty.Przedmiot, CONCAT(Nauczyciele.Nazwisko,' ', Nauczyciele.Imie), Oceny.Opis from Oceny, Przedmioty, Nauczyciele where Oceny.IdUcznia = {ide} and Oceny.IdPrzedmiotu={num} and Oceny.IdPrzedmiotu = Przedmioty.IdPrzedmiotu and Oceny.IdNauczyciela=Nauczyciele.IdNauczyciela"
            )
            s = kursor.fetchall()
            for i in s:
                a.append(list(i))
        return render_template("oceny.html", oceny=a, przedmioty=przedmioty)


@uczniowie.route("/oceny/<ide>/<ideOceny>/", methods=["POST", "GET"])
def edytujOcene(ide, ideOceny):
    stworzKusory()
    ideOceny = int(ideOceny)
    if request.method == "POST":
        ocena = int(request.form.get("ocena"))
        nauczyciel = int(request.form.get("nauczyciel"))
        przedmiot = int(request.form.get("przedmiot"))
        opis = request.form["opis"]
        kursor.execute(
            f"UPDATE `Oceny` SET `IdNauczyciela`={nauczyciel},`IdPrzedmiotu`={przedmiot},`Ocena`={ocena},`Opis`='{opis}' WHERE IdOceny = {ideOceny}"
        )
        db.commit()
        flash("Zmieniono pomyślnie")
        return redirect(url_for("ocenyUcznia", ide=idd))
    else:

        kursor.execute(
            f"SELECT Oceny.Ocena, Oceny.Opis, Przedmioty.Przedmiot, CONCAT(Nauczyciele.Nazwisko, ' ', Nauczyciele.Imie),  Oceny.IdOceny from Oceny, Nauczyciele, Przedmioty where Oceny.IdOceny = {ideOceny} and Oceny.IdNauczyciela = Nauczyciele.IdNauczyciela and Przedmioty.IdPrzedmiotu = Oceny.IdPrzedmiotu order by Przedmioty.Przedmiot"
        )
        podstawa = kursor.fetchall()
        kursor.execute(
            "SELECT IdNauczyciela, CONCAT(Nazwisko, ' ', Imie) from Nauczyciele"
        )
        nauczyciele = kursor.fetchall()
        kursor.execute("SELECT DISTINCT Ocena from Oceny")
        oceny = kursor.fetchall()
        kursor.execute("SELECT * from Przedmioty")
        przedmioty = kursor.fetchall()

        return render_template(
            "edit.html",
            podstawa=podstawa,
            nauczyciele=nauczyciele,
            oceny=oceny,
            przedmioty=przedmioty,
        )


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


@uczniowie.errorhandler(404)
def page_not_found(e):
    flash("Strona nie istnieje")
    return render_template("index.html"), 404
