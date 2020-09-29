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

dodaj = Blueprint(
    "dodaj", __name__, static_folder="static", template_folder="templates"
)


@dodaj.route("/uczen/", methods=["POST", "GET"])
def dodajUcznia():

    if "user" not in session:
        return redirect(url_for("login"))
    elif "klasa" not in session:
        return redirect(url_for("wyborKlasy"))
    else:
        stworzKusory()
        kursor.execute("SELECT IdKlasy, Klasa from Klasa")
        if request.method == "POST":
            imie = request.form["imie"]
            nazwisko = request.form["nazwisko"]
            dataUrodzenia = request.form["dataUrodzenia"]
            pesel = request.form["pesel"]
            klasa = request.form.get("klasa")

            kursor.execute(
                "INSERT INTO `Uczniowie`(`Nazwisko`, `Imie`, `DataUrodzenia`, `PESEL`, `IDKlasy`) VALUES ('{}', '{}', '{}', '{}', {})".format(
                    nazwisko, imie, dataUrodzenia, pesel, int(klasa)
                )
            )
            db.commit()
            flash("Dodano")
            return render_template("dodaj_ucznia.html")
        else:
            return render_template("dodaj_ucznia.html", klasy=kursor)


@dodaj.route("/nauczyciel/", methods=["POST", "GET"])
def dodajNauczyciela():
    if "user" not in session:
        return redirect(url_for("login"))
    elif "klasa" not in session:
        return redirect(url_for("wyborKlasy"))
    else:
        stworzKusory()
        if request.method == "POST":
            imie = request.form["imie"]
            nazwisko = request.form["nazwisko"]

            kursor.execute(
                f"INSERT INTO `Nauczyciele`(`Nazwisko`, `Imie`) VALUES ('{nazwisko}', '{imie}')"
            )
            db.commit()
            flash("Dodano")
            return render_template("dodaj_nauczyciela.html")
        else:
            return render_template("dodaj_nauczyciela.html")


@dodaj.route("/ocena/", methods=["POST", "GET"])
def dodajOcene():
    global ocena
    if "user" not in session:
        return redirect(url_for("login"))
    elif "klasa" not in session:
        return redirect(url_for("wyborKlasy"))
    else:
        stworzKusory()
        kursor.execute(
            f"SELECT IdUcznia, CONCAT(Imie, ' ', Nazwisko) from Uczniowie where Uczniowie.IDKlasy={session['klasa']} order by Nazwisko asc"
        )
        uczniowie = kursor.fetchall()

        kursor.execute(
            "SELECT IdNauczyciela, CONCAT(Imie, ' ', Nazwisko) from Nauczyciele order by Nazwisko asc"
        )
        nauczyciele = kursor.fetchall()
        kursor.execute(
            "SELECT IdPrzedmiotu, Przedmiot from Przedmioty order by Przedmiot asc"
        )
        przedmioty = kursor.fetchall()
        try:
            if ocena != 0:
                kursor.execute(
                    f"SELECT distinct Ocena from Oceny where Ocena={ocena} order by Ocena"
                )
                oceny = kursor.fetchall()
                ocena = 0
            else:
                kursor.execute("SELECT distinct Ocena from Oceny order by Ocena")
                oceny = kursor.fetchall()
        except:
            kursor.execute("SELECT distinct Ocena from Oceny order by Ocena")
            oceny = kursor.fetchall()
        if request.method == "POST":
            session.permanent = True
            uczen = request.form.get("uczen")
            nauczyciel = request.form.get("nauczyciel")
            przedmiot = request.form.get("przedmiot")
            ocena = request.form.get("ocena")
            opis = request.form["opis"]
            kursor.execute(
                f"INSERT INTO `Oceny`(`IdUcznia`, `IdNauczyciela`, `IdPrzedmiotu`, `Ocena`, `Opis`) VALUES ({uczen}, {nauczyciel}, {przedmiot}, {ocena}, '{opis}')"
            )
            db.commit()
            flash("Dodano")
            return render_template("dodaj_ocene.html")
        else:
            return render_template(
                "dodaj_ocene.html",
                uczniowie=uczniowie,
                nauczyciele=nauczyciele,
                przedmioty=przedmioty,
                oceny=oceny,
            )


@dodaj.route("/klasa/", methods=["POST", "GET"])
def dodajKlase():
    if request.method == "POST":
        stworzKusory()
        klasa = request.form["klasa"]
        if klasa == "":
            flash("Podaj Klasę")
            return render_template("dodaj_klase.html")
        kursor.execute(f"INSERT INTO `Klasa`(`Klasa`) VALUES ('{klasa}')")
        db.commit()
        flash("Dodano")
        return render_template("dodaj_klase.html")
    else:
        return render_template("dodaj_klase.html")


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


@dodaj.errorhandler(404)
def page_not_found(e):
    flash("Strona nie istnieje")
    return render_template("index.html"), 404
