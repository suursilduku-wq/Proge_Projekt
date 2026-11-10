"""
Projekt:  Tudengi kulude analüüsija (alfaversioon)
Autorid:  Uku Suursild, Henry Martti Niin

Kirjeldus:
    Programm loeb Coop Panga CSV-väljavõtte, jagab kulud kategooriatesse
    ja prindib need tabelina.

Kasutatud allikad:
    - Pythoni csv-moodul: https://docs.python.org/3/library/csv.html
    - Tehisaru Claude (Anthropic): aitas koostada programmi struktuuri ja
      funktsioonid loe_fail ning leia_kaupmees. Märksõnad ja kategooriad
      valisime ise oma tehingute põhjal; koodi testisime ise.

Sisend:
    Coop Panga väljavõte CSV-failina (Konto väljavõte → eksport CSV).
    naidis_valjavote.csv on samas vormingus väljamõeldud andmetega näidis.
"""

import csv
from datetime import datetime


# Märksõna (väikeste tähtedega) -> kategooria. Järjekord on oluline:
# esimene sobiv märksõna võidab, seega "apteek" on enne "konsum".
MARKSONAD = {
    "apteek": "Tervis", "apte": "Tervis",
    "konsum": "Toit", "maksimark": "Toit", "rimi": "Toit",
    "selver": "Toit", "lidl": "Toit", "maxima": "Toit", "prisma": "Toit",
    "wolt": "Toidukuller", "bolt.eu/d": "Toidukuller",
    "bolt": "Transport", "elron": "Transport",
    "spotify": "Meelelahutus", "kino": "Meelelahutus",
    "moku": "Väljas käimine", "pahad poisid": "Väljas käimine",
    "kohvik": "Väljas käimine", "cafe": "Väljas käimine",
    "uhiselamu": "Elamine",
    "rahasahtlisse": "Säästmine",
}

KUUPAEVA_VORMING = "%d.%m.%Y"


def leia_kaupmees(selgitus):
    """Leia kaardimakse selgitusest poe nimi.

    Näide: "POS: 1111 22** **** 3333, 05.10.2026 14:01, UJULA KONSUM \\..."
    -> "UJULA KONSUM" (kolmas komaga osa, enne kaldkriipsu).
    """
    osad = selgitus.split(", ", 2)
    if len(osad) < 3:
        return selgitus.strip()
    return osad[2].split("\\")[0].strip()


def loe_fail(failinimi):
    """Loe Coop Panga väljavõte ja tagasta tehingute list sõnastikena.

    Tõstatab ValueError'i, kui fail pole Coop Panga vormingus.
    """
    tehingud = []
    with open(failinimi, encoding="utf-8-sig") as fail:
        lugeja = csv.DictReader(fail, delimiter=";")
        if "Saaja/maksja nimi" not in (lugeja.fieldnames or []):
            raise ValueError("See ei ole Coop Panga väljavõte.")
        for rida in lugeja:
            try:
                selgitus = rida["Selgitus"].strip()
                saaja = rida["Saaja/maksja nimi"].strip()
                # Kaardimaksel on saaja asemel kaardi number.
                if saaja.startswith("Kaart") or saaja == "":
                    saaja = leia_kaupmees(selgitus)
                tehingud.append({
                    "kuupaev": datetime.strptime(rida["Kuupäev"],
                                                 KUUPAEVA_VORMING),
                    "saaja": saaja,
                    "selgitus": selgitus,
                    "summa": float(rida["Summa"].replace(",", ".")),
                })
            except (ValueError, KeyError):
                continue  # vigane rida, jätame vahele
    return tehingud


def leia_kategooria(tekst):
    """Tagasta esimese tekstis leiduva märksõna kategooria või "Muu"."""
    tekst = tekst.lower()
    for markson, kategooria in MARKSONAD.items():
        if markson in tekst:
            return kategooria
    return "Muu"


def kulud_kategooriate_kaupa(tehingud):
    """Tagasta sõnastik kategooria -> kulude summa, suurimast väiksemani.

    Arvestatakse ainult kulusid (summa < 0); säästmine jäetakse välja.
    """
    kulud = {}
    for tehing in tehingud:
        if tehing["summa"] >= 0:
            continue
        kategooria = leia_kategooria(tehing["saaja"] + " "
                                     + tehing["selgitus"])
        if kategooria != "Säästmine":
            kulud[kategooria] = kulud.get(kategooria, 0) - tehing["summa"]
    return dict(sorted(kulud.items(), key=lambda x: x[1], reverse=True))


def euro(summa):
    """Vorminda summa eesti moodi, nt 23.4 -> '23,40 €'."""
    return f"{summa:.2f} €".replace(".", ",")


def prindi_kulud(kulud):
    """Prindi kulud tabelina: kategooria, summa ja protsent kogukulust."""
    kokku = sum(kulud.values())
    if kokku == 0:
        print("Kulusid ei leitud.")
        return
    for kategooria, summa in kulud.items():
        print(f"{kategooria:<16}{euro(summa):>12}{summa / kokku:>6.0%}")
    print("-" * 34)
    print(f"{'KOKKU':<16}{euro(kokku):>12}")


def main():
    """Küsi failinimi, loe väljavõte ja prindi kulud kategooriate kaupa."""
    print("=== Tudengi kulude analüüsija ===")
    print("Programm loeb Coop Panga CSV-väljavõtet.")
    while True:
        failinimi = input("Faili nimi (nt naidis_valjavote.csv): ").strip()
        try:
            tehingud = loe_fail(failinimi)
            break
        except FileNotFoundError:
            print("Faili ei leitud. Kas fail on programmiga samas kaustas?")
        except ValueError as viga:
            print(viga, "Laadi väljavõte alla Coop Panga internetipangast.")

    print(f"Laetud {len(tehingud)} tehingut.\n")
    prindi_kulud(kulud_kategooriate_kaupa(tehingud))


if __name__ == "__main__":
    main()
