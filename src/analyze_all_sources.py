import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SPOTIFY_GL_DAT = "data/spotify_analysis_clean.csv"
LASTFM_DAT = "data/lastfm_big_artists.csv"
SPOTIFY_API_DAT = "data/spotify_api_sample.csv"
SPOTIFY_MALA_DAT = "data/spotify_tracks.csv"
HTML_DAT = "data/html_best_selling_artists.csv"

IZHOD_IZV_DAT = "data/all_sources_artist_summary.csv"
IZHOD_PES_DAT = "data/all_sources_track_sample.csv"

MAPA_REZ = "results"
DAT_LASTFM_GRAF = "results/artist_popularity_vs_lastfm_listeners.png"
DAT_LASTFM_OZN = "results/artist_popularity_vs_lastfm_listeners_top_labeled.png"
DAT_SPOTIFY_API_GRAF = "results/csv_vs_spotify_api_popularity.png"

ROCNI_ODMIKI = {
    "Ariana Grande": (6, 8),
    "Bad Bunny": (6, 8),
    "LISA": (-20, 8),
    "Labrinth": (8, 10),
    "The Neighbourhood": (-18, -10),
    "System Of A Down": (-22, 12),
    "Frank Ocean": (-24, -10),
    "Radiohead": (8, -8),
    "George Ezra": (10, 10),
    "Stray Kids": (-24, 8),
    "Maluma": (8, -10),
    "TWICE": (8, -12),
    "BLACKPINK": (8, 10),
    "The 1975": (10, 6),
    "Halsey": (-18, -10),
    "John Denver": (-24, 8),
    "Eagles": (8, 8),
    "Calvin Harris": (8, -4),
    "AC/DC": (8, -2),
    "Aerosmith": (12, -14),
    "Foo Fighters": (10, 6),
    "Metallica": (10, -12),
    "AP Dhillon": (-22, -8),
    "Farruko": (-20, 8),
    "Lil Tjay": (-22, 10),
}


def normaliziraj_ime(bes):
    """Vrne poenoteno ime izvajalca za lazje povezovanje virov."""
    if pd.isna(bes):
        return ""

    bes = str(bes).lower().strip()
    bes = bes.replace("&", "and")
    bes = bes.replace("â€™", "'")
    return " ".join(bes.split())


def nalozi_glavne_podatke():
    """Vrne glavno Spotify tabelo z dodatnimi stolpci za analizo."""
    tab = pd.read_csv(SPOTIFY_GL_DAT)

    if "main_artist" not in tab.columns:
        tab["main_artist"] = tab["artists"].fillna("").apply(
            lambda bes: str(bes).split(";")[0].strip() if str(bes) else ""
        )

    tab["artist_key"] = tab["main_artist"].apply(normaliziraj_ime)
    tab["duration_min"] = tab["duration_ms"] / 60000
    return tab


def zgradi_povzetek_izvajalcev(tab):
    """Vrne povzetek po izvajalcih za glavni Spotify dataset."""
    return (
        tab.groupby(["artist_key", "main_artist"])
        .agg(
            track_count=("track_id", "count"),
            avg_popularity=("popularity", "mean"),
            median_popularity=("popularity", "median"),
            avg_danceability=("danceability", "mean"),
            avg_energy=("energy", "mean"),
            avg_duration_min=("duration_min", "mean")
        )
        .reset_index()
    )


def nalozi_lastfm_podatke():
    """Vrne Last.fm tabelo s pretvorjenimi stevilskimi stolpci."""
    tab = pd.read_csv(LASTFM_DAT)
    tab["artist_key"] = tab["artist_name"].apply(normaliziraj_ime)
    tab["listeners"] = pd.to_numeric(tab["listeners"], errors="coerce")
    tab["playcount"] = pd.to_numeric(tab["playcount"], errors="coerce")
    return tab


def nalozi_html_podatke():
    """Vrne HTML tabelo z oznako, ali je izvajalec med best-selling izvajalci."""
    if not os.path.exists(HTML_DAT):
        return pd.DataFrame(columns=[
            "artist_name", "claimed_sales", "period_active",
            "genre", "country", "artist_key", "in_html_best_selling"
        ])

    tab = pd.read_csv(HTML_DAT)
    tab["artist_key"] = tab["artist_name"].apply(normaliziraj_ime)
    tab["in_html_best_selling"] = True
    return tab


