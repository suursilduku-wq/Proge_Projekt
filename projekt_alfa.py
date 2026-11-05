"""
Projekt:  Tudengi kulude analüüsija (alfaversioon)
Autorid:  Uku Suursild, Henry Martti Niin

Kirjeldus:
    Programm loeb Coop Panga internetipangast alla laaditud
    CSV-väljavõtte, jagab kulud
    kategooriatesse ning näitab neid tabeli ja graafikuna.
    Beetaversioonis lisanduvad korduvate kulude leidmine ja ennustus,
    millal raha enne järgmist õppetoetust otsa saab.

Kasutatud allikad:
    - matplotlib dokumentatsioon: https://matplotlib.org/stable/
    - Pythoni csv-moodul: https://docs.python.org/3/library/csv.html
    - Pythoni datetime-moodul: https://docs.python.org/3/library/datetime.html
    - Koodi kirjutamisel kasutati tehisintellekti Claude (Anthropic) abi.

Käivitamine:
    python kulude_analuusija.py
    (vajab teeki matplotlib: pip install matplotlib)

Sisend:
    Coop Panga väljavõte CSV-failina (Konto väljavõte → eksport CSV).
    Fail test.csv on samas vormingus väljamõeldud andmetega näidis.
"""

import csv
from datetime import datetime

import matplotlib.pyplot as plt


# Märksõnad, mille järgi tehing kategooriasse pannakse.
# Võti = märksõna saaja nimes (väikeste tähtedega), väärtus = kategooria.
# NB! Järjekord on oluline: kontrollitakse ülevalt alla ja esimene sobiv
# märksõna võidab. Seepärast on "apteek" enne "konsum" ja "rimi"
# (muidu läheks "UJULA KONSUMI APTEEK" toidu alla).
MARKSONAD = {
    "apteek": "Tervis",
    "apte": "Tervis",
    "konsum": "Toit",
    "maksimarket": "Toit",
    "maksimark": "Toit",
    "coop eesti": "Toit",
    "rimi": "Toit",
    "selver": "Toit",
    "lidl": "Toit",
    "maxima": "Toit",
    "prisma": "Toit",
    "herne kauplus": "Toit",
    "circle k": "Toit",
    "wolt": "Toidukuller",
    "mysushi": "Toidukuller",
    "bolt.eu/d": "Toidukuller",
    "bolt food": "Toidukuller",
    "bolt": "Transport",
    "elron": "Transport",
    "spotify": "Meelelahutus",
    "netflix": "Meelelahutus",
    "kino": "Meelelahutus",
    "piletitasku": "Meelelahutus",
    "olybet": "Meelelahutus",
    "moku": "Väljas käimine",
    "pyhaste": "Väljas käimine",
    "pahad poisid": "Väljas käimine",
    "kohvik": "Väljas käimine",
    "kraba": "Väljas käimine",
    "cafe": "Väljas käimine",
    "genklubi": "Väljas käimine",
    "zavood": "Väljas käimine",
    "kaubamaja": "Ostlemine",
    "charlot": "Ostlemine",
    "jahipaun": "Hobid",
    "anthropic": "Tellimused",
    "lightyear": "Investeerimine",
    "uhiselamu": "Elamine",
    "rahasahtlisse": "Säästmine",
}

# Kategooriad, mis ei ole päris kulutused (raha liigub sinu enda
# säästudesse või investeeringutesse). Neid kulude tabelis ei näidata.
MITTE_KULUD = {"Säästmine"}

KUUPAEVA_VORMING = "%d.%m.%Y"


