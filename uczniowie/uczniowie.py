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
from models import Uczen, Przedmiot, Ocena, Nauczyciel
from sqlalchemy import func
from app import db

uczniowie = Blueprint(
    "uczniowie", __name__, static_folder="static", template_folder="templates"
)


@uczniowie.route("/")
def listaUczniow():
    if "id" not in session:
        return redirect(url_for("login"))
    else:
        if session["czyNauczyciel"] == False:
            return redirect(url_for("home"))
        else:
            uczniowie = Uczen.query.filter_by(klasa=session["klasa"])
            return render_template("lista_uczniow.html", uczniowie=uczniowie)


@uczniowie.route("/oceny/<_id>/", methods=["POST", "GET"])
def ocenyUcznia(_id):
    if request.method == "POST":
        """idOceny = int(request.form.get("usuwanie"))
        kursor.execute(f"DELETE from Oceny where IdOceny = {idOceny}")
        db.commit()
        return redirect(url_for("listaUczniow"))
        """
    else:
        global idd
        _ide = int(_id)
        idd = _ide

        oceny = [i for i in Ocena.query.filter_by(uczen=_id).all()]
        idPrzedmiotow = [i.przedmiot for i in oceny]
        idPrzedmiotow = set(idPrzedmiotow)
        print(idPrzedmiotow)
        przedmioty = [Przedmiot.query.filter_by(id=i).first() for i in idPrzedmiotow]
        nauczyciele = [i for i in Nauczyciel.query.all()]

        return render_template(
            "oceny.html", oceny=oceny, przedmioty=przedmioty, nauczyciele=nauczyciele
        )


@uczniowie.route("/oceny/<_id>/<idOceny>/", methods=["POST", "GET"])
def edytujOcene(_id, idOceny):
    if request.method == "POST":
        ocena = str(request.form.get("ocena"))
        nauczyciel = int(request.form.get("nauczyciel"))
        przedmiot = int(request.form.get("przedmiot"))
        opis = str(request.form["opis"])
        ocena = Ocena.query.filter_by(id=idOceny)
        ocena.ocena = ocena
        ocena.nauczyciel = nauczyciel
        ocena.przedmiot = przedmiot
        ocena.opis = opis
        db.session.commit()
        flash("Zmieniono pomyślnie")
        return redirect(url_for("uczniowie.ocenyUcznia", _id=_id))
    else:
        ocena = Ocena.query.filter_by(id=idOceny).first()
        przedmioty = Przedmiot.query.all()
        nauczyciele = Nauczyciel.query.all()

        return render_template(
            "edit.html", ocena=ocena, nauczyciele=nauczyciele, przedmioty=przedmioty,
        )


@uczniowie.route("/oceny/<idUcznia>/<idOceny>/")
def usunOcene(idUcznia, idOceny):
    ocenaDoUsieniecia = Ocena.query.filter_by(id=idOceny).first()
    db.session.delete(ocenaDoUsieniecia)
    db.session.commit()
    flash("usunięto")
    return redirect(url_for("uczniowie.ocenyUcznia", _id=idUcznia))


@uczniowie.errorhandler(404)
def page_not_found(e):
    flash("Strona nie istnieje")
    return render_template("index.html"), 404
