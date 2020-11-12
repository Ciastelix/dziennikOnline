from app import db
from datetime import date, timedelta


class Uczen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazwisko = db.Column(db.String(40), nullable=False)
    imie = db.Column(db.String(40), nullable=False)
    dataUrodzenia = db.Column(db.Date, default=date.today())
    pesel = db.Column(db.String(11))
    klasa = db.Column(db.Integer, db.ForeignKey("klasa.id"))

    def __init__(self, nazwisko, imie, dataUrodzenia, pesel, klasa):
        self.nazwisko = nazwisko
        self.imie = imie
        self.dataUrodzenia = dataUrodzenia
        self.pesel = pesel
        self.klasa = klasa

    oceny = db.relationship("Ocena", backref="oceny")
    konto = db.relationship("KontoUcznia", backref="uzytkownikUczen", uselist=False)


class Klasa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    klasa = db.Column(db.String(10), nullable=False)
    wychowawca = db.Column(db.Integer, db.ForeignKey("nauczyciel.id"))

    uczniowie = db.relationship("Uczen", backref="uczniowie")


class Przedmiot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    przedmiot = db.Column(db.String(20), unique=True)
    nauczyciele = db.relationship("Nauczyciel", backref="nauczyciele")


class Ocena(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uczen = db.Column(db.Integer, db.ForeignKey("uczen.id"))
    nauczyciel = db.Column(db.Integer, db.ForeignKey("nauczyciel.id"))
    przedmiot = db.Column(db.Integer, db.ForeignKey("przedmiot.id"))
    ocena = db.Column(db.String(2))
    opis = db.Column(db.String(3))
    dataWystawienia = db.Column(db.Date, default=date.today())


class Nauczyciel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazwisko = db.Column(db.String(20))
    imie = db.Column(db.String(20))
    przedmiot = db.Column(db.Integer, db.ForeignKey("przedmiot.id"))

    wystawione = db.relationship("Ocena", backref="wystawione")
    wychowawcy = db.relationship("Klasa", backref="wychowawcy")
    konto = db.relationship(
        "KontoNauczyciela", backref="uzytkownikNauczyciel", uselist=False
    )


class KontoUcznia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uczen = db.Column(db.Integer, db.ForeignKey("uczen.id"))
    login = db.Column(db.String(20), unique=True)
    haslo = db.Column(db.String(20))


class KontoNauczyciela(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nauczyciel = db.Column(db.Integer, db.ForeignKey("nauczyciel.id"))
    login = db.Column(db.String(20), unique=True)
    haslo = db.Column(db.String(20))