def leia_kaupmees(selgitus):
    """Leia kaardimakse selgitusest poe või teenuse nimi.

    Coop Panga kaardimakse selgitus on kujul
    "POS: 5374 87** **** 2504, 05.10.2026 14:01:59, UJULA KONSUM   \\UJULA 2..."
    Poe nimi on kolmas komaga eraldatud osa, enne esimest kaldkriipsu.

    Näide: -> "UJULA KONSUM"

    Argumendid:
        selgitus (str): tehingu selgitus.

    Tagastab:
        str: poe nimi või kogu selgitus, kui seda ei õnnestu eraldada.
    """
    osad = selgitus.split(", ", 2)
    if len(osad) < 3:
        return selgitus.strip()
    return osad[2].split("\\")[0].strip()


def loe_fail(failinimi):
    """Loe pangaväljavõte CSV-failist ja tagasta tehingute list.

    Programm toetab ainult Coop Panga väljavõtet (eraldaja semikoolon,
    veerud "Kuupäev", "Saaja/maksja nimi", "Summa", "Selgitus" jne).

    Iga tehing on sõnastik kujul
    {"kuupaev": date, "saaja": str, "selgitus": str, "summa": float}.
    Vigased read jäetakse vahele.

    Argumendid:
        failinimi (str): CSV-faili nimi.

    Tagastab:
        list: tehingute sõnastikud kuupäeva järgi sorteerituna.

    Tõstatab:
        ValueError: kui fail ei ole Coop Panga väljavõtte vormingus.
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
                # Kaardimaksel on saaja asemel kaardi number,
                # päris poe nimi on selgituses.
                if saaja.startswith("Kaart") or saaja == "":
                    saaja = leia_kaupmees(selgitus)
                kuupaev = datetime.strptime(rida["Kuupäev"].strip(),
                                            KUUPAEVA_VORMING).date()
                summa = float(rida["Summa"].replace(",", ".").strip())
            except (ValueError, KeyError, AttributeError):
                continue  # vigane rida, jätame vahele

            tehingud.append({
                "kuupaev": kuupaev,
                "saaja": saaja,
                "selgitus": selgitus,
                "summa": summa,
            })
    tehingud.sort(key=lambda t: t["kuupaev"])
    return tehingud


def leia_kategooria(saaja):
    """Leia saaja nime järgi tehingu kategooria.

    Näide: leia_kategooria("RIMI EESTI FOOD") -> "Toit"

    Argumendid:
        saaja (str): saaja nimi väljavõttest.

    Tagastab:
        str: kategooria nimi või "Muu", kui märksõna ei leitud.
    """
    saaja_vaike = saaja.lower()
    for markson, kategooria in MARKSONAD.items():
        if markson in saaja_vaike:
            return kategooria
    return "Muu"


def lisa_kategooriad(tehingud):
    """Lisa igale tehingule võti "kategooria".

    Sissetulekud (summa > 0) saavad kategooriaks "Sissetulek".

    Argumendid:
        tehingud (list): loe_fail() tagastatud list.
    """
    for tehing in tehingud:
        if tehing["summa"] > 0:
            tehing["kategooria"] = "Sissetulek"
        else:
            # Otsime märksõna nii saaja nimest kui ka selgitusest.
            tekst = tehing["saaja"] + " " + tehing["selgitus"]
            tehing["kategooria"] = leia_kategooria(tekst)


def kulud_kategooriate_kaupa(tehingud):
    """Arvuta iga kategooria kulude kogusumma positiivse arvuna.

    Argumendid:
        tehingud (list): kategooriatega tehingud.

    Tagastab:
        dict: kategooria -> kogusumma eurodes, suurimast väiksemani.
    """
    kulud = {}
    for tehing in tehingud:
        if tehing["summa"] < 0 and tehing["kategooria"] not in MITTE_KULUD:
            kategooria = tehing["kategooria"]
            kulud[kategooria] = kulud.get(kategooria, 0) - tehing["summa"]
    return dict(sorted(kulud.items(), key=lambda x: x[1], reverse=True))


def euro(summa):
    """Vorminda summa eesti moodi, nt 23.4 -> '23,40 €'."""
    return f"{summa:.2f} €".replace(".", ",")


def prindi_kulud(kulud):
    """Prindi kulud tabelina: kategooria, summa ja protsent kogukulust.

    Argumendid:
        kulud (dict): kulud_kategooriate_kaupa() tulemus.
    """
    kokku = sum(kulud.values())
    if kokku == 0:
        print("Kulusid ei leitud.")
        return
    print()
    for kategooria, summa in kulud.items():
        protsent = summa / kokku * 100
        print(f"{kategooria:<16}{euro(summa):>12}{protsent:>6.0f}%")
    print("-" * 34)
    print(f"{'KOKKU':<16}{euro(kokku):>12}")


def joonista_graafik(kulud):
    """Joonista kulude tulp- ja sektordiagramm kõrvuti ühte aknasse.

    Argumendid:
        kulud (dict): kulud_kategooriate_kaupa() tulemus.
    """
    if not kulud:
        print("Kulusid ei leitud, graafikut pole võimalik joonistada.")
        return
    nimed = list(kulud.keys())
    summad = list(kulud.values())

    joonis, (tulbad, sektor) = plt.subplots(1, 2, figsize=(12, 5))

    tulbad.bar(nimed, summad, color="#4C72B0")
    tulbad.set_title("Kulud kategooriate kaupa")
    tulbad.set_ylabel("Eurot")
    tulbad.tick_params(axis="x", rotation=30)
    for i, summa in enumerate(summad):
        tulbad.text(i, summa, euro(summa), ha="center", va="bottom")

    sektor.pie(summad, labels=nimed, autopct="%1.0f%%", startangle=90)
    sektor.set_title("Kulude osakaal")

    joonis.tight_layout()
    plt.show()


def saastetud_kokku(tehingud):
    """Tagasta, kui palju raha on perioodi jooksul säästudesse kantud."""
    kokku = 0
    for tehing in tehingud:
        if tehing["kategooria"] == "Säästmine":
            kokku -= tehing["summa"]
    return kokku


def main():
    """Põhiprogramm: loe fail ja näita menüüd, kuni kasutaja väljub."""
    print("=== Tudengi kulude analüüsija ===")
    print("Programm loeb Coop Panga internetipangast alla laaditud")
    print("CSV-väljavõtet (Konto väljavõte → eksport CSV).")
    print("Proovimiseks võid kasutada ka faili test.csv.")
    print()
    while True:
        failinimi = input("Sisesta faili nimi (nt test.csv): ").strip()
        try:
            tehingud = loe_fail(failinimi)
            break
        except FileNotFoundError:
            print("Faili ei leitud. Kontrolli, et fail on programmiga "
                  "samas kaustas.")
        except ValueError as viga:
            print(f"{viga} Laadi alla väljavõte Coop Panga "
                  "internetipangast CSV-vormingus.")

    lisa_kategooriad(tehingud)
    if tehingud:
        algus = tehingud[0]["kuupaev"].strftime(KUUPAEVA_VORMING)
        lopp = tehingud[-1]["kuupaev"].strftime(KUUPAEVA_VORMING)
        print(f"Laetud {len(tehingud)} tehingut ({algus}–{lopp}).")
    else:
        print("Failist ei leitud ühtegi tehingut.")

    while True:
        print()
        print("1 – Kulud kategooriate kaupa")
        print("2 – Näita graafikut")
        print("0 – Välju")
        valik = input("Vali: ").strip()

        if valik == "1":
            prindi_kulud(kulud_kategooriate_kaupa(tehingud))
            saastetud = saastetud_kokku(tehingud)
            if saastetud > 0:
                print(f"\nLisaks kantud säästudesse: {euro(saastetud)}")
        elif valik == "2":
            joonista_graafik(kulud_kategooriate_kaupa(tehingud))
        elif valik == "0":
            print("Head aega!")
            break
        else:
            print("Tundmatu valik, proovi uuesti.")


if __name__ == "__main__":
    main()
