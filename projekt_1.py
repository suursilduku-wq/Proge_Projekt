"""
Projekt:  Tudengi kulude analüüsija
Autorid:  Uku [perenimi], [paarilise nimi]
Kursus:   Programmeerimine, sügis 2026

Kirjeldus:
    Programm loeb pangast alla laaditud CSV-väljavõtte, jagab kulud
    kategooriatesse, näitab neid graafikul, leiab korduvad väikesed kulud
    ning ennustab, millal raha enne järgmist õppetoetust otsa saab.

Kasutatud allikad:
    - matplotlib õpetus: https://matplotlib.org/stable/tutorials/
    - Pythoni csv-moodul: https://docs.python.org/3/library/csv.html
    - [lisage siia kõik, mida veel kasutate]

Käivitamine:
    python kulude_analuusija.py
    (vajab: pip install matplotlib)
"""

import csv
import matplotlib.pyplot as plt


# Märksõnad, mille järgi tehing kategooriasse pannakse.
# Võti = märksõna saaja nimes (väikeste tähtedega), väärtus = kategooria.
# Täiendage seda sõnastikku oma tehingute järgi!
MARKSONAD = {
    "rimi": "Toit",
    "selver": "Toit",
    "lidl": "Toit",
    "coop": "Toit",
    "wolt": "Toidukuller",
    "bolt": "Transport",
    "elron": "Transport",
    "spotify": "Meelelahutus",
    "kino": "Meelelahutus",
    "cafe": "Väljas käimine",
    "genklubi": "Väljas käimine",
    "zavood": "Väljas käimine",
    "uhiselamu": "Elamine",
}


def loe_fail(failinimi):
    """Loe pangaväljavõte CSV-failist ja tagasta tehingute list.

    Iga tehing on sõnastik kujul:
        {"kuupaev": "03.10.2026", "saaja": "RIMI EESTI FOOD", "summa": -23.45}

    Vihjed:
    - ava fail: open(failinimi, encoding="utf-8")
    - csv.DictReader(fail, delimiter=";") annab iga rea sõnastikuna
    - summa on tekst kujul "-23,45": asenda koma punktiga ja tee float()

    Argumendid:
        failinimi (str): CSV-faili nimi.

    Tagastab:
        list: tehingute sõnastikud.
    """
    tehingud = []
    # TODO: kirjutage siia faili lugemine
    return tehingud


def leia_kategooria(saaja):
    """Leia saaja nime järgi tehingu kategooria.

    Käi läbi sõnastik MARKSONAD. Kui mõni märksõna sisaldub saaja nimes
    (väikeste tähtedega), tagasta selle kategooria. Kui ühtegi ei leita,
    tagasta "Muu".

    Näide: leia_kategooria("RIMI EESTI FOOD") -> "Toit"

    Argumendid:
        saaja (str): saaja nimi väljavõttest.

    Tagastab:
        str: kategooria nimi.
    """
    # TODO
    return "Muu"


def lisa_kategooriad(tehingud):
    """Lisa igale tehingule võti "kategooria".

    Kasuta iga tehingu puhul funktsiooni leia_kategooria().
    Sissetulekutele (summa > 0) pane kategooriaks "Sissetulek".

    Argumendid:
        tehingud (list): loe_fail() tagastatud list.
    """
    # TODO
    pass


def kulud_kategooriate_kaupa(tehingud):
    """Arvuta iga kategooria kulude kogusumma.

    Arvesta ainult kulusid (summa < 0) ja liida need positiivsete
    arvudena, et graafik oleks loetav.

    Näide tulemusest: {"Toit": 116.05, "Transport": 29.90, ...}

    Argumendid:
        tehingud (list): kategooriatega tehingud.

    Tagastab:
        dict: kategooria -> kogusumma eurodes.
    """
    kulud = {}
    # TODO
    return kulud


def prindi_kulud(kulud):
    """Prindi kulud tabelina ekraanile, suurimast väiksemani.

    Iga rea kohta: kategooria, summa ja protsent kogukulust.
    Lõppu rida KOKKU.

    Vihje: sorted(kulud.items(), key=lambda x: x[1], reverse=True)

    Argumendid:
        kulud (dict): kulud_kategooriate_kaupa() tulemus.
    """
    # TODO
    pass


def joonista_graafik(kulud):
    """Joonista kulude tulpdiagramm matplotlibiga.

    Vihjed: plt.bar(nimed, summad), plt.title(...), plt.ylabel("Eurot"),
    plt.show()

    Argumendid:
        kulud (dict): kulud_kategooriate_kaupa() tulemus.
    """
    # TODO
    pass


# --- Beetaversiooni funktsioonid (alfaversioonis veel pole vaja) ---

def korduvad_kulud(tehingud):
    """Leia saajad, kellele on makstud vähemalt 3 korda, ja nende aastasumma.

    Tagastab sõnastiku: saaja -> (kordade arv, summa kokku, aastas ~)
    """
    # TODO beetaversioonis
    return {}


def ennusta_raha_loppu(tehingud, kontojaak, toetuse_kuupaev):
    """Ennusta keskmise päevakulu põhjal, mis kuupäeval raha otsa saab.

    Võrdle seda järgmise õppetoetuse kuupäevaga ja anna hoiatus.
    """
    # TODO beetaversioonis
    pass


def main():
    """Põhiprogramm: küsi failinimi ja näita menüüd."""
    print("=== Tudengi kulude analüüsija ===")
    failinimi = input("Sisesta faili nimi (nt test.csv): ")

    tehingud = loe_fail(failinimi)
    lisa_kategooriad(tehingud)
    print(f"Laetud {len(tehingud)} tehingut.")

    while True:
        print()
        print("1 – Kulud kategooriate kaupa")
        print("2 – Näita graafikut")
        print("0 – Välju")
        valik = input("Vali: ")

        if valik == "1":
            prindi_kulud(kulud_kategooriate_kaupa(tehingud))
        elif valik == "2":
            joonista_graafik(kulud_kategooriate_kaupa(tehingud))
        elif valik == "0":
            break
        else:
            print("Tundmatu valik, proovi uuesti.")


if __name__ == "__main__":
    main()