def nalozi_velik_spotify_api_vzorec():
    """Vrne tabelo velikega Spotify API vzorca, ce ta obstaja."""
    if not os.path.exists(SPOTIFY_API_DAT):
        return pd.DataFrame(columns=["track_id", "api_popularity", "source"])

    tab = pd.read_csv(SPOTIFY_API_DAT)
    tab["api_popularity"] = pd.to_numeric(tab["api_popularity"], errors="coerce")
    tab["source"] = "spotify_api_big_sample"
    return tab


def nalozi_manjsi_spotify_api_vzorec():
    """Vrne tabelo manjsega starejsega Spotify API vzorca."""
    if not os.path.exists(SPOTIFY_MALA_DAT):
        return pd.DataFrame(columns=["track_name", "main_artist", "api_popularity", "source"])

    tab = pd.read_csv(SPOTIFY_MALA_DAT)

    if "track" in tab.columns and "track_name" not in tab.columns:
        tab["track_name"] = tab["track"]

    if "artist" in tab.columns and "main_artist" not in tab.columns:
        tab["main_artist"] = tab["artist"]

    if "main_artist" not in tab.columns:
        tab["main_artist"] = ""

    if "popularity" in tab.columns:
        tab["api_popularity"] = pd.to_numeric(tab["popularity"], errors="coerce")
    else:
        tab["api_popularity"] = np.nan

    tab["source"] = "spotify_api_small_sample"
    return tab


def zdruzi_vire_izvajalcev(pov_izv, tab_lastfm, tab_html):
    """Vrne zdruzeno tabelo izvajalcev iz Spotify, Last.fm in HTML vira."""
    zdruzena_tab = pov_izv.merge(
        tab_lastfm[["artist_key", "artist_name", "listeners", "playcount", "tags", "found"]],
        on="artist_key",
        how="left"
    )

    zdruzena_tab = zdruzena_tab.merge(
        tab_html[["artist_key", "claimed_sales", "period_active", "genre", "country", "in_html_best_selling"]],
        on="artist_key",
        how="left"
    )

    zdruzena_tab["in_html_best_selling"] = zdruzena_tab["in_html_best_selling"].fillna(False)
    return zdruzena_tab


def zdruzi_velik_spotify_api_vzorec(gl_tab, tab_api):
    """Vrne zdruzeno tabelo glavnega dataseta in velikega Spotify API vzorca."""
    if tab_api.empty:
        return pd.DataFrame()

    return gl_tab.merge(tab_api, on="track_id", how="inner")


def zdruzi_manjsi_spotify_api_vzorec(gl_tab, tab_api):
    """Vrne zdruzeno tabelo glavnega dataseta in manjsega Spotify API vzorca."""
    if tab_api.empty:
        return pd.DataFrame()

    return gl_tab.merge(
        tab_api[["track_name", "main_artist", "api_popularity", "source"]],
        on=["track_name", "main_artist"],
        how="inner"
    )


def izpisi_glavne_rezultate(pov_izv, zdruz_izv, zdruz_api, zdruz_api_m):
    """Vrne None in izpise povzetek vecvirovne analize."""
    print("Zdruzena analiza vseh virov")
    print("---------------------------")
    print("Število izvajalcev v povzetku:", len(pov_izv))
    print("Izvajalci z Last.fm podatki:", zdruz_izv["listeners"].notna().sum())
    print("Izvajalci, najdeni v HTML viru:", int(zdruz_izv["in_html_best_selling"].sum()))
    print("Pesmi v Spotify API vzorcu:", len(zdruz_api))
    print("Pesmi v manjši prejšnji Spotify API zbirki:", len(zdruz_api_m))
    print()


