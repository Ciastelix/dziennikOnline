from flask_admin import Admin
from datetime import timedelta, date

from app import app
from app import db
import views

from dodaj.dodaj import dodaj
from test.test import test
from uczniowie.uczniowie import uczniowie





#
#! przebudować tabele nauczyciele
# TODO: dodać przedmioty nauczene (max 2)
# TODO: dodać więcej nauczyiceli
# TODO: dodać jako wychowwaców klas
#
#
#! przebudować tabele przedmioty
# TODO: dodać więcej przedmiotów
#
#
#! przebudować tabele klasa;

# TODO: dodać więcej klas
# TODO: dodać wychowawców (id nauczyciela klucz obcy)
#
#! przebudować tabele uczniowie
# TODO: dodać więcej uczniów
#
#! przebudować tabele oceny
# TODO: dodać pole daty

#! przebudować system logowanie
# TODO: dodać baze z nauczycielami (ich id jako klucz obcy) oraz dyrekcji (pole bool admin)
# * jeśli to admin to dać dostęp do wszystkiego
# * nauczyciel ma dostęp do wszystkiego oprócz narzędzi administracyjnych
# TODO: dodać baze z uczniami (ich id jako klucz obcy)
# * uczeń na dostęp jedynie do swoich oceny
# * przeglądanie planu lekcji
#! dodanie planu lekcji zmiana co 24h
# TODO: po zalogowaniu losowane są godziny lekcyjne (6) oraz nauczyciele dla klas (bez powtórzeń)
#! przebudować dodawanie nauczycieli
# TODO: dodać wybór nauczanego przedmiotu
# TODO: dodać wybór jako wychowawca
#! przebudować doadwanie ocen
# TODO: dodać pole wyboru daty
#! zmienić adres strony
# TODO: zmienić adres ip na mnemoniczny
#! pozbyć się testu
# TODO: wyrzucić test do innego projektu
# TODO: dodać adres ip oraz mnemoniczny
#! przebudować wygląd strony
# TODO: zmienić layout
#! naprawa systemu usuwania ocen
# TODO: naprawić system usuwania ocen (zrobić button w nim input dać niewidzalny test)
# ? dodać najnowsze aktualizacje ocen


app.permanent_session_lifetime = timedelta(minutes=20)
admin = Admin(app)
app.register_blueprint(dodaj, url_prefix="/dodaj")
app.register_blueprint(test, url_prefix="/test")
app.register_blueprint(uczniowie, url_prefix="/uczniowie")

if __name__ == "__main__":
    app.run(debug=True)
    db.create_all()
    