from app import app, db
from flask import redirect, url_for, render_template, request, session, flash
import sqlalchemy
from models import Klasa, KontoNauczyciela, KontoUcznia, Nauczyciel


@app.route("/")
@app.route("/home/")
def home():
    if "id" not in session:
        return redirect(url_for("login"))
    else:
        klasa = Klasa.query.filter_by(id=session["klasa"]).first()
        return render_template("index.html", klasa=klasa.klasa)


@app.route("/login/", methods=["POST", "GET"])
def login():
    session.permanent = True
    if request.method == "POST":
        login = request.form["username"]
        haslo = request.form["password"]
        try:
            uczen = KontoUcznia.query.filter_by(login=login, haslo=haslo).one()
            session["czyNauczyciel"] = False
            session["id"] = uczen.uczen
            return redirect(url_for("user"))

        except:
            try:
                nauczyciel = KontoNauczyciela.query.filter_by(
                    login=login, haslo=haslo
                ).one()
                session["czyNauczyciel"] = True
                session["id"] = nauczyciel.nauczyciel
                return redirect(url_for("wyborKlasy"))
            except:
                flash("Niepoprawne dane!")
                return redirect(url_for("login"))

    elif "id" in session:
        if session["czyNauczyciel"]:
            return redirect(url_for("wyborKlasy"))
        else:
            return redirect(url_for("user"))
    else:
        return render_template("login.html")


@app.route("/wybor/klasa/", methods=["POST", "GET"])
def wyborKlasy():
    if request.method == "POST":
        session["klasa"] = int(request.form.get("klasa"))
        return redirect(url_for("home"))
    else:
        klasa = Klasa.query.all()
        return render_template("wybor_klasy.html", klasy=klasa)


@app.route("/logout/")
def logout():
    if "id" in session:
        session.pop("id", None)
        session.pop("czyNauczyciel", None)
        session.pop("klasa", None)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


@app.route("/user/", methods=["POST", "GET"])
def user():
    if "id" in session:
        return render_template("user.html")
    else:
        return redirect(url_for("login"))


@app.route("/user/zmiana/", methods=["POST", "GET"])
def zmiana():
    if "id" in session:
        if request.method == "POST":
            login = request.form["login"]
            haslo = request.form["haslo"]
            if session["czyNauczyciel"] == True:
                daneNauczyciela = KontoNauczyciela.query.filter_by(
                    nauczyciel=session["id"]
                ).first()
                if login == "":
                    login = daneNauczyciela.login
                if haslo == "":
                    haslo = daneNauczyciela.haslo
                daneNauczyciela.login = login
                daneNauczyciela.haslo = haslo
            else:
                daneUcznia = KontoUcznia.query.filter_by(uczen=session["id"]).first()
                if login == "":
                    login = daneUcznia.login
                if haslo == "":
                    haslo = daneUcznia.haslo
                daneUcznia.login = login
                daneUcznia.haslo = haslo
            db.session.commit()
            flash("Zmieniono")
            return render_template("edit.html", login=login, haslo=haslo)
        else:

            if session["czyNauczyciel"] == True:
                daneNauczyciela = KontoNauczyciela.query.filter_by(
                    nauczyciel=session["id"]
                ).first()
                return render_template(
                    "edit.html",
                    login=daneNauczyciela.login,
                    haslo=daneNauczyciela.haslo,
                )
            else:
                daneUcznia = KontoUcznia.query.filter_by(uczen=session["id"]).first()
                return render_template(
                    "edit.html", login=daneUcznia.login, haslo=daneUcznia.haslo
                )
    else:
        return redirect(url_for("login"))


@app.route("/nauczyciele/")
def listaNauczycieli():
    if "id" not in session:
        return redirect(url_for("login"))
    else:
        nauczyciele = Nauczyciel.query.all()
        return render_template("lista_nauczycieli.html", nauczyciele=nauczyciele)


@app.errorhandler(404)
def page_not_found(e):
    flash("Strona nie istnieje")
    return render_template("index.html"), 404