def izpisi_povezavo_z_lastfm(zdruz_izv):
    """Vrne None in izpise korelacijo med Spotify popularnostjo in Last.fm poslušalci."""
    podtab = zdruz_izv.dropna(subset=["listeners"]).copy()

    if podtab.empty:
        print("Povezava med Spotify popularnostjo in Last.fm poslušalci")
        print("--------------------------------------------------------")
        print("Ni dovolj Last.fm podatkov za izračun.")
        print()
        return

    podtab["log_listeners"] = np.log10(podtab["listeners"] + 1)
    kor = podtab["avg_popularity"].corr(podtab["log_listeners"])

    print("Povezava med Spotify popularnostjo in Last.fm poslušalci")
    print("--------------------------------------------------------")
    print("Korelacija:", round(kor, 3))
    print()


def izpisi_primerjavo_html(zdruz_izv):
    """Vrne None in izpise primerjavo med izvajalci iz HTML vira in ostalimi."""
    prim = zdruz_izv.groupby("in_html_best_selling")["avg_popularity"].mean()

    if prim.empty:
        print("Primerjava izvajalcev iz HTML vira")
        print("----------------------------------")
        print("HTML podatki niso na voljo.")
        print()
        return

    print("Primerjava izvajalcev iz HTML vira")
    print("----------------------------------")
    print("Izvajalci iz HTML best-selling vira imajo povprečno popularnost:", round(prim.get(True, float("nan")), 2))
    print("Ostali izvajalci imajo povprečno popularnost:", round(prim.get(False, float("nan")), 2))
    print()


def izpisi_primerjavo_spotify_api(zdruz_api, zdruz_api_m):
    """Vrne None in izpise primerjavo med CSV popularnostjo in Spotify API popularnostjo."""
    if zdruz_api.empty and zdruz_api_m.empty:
        print("Primerjava CSV in Spotify API popularnosti")
        print("------------------------------------------")
        print("Spotify API vzorec ni na voljo.")
        print()
        return

    if not zdruz_api.empty and zdruz_api["api_popularity"].notna().sum() > 0:
        kor = zdruz_api["popularity"].corr(zdruz_api["api_popularity"])
        povp_raz = (zdruz_api["api_popularity"] - zdruz_api["popularity"]).mean()

        print("Primerjava CSV in Spotify API popularnosti")
        print("------------------------------------------")
        print("Velik Spotify API vzorec - korelacija:", round(kor, 3))
        print("Velik Spotify API vzorec - povprečna razlika:", round(povp_raz, 2))
        print()
        return

    if zdruz_api_m.empty or zdruz_api_m["api_popularity"].notna().sum() == 0:
        print("Spotify API primerjava popularnosti")
        print("-----------------------------------")
        print("V Spotify API vzorcu ni polja api_popularity.")
        print()
        return

    kor = zdruz_api_m["popularity"].corr(zdruz_api_m["api_popularity"])
    povp_raz = (zdruz_api_m["api_popularity"] - zdruz_api_m["popularity"]).mean()

    print("Primerjava CSV in Spotify API popularnosti")
    print("------------------------------------------")
    print("Uporabljen je manjši Spotify API vzorec, pridobljen prej.")
    print("Korelacija:", round(kor, 3))
    print("Povprečna razlika:", round(povp_raz, 2))
    print()


