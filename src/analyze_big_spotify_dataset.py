import os

import matplotlib.pyplot as plt
import pandas as pd


VHODNA_DAT = "data/spotify-tracks-dataset-detailed.csv"
IZHODNA_DAT = "data/spotify_analysis_clean.csv"
MAPA_REZ = "results"

DAT_HIST = "results/big_popularity_histogram.png"
DAT_ZANR = "results/top_genres_by_average_popularity.png"
DAT_KOR = "results/popularity_correlations.png"


STEV_STOLPCI = [
    "popularity",
    "duration_ms",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo"
]


ANALIZNE_LASTNOSTI = [
    "duration_min",
    "danceability",
    "energy",
    "tempo"
]


OZNAKE_LAST = {
    "duration_min": "Dolžina pesmi",
    "danceability": "Plesnost",
    "energy": "Energičnost",
    "tempo": "Tempo"
}


def doloci_skupino_zanra(zanr):
    """Vrne sirso glasbeno skupino za podani zanr."""
    zanr = str(zanr).lower()

    if "classical" in zanr or "opera" in zanr or "piano" in zanr:
        return "Klasična glasba"
    if "reggae" in zanr or "dub" in zanr:
        return "Reggae"
    if "jazz" in zanr or "blues" in zanr:
        return "Jazz in blues"
    if "hip-hop" in zanr or "rap" in zanr or "trap" in zanr:
        return "Hip-hop in rap"
    if "rock" in zanr or "punk" in zanr or "grunge" in zanr or "emo" in zanr:
        return "Rock"
    if "metal" in zanr or "hardcore" in zanr:
        return "Metal"
    if "pop" in zanr or "k-pop" in zanr:
        return "Pop"
    if "reggaeton" in zanr or "latin" in zanr or "salsa" in zanr:
        return "Latino"
    if "electro" in zanr or "edm" in zanr or "house" in zanr or "techno" in zanr or "trance" in zanr:
        return "Elektronska glasba"
    if "country" in zanr or "folk" in zanr or "acoustic" in zanr or "singer-songwriter" in zanr:
        return "Country in folk"

    return "Drugo"


def nalozi_in_pocisti_podatke():
    """Vrne ocisceno tabelo velikega Spotify dataseta."""
    tab = pd.read_csv(VHODNA_DAT)
    tab = tab.drop_duplicates()
    tab = tab.dropna(subset=["popularity", "track_genre"])

    for ime_st in STEV_STOLPCI:
        tab[ime_st] = pd.to_numeric(tab[ime_st], errors="coerce")

    tab = tab.dropna(subset=STEV_STOLPCI)
    tab["main_artist"] = tab["artists"].fillna("").apply(
        lambda bes: str(bes).split(";")[0].strip() if str(bes) else ""
    )
    tab["duration_min"] = tab["duration_ms"] / 60000
    tab["genre_group"] = tab["track_genre"].apply(doloci_skupino_zanra)

    return tab


def izpisi_osnovne_podatke(tab):
    """Vrne None in izpise osnovni pregled velikega Spotify dataseta."""
    print("Osnovni pregled velikega Spotify dataseta")
    print("----------------------------------------")
    print("Število pesmi:", len(tab))
    print("Število izvajalcev:", tab["artists"].nunique())
    print("Število žanrov:", tab["track_genre"].nunique())
    print("Povprečna popularnost:", round(tab["popularity"].mean(), 2))
    print("Mediana popularnosti:", round(tab["popularity"].median(), 2))
    print("Najmanjša popularnost:", int(tab["popularity"].min()))
    print("Največja popularnost:", int(tab["popularity"].max()))
    print()


def izpisi_skupine_zanrov(tab):
    """Vrne None in izpise povprecno popularnost po sirsih skupinah zanrov."""
    skup = (
        tab[tab["genre_group"] != "Drugo"]
        .groupby("genre_group")["popularity"]
        .mean()
        .sort_values(ascending=False)
    )

    print("Povprečna popularnost po večjih glasbenih skupinah")
    print("--------------------------------------------------")
    for ime_sk, vred in skup.items():
        print(f"{ime_sk}: {round(vred, 2)}")
    print()


def izracunaj_in_izpisi_korelacije(tab):
    """Vrne serijo korelacij med lastnostmi pesmi in popularnostjo."""
    stolpci = ["popularity"] + ANALIZNE_LASTNOSTI

    kor = tab[stolpci].corr()["popularity"].drop("popularity")
    kor = kor.sort_values(key=lambda vred: vred.abs(), ascending=False)

    print("Korelacije s popularnostjo")
    print("--------------------------")
    for ime_st, vred in kor.items():
        print(f"{OZNAKE_LAST[ime_st]}: {round(vred, 3)}")
    print()

    return kor


def ustvari_histogram_popularnosti(tab):
    """Vrne None in shrani histogram popularnosti pesmi."""
    plt.figure(figsize=(8, 5))
    plt.hist(tab["popularity"], bins=20, edgecolor="black", color="steelblue")
    plt.title("Porazdelitev popularnosti pesmi")
    plt.xlabel("Popularnost")
    plt.ylabel("Število pesmi")
    plt.tight_layout()
    plt.savefig(DAT_HIST)
    plt.close()


def ustvari_graf_skupin_zanrov(tab):
    """Vrne None in shrani graf povprecne popularnosti po skupinah zanrov."""
    skup = (
        tab[tab["genre_group"] != "Drugo"]
        .groupby("genre_group")["popularity"]
        .mean()
        .sort_values()
    )

    plt.figure(figsize=(10, 5))
    plt.barh(skup.index, skup.values, color="teal")
    plt.title("Povprečna popularnost po večjih glasbenih skupinah")
    plt.xlabel("Povprečna popularnost")
    plt.ylabel("Glasbena skupina")
    plt.tight_layout()
    plt.savefig(DAT_ZANR)
    plt.close()


def ustvari_graf_korelacij(kor):
    """Vrne None in shrani graf korelacij lastnosti s popularnostjo."""
    kor_urej = kor.sort_values()
    oznake = [OZNAKE_LAST[ime_st] for ime_st in kor_urej.index]
    barve = ["indianred" if vred < 0 else "seagreen" for vred in kor_urej.values]

    plt.figure(figsize=(10, 6))
    plt.barh(oznake, kor_urej.values, color=barve)
    plt.axvline(0, color="black", linewidth=1)
    plt.title("Povezanost lastnosti pesmi s popularnostjo")
    plt.xlabel("Korelacija")
    plt.ylabel("Lastnost pesmi")
    plt.tight_layout()
    plt.savefig(DAT_KOR)
    plt.close()


def glavni_program():
    """Vrne None in pripravi glavno analizo velikega Spotify dataseta."""
    os.makedirs(MAPA_REZ, exist_ok=True)

    tab = nalozi_in_pocisti_podatke()
    tab.to_csv(IZHODNA_DAT, index=False)

    izpisi_osnovne_podatke(tab)
    izpisi_skupine_zanrov(tab)
    kor = izracunaj_in_izpisi_korelacije(tab)

    ustvari_histogram_popularnosti(tab)
    ustvari_graf_skupin_zanrov(tab)
    ustvari_graf_korelacij(kor)

    print("Shranjene datoteke")
    print("------------------")
    print(IZHODNA_DAT)
    print(DAT_HIST)
    print(DAT_ZANR)
    print(DAT_KOR)


if __name__ == "__main__":
    glavni_program()
