import os

import matplotlib.pyplot as plt
import pandas as pd


vhodna_dat = "data/spotify-tracks-dataset-detailed.csv"
izhodna_dat = "data/spotify_analysis_clean.csv"
rez_mapa = "results"

dat_histogram = "results/big_popularity_histogram.png"
dat_zanr = "results/top_genres_by_average_popularity.png"
dat_korelacije = "results/popularity_correlations.png"

st_stolpci = ["popularity", "duration_ms", "danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
analiza_lastnosti = ["duration_min", "danceability", "energy", "tempo"]
oznake_lastnosti = {"duration_min": "Dolžina pesmi", "danceability": "Plesnost", "energy": "Energičnost", "tempo": "Tempo"}

def skupina_zanra(zanr):
    """Vrne skupino za žanr."""
    zanr = str(zanr).lower().strip()

    if zanr in ["pop", "power-pop", "indie-pop", "synth-pop", "k-pop", "j-pop", "cantopop", "mandopop", "pop-film", "j-idol"]:
        return "Pop"
    if zanr in ["rock", "alt-rock", "alternative", "hard-rock", "psych-rock", "rockabilly", "rock-n-roll", "indie", "j-rock", "british"]:
        return "Rock"
    if zanr in ["punk", "punk-rock", "emo", "grunge"]:
        return "Punk"
    if zanr in ["metal", "heavy-metal", "black-metal", "death-metal", "metalcore", "grindcore", "hardcore", "groove", "goth", "industrial"]:
        return "Metal"
    if zanr in ["hip-hop", "trip-hop", "r-n-b"]:
        return "Hip-hop, rap in R&B"
    if zanr in [
        "electro", "electronic", "edm", "house", "deep-house", "progressive-house",
        "chicago-house", "techno", "detroit-techno", "minimal-techno", "trance",
        "breakbeat", "drum-and-bass", "dubstep", "idm", "garage", "club",
        "dance", "hardstyle", "j-dance", "party",
    ]:
        return "Elektronska glasba"
    if zanr in ["reggae", "dub", "ska", "dancehall"]:
        return "Reggae"
    if zanr in ["latin", "latino", "reggaeton", "salsa", "samba", "tango", "brazil", "mpb", "pagode", "forro", "sertanejo", "spanish"]:
        return "Latino glasba"
    if zanr in ["country", "folk", "acoustic", "bluegrass", "honky-tonk", "singer-songwriter", "songwriter", "guitar"]:
        return "Country in folk"
    if zanr in ["jazz", "blues", "soul", "funk", "disco", "gospel"]:
        return "Jazz, blues, soul in funk"
    if zanr in ["classical", "opera", "piano", "new-age"]:
        return "Klasična in instrumentalna glasba"
    if zanr in ["ambient", "chill", "sleep", "study", "sad", "happy", "romance"]:
        return "Ambientalna glasba"
    if zanr in ["children", "kids", "disney", "show-tunes", "anime"]:
        return "Otroška, filmska in odrska glasba"
    if zanr in ["afrobeat"]:
        return "Afriška glasba"
    if zanr in ["french", "german", "swedish"]:
        return "Evropska glasba"
    if zanr in ["indian", "iranian", "turkish", "malay", "world-music"]:
        return "Azijska glasba"

    return "Drugo"


def pocisti_podatke():
    """Vrne očiščene podatke."""
    tab = pd.read_csv(vhodna_dat)
    tab = tab.drop_duplicates()
    tab = tab.dropna(subset=["popularity", "track_genre"])

    for ime_st in st_stolpci:
        tab[ime_st] = pd.to_numeric(tab[ime_st], errors="coerce")

    tab = tab.dropna(subset=st_stolpci)
    tab["main_artist"] = tab["artists"].fillna("").apply(
        lambda bes: str(bes).split(";")[0].strip() if str(bes) else ""
    )
    tab["duration_min"] = tab["duration_ms"] / 60000
    tab["genre_group"] = tab["track_genre"].apply(skupina_zanra)

    return tab


def izracun_korelacij(tab):
    """Vrne korelacije s popularnostjo."""
    stolpci = ["popularity"] + analiza_lastnosti
    kor = tab[stolpci].corr()["popularity"].drop("popularity")
    kor = kor.sort_values(key=lambda vred: vred.abs(), ascending=False)
    return kor


def graf_popularnosti(tab):
    """Shrani histogram popularnosti."""
    plt.figure(figsize=(8, 5))
    plt.hist(tab["popularity"], bins=20, edgecolor="black", color="steelblue")
    plt.title("Porazdelitev popularnosti pesmi")
    plt.xlabel("Popularnost")
    plt.ylabel("Število pesmi")
    plt.tight_layout()
    plt.savefig(dat_histogram)
    plt.close()


def graf_zanri(tab):
    """Shrani graf po skupinah žanrov."""
    skup = (
        tab[(tab["genre_group"] != "Drugo") & (tab["track_genre"] != "comedy")]
        .groupby("genre_group")["popularity"]
        .mean()
        .sort_values()
    )

    plt.figure(figsize=(10, 6))
    plt.barh(skup.index, skup.values, color="teal")
    plt.title("Povprečna popularnost po večjih glasbenih skupinah")
    plt.xlabel("Povprečna popularnost")
    plt.ylabel("Glasbena skupina")
    plt.tight_layout()
    plt.savefig(dat_zanr)
    plt.close()


def graf_korelacije(kor):
    """Shrani graf korelacij."""
    kor_urej = kor.sort_values()
    oznake = [oznake_lastnosti[ime_st] for ime_st in kor_urej.index]
    barve = ["indianred" if vred < 0 else "seagreen" for vred in kor_urej.values]

    plt.figure(figsize=(10, 6))
    plt.barh(oznake, kor_urej.values, color=barve)
    plt.axvline(0, color="black", linewidth=1)
    plt.title("Povezanost lastnosti pesmi s popularnostjo")
    plt.xlabel("Korelacija")
    plt.ylabel("Lastnost pesmi")
    plt.tight_layout()
    plt.savefig(dat_korelacije)
    plt.close()


def glavni():
    """Naredi glavno Spotify analizo."""
    os.makedirs(rez_mapa, exist_ok=True)
    tab = pocisti_podatke()
    tab.to_csv(izhodna_dat, index=False)
    kor = izracun_korelacij(tab)
    graf_popularnosti(tab)
    graf_zanri(tab)
    graf_korelacije(kor)


if __name__ == "__main__":
    glavni()
