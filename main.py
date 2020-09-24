from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from time import sleep
import mysql.connector


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=20)


@app.route("/")
@app.route("/home/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    if "klasa" not in session:
        return redirect(url_for("wyborKlasy"))
    stworzKusory()
    kursor.execute(f"SELECT Klasa from Klasa where IdKlasy={session['klasa']}")
    return render_template("index.html", klasa=kursor)


@app.route("/login/", methods=["POST", "GET"])
def login():
    global db
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        db = mysql.connector.connect(
            host="localhost", user=user, passwd=password, database="oceny"
        )

        if db:
            session.permanent = True
            session["user"] = user
            session["password"] = password
            return redirect(url_for("wyborKlasy"))
        else:
            flash("Niepoprawne dane!")
    else:
        if "user" in session:
            db = mysql.connector.connect(
                host="localhost",
                user=session["user"],
                passwd=session["password"],
                database="oceny",
            )

            return redirect(url_for("user"))
        return render_template("login.html")


def stworzKusory():
    global kursor
    global db
    db = mysql.connector.connect(
        host="localhost",
        user=session["user"],
        passwd=session["password"],
        database="oceny",
    )
    kursor = db.cursor(buffered=True)


@app.route("/wybor/klasa/", methods=["POST", "GET"])
def wyborKlasy():
    session.permanent = True
    stworzKusory()
    kursor.execute("SELECT * from Klasa")
    if request.method == "POST":
        session["klasa"] = int(request.form.get("klasa"))
        return redirect(url_for("home"))

    else:
        return render_template("wybor_klasy.html", klasy=kursor)


@app.route("/logout/")
def logout():
    if "user" in session:
        session.pop("user", None)
        session.pop("password", None)
        session.pop("email", None)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


@app.route("/user/", methods=["POST", "GET"])
def user():
    if "user" in session:
        stworzKusory()
        kursor.execute(f"SHOW GRANTS FOR {session['user']}@'localhost'")
        return render_template("user.html", uprawnienia=kursor)
    elif "klasa" not in session:
        return redirect(url_for("wyborKlasy"))
    else:
        return redirect(url_for("login"))


@app.route("/dodaj/uczen/", methods=["POST", "GET"])
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


@app.route("/dodaj/nauczyciel/", methods=["POST", "GET"])
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


@app.route("/dodaj/ocena/", methods=["POST", "GET"])
def dodajOcene():
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
        kursor.execute("SELECT distinct Ocena from Oceny")
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


@app.route("/dodaj/klasa/", methods=["POST", "GET"])
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


@app.route("/uczniowie/")
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


@app.route("/lista/nauczyciele/")
def listaNauczycieli():
    if "user" not in session:
        return redirect(url_for("login"))
    elif "klasa" not in session:
        return redirect(url_for("wyborKlasy"))
    else:
        stworzKusory()
        kursor.execute("SELECT Imie, Nazwisko from Nauczyciele order by Nazwisko asc")
        return render_template("lista_nauczycieli.html", va=kursor)


@app.errorhandler(404)
def page_not_found(e):
    flash("Strona nie istnieje")
    return render_template("index.html"), 404


@app.route("/uczniowie/oceny/<ide>/", methods=["POST", "GET"])
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


@app.route("/uczniowie/oceny/<ide>/<ideOceny>/", methods=["POST", "GET"])
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


if __name__ == "__main__":
    app.run(debug=True)
