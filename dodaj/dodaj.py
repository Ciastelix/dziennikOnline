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
from sqlalchemy import func
from models import (
    Uczen,
    Klasa,
    Nauczyciel,
    Ocena,
    Przedmiot,
    KontoNauczyciela,
    KontoUcznia,
)
from app import db
from datetime import date
from string import ascii_letters
from random import choice

doHasla = [i for i in zip(ascii_letters, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])]
dodaj = Blueprint(
    "dodaj", __name__, static_folder="static", template_folder="templates"
)


@dodaj.route("/uczen/", methods=["POST", "GET"])
def dodajUcznia():

    if "id" not in session:
        return redirect(url_for("login"))
    elif session["czyNauczyciel"] == False:
        return redirect(url_for("home"))
    else:
        if request.method == "POST":
            imie = request.form["imie"]
            nazwisko = request.form["nazwisko"]
            dataUrodzenia = request.form["dataUrodzenia"]
            pesel = request.form["pesel"]
            klasa = request.form.get("klasa")
            dataUrodzenia = dataUrodzenia.split("-")
            uczen = Uczen(
                nazwisko=nazwisko,
                imie=imie,
                dataUrodzenia=date(
                    int(dataUrodzenia[0]), int(dataUrodzenia[1]), int(dataUrodzenia[2])
                ),
                pesel=pesel,
                klasa=klasa,
            )
            db.session.add(uczen)
            while True:
                login = ""
                for _ in range(10):
                    login += str(choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
                try:
                    KontoUcznia.query.filter_by(login=login).first()
                    continue
                except:
                    try:
                        KontoNauczyciela.query.filter_by(login=login).first()[0]
                        continue
                    except:
                        break
            haslo = ""
            for _ in range(10):
                haslo += str(choice(doHasla))
            idUcznia = db.session.query(func.max(KontoUcznia.id)).first()[0]
            konto = KontoUcznia(login=login, haslo=haslo, uczen=int(idUcznia.id) + 1)
            db.session.add(konto)
            db.session.commit()
            flash("Dodano")
            return render_template("dodaj_ucznia.html")
        else:
            klasy = Klasa.query.all()
            return render_template("dodaj_ucznia.html", klasy=klasy)


@dodaj.route("/nauczyciel/", methods=["POST", "GET"])
def dodajNauczyciela():
    if "id" not in session:
        return redirect(url_for("login"))
    else:
        if session["czyNauczyciel"] == False:
            return redirect(url_for("home"))
        else:
            if request.method == "POST":
                imie = request.form["imie"]
                nazwisko = request.form["nazwisko"]
                nauczyciel = Nauczyciel(imie=imie, nazwisko=nazwisko)
                db.session.add(nauczyciel)
                while True:

                    login = ""
                    for _ in range(10):
                        login += str(choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
                    try:
                        KontoNauczyciela.query.filter_by(login=login).first()[0]
                        continue
                    except:
                        try:
                            KontoUcznia.query.filter_by(login=login).first()
                            continue
                        except:
                            break

                haslo = ""
                for _ in range(10):
                    haslo += str(choice(doHasla))
                idNauczyciela = db.session.query(func.max(KontoNauczyciela.id)).first()
                konto = KontoNauczyciela(
                    login=login, haslo=haslo, nauczyciel=int(idNauczyciela.id) + 1
                )
                db.session.add(konto)
                db.session.commit()
                flash("Dodano")
                return render_template("dodaj_nauczyciela.html")
            else:
                return render_template("dodaj_nauczyciela.html")


@dodaj.route("/ocena/<ocen>/", methods=["POST", "GET"])
def dodajOcene(ocen=0):
    if "id" not in session:
        return redirect(url_for("login"))
    else:
        if session["czyNauczyciel"] == False:
            return redirect(url_for("home"))
        elif "klasa" not in session:
            return redirect(url_for("wyborKlasy"))

        else:
            if request.method == "POST":
                uczen = request.form.get("uczen")
                nauczyciel = request.form.get("nauczyciel")
                przedmiot = request.form.get("przedmiot")
                ocena = request.form.get("ocena")
                opis = request.form["opis"]
                nowaOcena = Ocena(
                    uczen=uczen,
                    nauczyciel=nauczyciel,
                    przedmiot=przedmiot,
                    ocena=str(ocena),
                    opis=opis,
                    dataWystawienia=date.today(),
                )
                db.session.add(nowaOcena)
                db.session.commit()
                flash("Dodano")
                return render_template("dodaj_ocene.html")
            else:
                uczniowie = Uczen.query.filter_by(klasa=session["klasa"])
                nauczyciele = Nauczyciel.query.all()
                przedmioty = Przedmiot.query.all()
                if int(ocen) == 0:
                    oceny = [1, 2, 3, 4, 5, 6, "+", "-", "np"]
                else:
                    oceny = [ocena]
                return render_template(
                    "dodaj_ocene.html",
                    uczniowie=uczniowie,
                    nauczyciele=nauczyciele,
                    przedmioty=przedmioty,
                    oceny=oceny,
                )


@dodaj.route("/klasa/", methods=["POST", "GET"])
def dodajKlase():
    if "id" not in session:
        return redirect(url_for("login"))
    else:
        if session["czyNauczyciel"] == False:
            return redirect(url_for("home"))
        else:
            if request.method == "POST":

                klasa = str(request.form["klasa"])
                if True:
                    Klasa.query.filter_by(klasa=klasa.upper()).all()
                    flash(f"Klasa {klasa} już istnieje")
                    return render_template("dodaj_klase.html")
                if False:
                    kl = Klasa(klasa=klasa.upper())
                    db.session.add(kl)
                    db.session.commit()
                    flash("Dodano")
                    return render_template("dodaj_klase.html")
            else:
                return render_template("dodaj_klase.html")


@dodaj.errorhandler(404)
def page_not_found(e):
    flash("Strona nie istnieje")
    return render_template("index.html"), 404
