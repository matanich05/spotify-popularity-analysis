import csv
import time
import pandas as pd
import requests

api_key = "e43edfad49094009e575a0618a58673f"
url = "http://ws.audioscrobbler.com/2.0/"
vhodna_dat = "data/spotify_analysis_clean.csv"
izhodna_dat = "data/lastfm_big_artists.csv"
min_st_pesmi = 15
meja_izvajalcev = 300
cas = 0.25

def izvajalci():
    """Vrne seznam najbolj pomembnih izvajalcev iz velikega Spotify dataseta."""

    tab = pd.read_csv(vhodna_dat)
    if "main_artist" not in tab.columns:
        tab["main_artist"] = tab["artists"].fillna("").apply(
            lambda besedilo: str(besedilo).split(";")[0].strip() if str(besedilo) else ""
        )
    povzetek = (
        tab.groupby("main_artist")
        .agg(
            stevilo_pesmi=("track_id", "count"),
            povprecna_popularnost=("popularity", "mean")
        )
        .reset_index()
    )
    povzetek = povzetek[povzetek["stevilo_pesmi"] >= min_st_pesmi]
    povzetek = povzetek.sort_values(
        ["povprecna_popularnost", "stevilo_pesmi"],
        ascending=[False, False]
    ).head(meja_izvajalcev)

    return povzetek["main_artist"].tolist()

def podatki_izvajalec(ime_izvajalca):
    """Vrne slovar z Last.fm podatki o enem izvajalcu."""

    parametri = {
        "method": "artist.getinfo",
        "artist": ime_izvajalca,
        "api_key": api_key,
        "format": "json",
        "autocorrect": 1
    }
    odg = requests.get(url, params=parametri, timeout=20)
    podatki = odg.json()
    time.sleep(cas)
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
    stat = izvajalec.get("stats", {})
    oznake = izvajalec.get("tags", {}).get("tag", [])

    ime_oznak = []
    for el in oznake[:5]:
        ime_oznake = el.get("name", "")
        if ime_oznake:
            ime_oznak.append(ime_oznake)

    return {
        "artist_name": izvajalec.get("name", ime_izvajalca),
        "listeners": stat.get("listeners", ""),
        "playcount": stat.get("playcount", ""),
        "tags": ", ".join(ime_oznak),
        "url": izvajalec.get("url", ""),
        "found": "True"
    }


def shrani_csv(vrst):
    """Shrani Last.fm podatke v csv datoteko."""

    if not vrst:
        return
    ime_stolpcev = list(vrst[0].keys())

    with open(izhodna_dat, "w", newline="", encoding="utf-8") as datoteka:
        wr = csv.DictWriter(datoteka, fieldnames=ime_stolpcev)
        wr.writeheader()
        wr.writerows(vrst)


def glavni():
    """Shrani Last.fm podatke za izbrane izvajalce iz urejenega dataseta"""

    izbrani = izvajalci()
    vrst = []
    for ime_izvajalca in izbrani:
        vrst.append(podatki_izvajalec(ime_izvajalca))
    shrani_csv(vrst)


if __name__ == "__main__":
    glavni()
