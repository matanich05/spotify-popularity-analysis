import csv
import re

import requests
from bs4 import BeautifulSoup


url = "https://ca.billboard.com/charts/billboard-canadian-hot-100"
izhodna_dat = "data/html_billboard_hot_100.csv"
glave = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def pocisti_besedilo(bes):
    """Vrne besedilo brez odvečnih presledkov."""
    return " ".join(str(bes).split())


def shrani_csv(vrst):
    """Shrani Billboard Canadian Hot 100 podatke v csv datoteko."""
    if not vrst:
        return

    ime_stolpcev = list(vrst[0].keys())

    with open(izhodna_dat, "w", newline="", encoding="utf-8") as dat:
        wr = csv.DictWriter(dat, fieldnames=ime_stolpcev)
        wr.writeheader()
        wr.writerows(vrst)


def poisci_blok_lestvice(juha):
    """Vrne glavni del HTML strani za branje Billboard podatkov."""
    return juha


def vrstice_billboard(blok):
    """Vrne seznam podatkov o pesmih z Billboard Canadian Hot 100."""
    vrst = blok.get_text("\n", strip=True).splitlines()
    vrst = [pocisti_besedilo(el) for el in vrst]
    vrst = [el for el in vrst if el]

    zacetek = None
    konec = None

    for i, el in enumerate(vrst):
        if el == "THIS" and i + 9 < len(vrst):
            if (
                vrst[i + 1] == "WEEK"
                and vrst[i + 2] == "LAST"
                and vrst[i + 3] == "WEEK"
                and vrst[i + 4] == "PEAK"
                and vrst[i + 5] == "POS."
                and vrst[i + 6] == "WKS ON"
                and vrst[i + 7] == "CHART"
            ):
                zacetek = i + 8
                break

    if zacetek is None:
        return []

    for i in range(zacetek, len(vrst)):
        if "See Full CHART Here" in vrst[i]:
            konec = i
            break

        if re.fullmatch(r"[A-Za-z]+ \d{1,2}, \d{4}", vrst[i]):
            konec = i
            break

        if vrst[i] in ["advertisement", "About Us", "Privacy Policy"]:
            konec = i
            break

    if konec is None:
        konec = len(vrst)

    podatki = vrst[zacetek:konec]
    vrst = []
    i = 0

    while i + 5 < len(podatki):
        if not podatki[i].isdigit():
            i += 1
            continue

        rank = int(podatki[i])

        if rank < 1 or rank > 100:
            i += 1
            continue

        premik = 0
        if podatki[i + 1] == "New":
            premik = 1

        if i + 5 + premik >= len(podatki):
            break

        naslov_pesmi = podatki[i + 1 + premik]
        izvajalec = podatki[i + 2 + premik]
        last_week = podatki[i + 3 + premik]
        peak_pos = podatki[i + 4 + premik]
        weeks_on_chart = podatki[i + 5 + premik]

        vrst.append(
            {
                "rank": rank,
                "song_title": naslov_pesmi,
                "artist_name": izvajalec,
                "last_week": last_week,
                "peak_pos": peak_pos,
                "weeks_on_chart": weeks_on_chart,
            }
        )
        i += 6 + premik

    return vrst


def odstrani_podvojene(vrst):
    """Vrne seznam brez podvojenih pesmi na lestvici."""
    nove_vrst = []
    videni = set()

    for vrstica in vrst:
        kljuc = (vrstica["rank"], vrstica["song_title"], vrstica["artist_name"])
        if kljuc in videni:
            continue

        nove_vrst.append(vrstica)
        videni.add(kljuc)

    return nove_vrst


def glavni():
    """Shrani Billboard Canadian Hot 100 podatke v csv."""
    odg = requests.get(url, headers=glave, timeout=20)
    odg.raise_for_status()

    juha = BeautifulSoup(odg.text, "html.parser")
    blok = poisci_blok_lestvice(juha)

    if blok is None:
        return

    vrst = vrstice_billboard(blok)
    vrst = odstrani_podvojene(vrst)

    if not vrst:
        return

    shrani_csv(vrst)


if __name__ == "__main__":
    glavni()
