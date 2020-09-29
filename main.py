from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
import mysql.connector
from strony.dodaj.dodaj import dodaj
from strony.test.test import test
from strony.uczniowie.uczniowie import uczniowie
from strony.nauczyciele.nauczyciele import nauczyciele


app = Flask(__name__)
app.secret_key = "hello"
app.register_blueprint(dodaj, url_prefix="/dodaj")
app.register_blueprint(test, url_prefix="/test")
app.register_blueprint(uczniowie, url_prefix="/uczniowie")
app.register_blueprint(nauczyciele, url_premix="/nauczyciele")
app.permanent_session_lifetime = timedelta(minutes=20)

ocena = 0


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
        try:
            db = mysql.connector.connect(
                host="localhost", user=user, passwd=password, database="oceny"
            )
            session.permanent = True
            session["user"] = user
            session["password"] = password
            return redirect(url_for("wyborKlasy"))
        except:
            flash("Niepoprawne dane!")
            user = request.form["username"]
            password = request.form["password"]
            stworzKusory()
            kursor.execute(
                f"SELECT COUNT(*) from user where user.user = '{user}' and user.pass = '{password}'"
            )
            uzyt = kursor.fetchall()
            if uzyt[0][0] > 0:
                session["user"] = user
                session["password"]
            return redirect(url_for("test"))
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


@app.errorhandler(404)
def page_not_found(e):
    flash("Strona nie istnieje")
    return render_template("index.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