def ustvari_lastfm_grafa(zdruz_izv):
    """Vrne None in shrani oba Last.fm grafa povezave s Spotify popularnostjo."""
    podtab = zdruz_izv.dropna(subset=["listeners"]).copy()

    if podtab.empty:
        return

    podtab = podtab[podtab["listeners"] > 0].copy()

    plt.figure(figsize=(10, 6))
    plt.scatter(podtab["listeners"], podtab["avg_popularity"], alpha=0.45, color="darkgreen", s=35)
    plt.xscale("log")
    plt.title("Povprečna Spotify popularnost in število Last.fm poslušalcev")
    plt.xlabel("Število Last.fm poslušalcev (logaritemska skala)")
    plt.ylabel("Povprečna Spotify popularnost")

    ozn_podtab = podtab.sort_values(["avg_popularity", "listeners"], ascending=False).head(12)
    osnovni_odm = [
        (4, 4), (6, 8), (6, -8), (-18, 6), (-18, -8), (8, 12),
        (8, -12), (-22, 12), (-22, -12), (10, 16), (-24, 16), (10, -16)
    ]

    for ind, (_, vrst) in enumerate(ozn_podtab.iterrows()):
        odm = ROCNI_ODMIKI.get(vrst["main_artist"], osnovni_odm[ind % len(osnovni_odm)])
        plt.annotate(
            vrst["main_artist"],
            (vrst["listeners"], vrst["avg_popularity"]),
            fontsize=7,
            xytext=odm,
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.8, ec="none"),
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.6, alpha=0.8)
        )

    plt.tight_layout()
    plt.savefig(DAT_LASTFM_GRAF)
    plt.close()

    top_podtab = podtab.sort_values(["avg_popularity", "listeners"], ascending=False).head(25).copy()

    plt.figure(figsize=(11, 7))
    plt.scatter(top_podtab["listeners"], top_podtab["avg_popularity"], alpha=0.75, color="darkgreen", s=45)
    plt.xscale("log")
    plt.title("Najpomembnejši izvajalci: Spotify popularnost in Last.fm poslušalci")
    plt.xlabel("Število Last.fm poslušalcev (logaritemska skala)")
    plt.ylabel("Povprečna Spotify popularnost")

    for ind, (_, vrst) in enumerate(top_podtab.iterrows()):
        odm = ROCNI_ODMIKI.get(vrst["main_artist"], osnovni_odm[ind % len(osnovni_odm)])
        plt.annotate(
            vrst["main_artist"],
            (vrst["listeners"], vrst["avg_popularity"]),
            fontsize=7,
            xytext=odm,
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.85, ec="none"),
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.6, alpha=0.8)
        )

    plt.tight_layout()
    plt.savefig(DAT_LASTFM_OZN)
    plt.close()


def ustvari_spotify_api_graf(zdruz_api, zdruz_api_m):
    """Vrne None in shrani primerjalni graf CSV in Spotify API popularnosti."""
    if not zdruz_api.empty:
        podtab = zdruz_api.dropna(subset=["api_popularity"]).copy()
    else:
        podtab = zdruz_api_m.dropna(subset=["api_popularity"]).copy()

    if podtab.empty:
        return

    plt.figure(figsize=(6, 6))
    plt.scatter(podtab["popularity"], podtab["api_popularity"], alpha=0.7, color="purple")
    plt.title("CSV popularnost proti Spotify API popularnosti")
    plt.xlabel("Popularnost v velikem CSV")
    plt.ylabel("Popularnost iz Spotify API")
    plt.tight_layout()
    plt.savefig(DAT_SPOTIFY_API_GRAF)
    plt.close()


def glavni_program():
    """Vrne None in pripravi koncno zdruzeno analizo vseh uporabljenih virov."""
    os.makedirs(MAPA_REZ, exist_ok=True)

    gl_tab = nalozi_glavne_podatke()
    pov_izv = zgradi_povzetek_izvajalcev(gl_tab)
    tab_lastfm = nalozi_lastfm_podatke()
    tab_html = nalozi_html_podatke()
    tab_api = nalozi_velik_spotify_api_vzorec()
    tab_api_m = nalozi_manjsi_spotify_api_vzorec()

    zdruz_izv = zdruzi_vire_izvajalcev(pov_izv, tab_lastfm, tab_html)
    zdruz_api = zdruzi_velik_spotify_api_vzorec(gl_tab, tab_api)
    zdruz_api_m = zdruzi_manjsi_spotify_api_vzorec(gl_tab, tab_api_m)

    zdruz_izv.to_csv(IZHOD_IZV_DAT, index=False)
    zdruz_api.to_csv(IZHOD_PES_DAT, index=False)

    izpisi_glavne_rezultate(pov_izv, zdruz_izv, zdruz_api, zdruz_api_m)
    izpisi_povezavo_z_lastfm(zdruz_izv)
    izpisi_primerjavo_html(zdruz_izv)
    izpisi_primerjavo_spotify_api(zdruz_api, zdruz_api_m)

    ustvari_lastfm_grafa(zdruz_izv)
    ustvari_spotify_api_graf(zdruz_api, zdruz_api_m)

    print("Shranjene datoteke")
    print("------------------")
    print(IZHOD_IZV_DAT)
    print(IZHOD_PES_DAT)
    print(DAT_LASTFM_GRAF)
    print(DAT_LASTFM_OZN)
    print(DAT_SPOTIFY_API_GRAF)


if __name__ == "__main__":
    glavni_program()
