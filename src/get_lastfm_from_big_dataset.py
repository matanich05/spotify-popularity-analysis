import csv
import time

import pandas as pd
import requests


API_KLJUC = "e43edfad49094009e575a0618a58673f"
OSNOVNI_URL = "http://ws.audioscrobbler.com/2.0/"
VHODNA_DATOTEKA = "data/spotify_analysis_clean.csv"
IZHODNA_DATOTEKA = "data/lastfm_big_artists.csv"
MIN_STEVILO_PESMI = 15
MEJA_IZVAJALCEV = 120
CAS_CAKANJA = 0.25


def izberi_izvajalce():
    """Vrne seznam najbolj pomembnih izvajalcev iz velikega Spotify dataseta."""
    tabela = pd.read_csv(VHODNA_DATOTEKA)

    if "main_artist" not in tabela.columns:
        tabela["main_artist"] = tabela["artists"].fillna("").apply(
            lambda besedilo: str(besedilo).split(";")[0].strip() if str(besedilo) else ""
        )

    povzetek = (
        tabela.groupby("main_artist")
        .agg(
            stevilo_pesmi=("track_id", "count"),
            povprecna_popularnost=("popularity", "mean")
        )
        .reset_index()
    )

    povzetek = povzetek[povzetek["stevilo_pesmi"] >= MIN_STEVILO_PESMI]
    povzetek = povzetek.sort_values(
        ["povprecna_popularnost", "stevilo_pesmi"],
        ascending=[False, False]
    ).head(MEJA_IZVAJALCEV)

    return povzetek["main_artist"].tolist()


def pridobi_podatke_o_izvajalcu(ime_izvajalca):
    """Vrne slovar z Last.fm podatki o enem izvajalcu."""
    parametri = {
        "method": "artist.getinfo",
        "artist": ime_izvajalca,
        "api_key": API_KLJUC,
        "format": "json",
        "autocorrect": 1
    }

    odgovor = requests.get(OSNOVNI_URL, params=parametri, timeout=20)
    podatki = odgovor.json()
    time.sleep(CAS_CAKANJA)

    if "error" in podatki:
        return {
            "artist_name": ime_izvajalca,
            "listeners": "",
            "playcount": "",
            "tags": "",
            "url": "",
            "found": "False"
        }

    izvajalec = podatki["artist"]
    statistika = izvajalec.get("stats", {})
    oznake = izvajalec.get("tags", {}).get("tag", [])

    imena_oznak = []
    for oznaka in oznake[:5]:
        ime_oznake = oznaka.get("name", "")
        if ime_oznake:
            imena_oznak.append(ime_oznake)

    return {
        "artist_name": izvajalec.get("name", ime_izvajalca),
        "listeners": statistika.get("listeners", ""),
        "playcount": statistika.get("playcount", ""),
        "tags": ", ".join(imena_oznak),
        "url": izvajalec.get("url", ""),
        "found": "True"
    }


def shrani_v_csv(vrstice):
    """Vrne None in shrani velike Last.fm podatke v CSV datoteko."""
    if not vrstice:
        print("Ni podatkov za shranjevanje.")
        return

    imena_stolpcev = list(vrstice[0].keys())

    with open(IZHODNA_DATOTEKA, "w", newline="", encoding="utf-8") as datoteka:
        pisec = csv.DictWriter(datoteka, fieldnames=imena_stolpcev)
        pisec.writeheader()
        pisec.writerows(vrstice)


def glavni_program():
    """Vrne None in shrani Last.fm podatke za pomembne izvajalce iz velikega dataseta."""
    izbrani_izvajalci = izberi_izvajalce()
    vrstice = []

    print("Stevilo izbranih izvajalcev:", len(izbrani_izvajalci))
    print()

    for ime_izvajalca in izbrani_izvajalci:
        print("Obdelujem izvajalca:", ime_izvajalca)
        vrstice.append(pridobi_podatke_o_izvajalcu(ime_izvajalca))

    shrani_v_csv(vrstice)

    print()
    print(f"Podatki so shranjeni v: {IZHODNA_DATOTEKA}")


if __name__ == "__main__":
    glavni_program()
