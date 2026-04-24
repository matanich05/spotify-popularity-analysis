import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


spotfiy_urejen = "data/spotify_analysis_clean.csv"
lastfm_dat = "data/lastfm_big_artists.csv"
html_dat = "data/html_billboard_hot_100.csv"
rez_mapa = "results"
prvi_lastfm_graf = "results/artist_popularity_vs_lastfm_listeners.png"
html_graf = "results/artist_popularity_vs_billboard.png"


def ime(bes):
    """Vrne ime izvajalca v enotni obliki."""
    if pd.isna(bes):
        return ""
    bes = str(bes).lower().strip()
    bes = bes.replace("&", "and")
    bes = bes.replace("’", "'")
    return " ".join(bes.split())


def glavni_podatki():
    """Vrne glavno Spotify tabelo."""
    tab = pd.read_csv(spotfiy_urejen)
    if "main_artist" not in tab.columns:
        tab["main_artist"] = tab["artists"].fillna("").apply(
            lambda bes: str(bes).split(";")[0].strip() if str(bes) else ""
        )
    tab["artist_key"] = tab["main_artist"].apply(ime)
    tab["duration_min"] = tab["duration_ms"] / 60000
    return tab


def povzetek_izvajalcev(tab):
    """Vrne povzetek po izvajalcih."""
    return (
        tab.groupby(["artist_key", "main_artist"])
        .agg(
            track_count=("track_id", "count"),
            avg_popularity=("popularity", "mean"),
            median_popularity=("popularity", "median"),
        )
        .reset_index()
    )


def lastfm_podatki():
    """Vrne Last.fm tabelo."""
    tab = pd.read_csv(lastfm_dat)
    tab["artist_key"] = tab["artist_name"].apply(ime)
    tab["listeners"] = pd.to_numeric(tab["listeners"], errors="coerce")
    tab["playcount"] = pd.to_numeric(tab["playcount"], errors="coerce")
    return tab


def html_podatki():
    """Vrne Billboard tabelo po izvajalcih."""
    if not os.path.exists(html_dat):
        return pd.DataFrame(
            columns=[
                "artist_name",
                "artist_key",
                "best_rank",
                "weeks_on_chart",
                "in_html_chart",
            ]
        )
    tab = pd.read_csv(html_dat)
    tab["artist_key"] = tab["artist_name"].apply(ime)
    tab["rank"] = pd.to_numeric(tab["rank"], errors="coerce")
    tab["weeks_on_chart"] = pd.to_numeric(tab["weeks_on_chart"], errors="coerce")
    tab = (
        tab.groupby(["artist_key", "artist_name"])
        .agg(
            best_rank=("rank", "min"),
            weeks_on_chart=("weeks_on_chart", "max"),
        )
        .reset_index()
    )
    tab["in_html_chart"] = True
    return tab


def zdruzevanje_virov(pov_izv, tab_lastfm, tab_html):
    """Vrne združeno tabelo izvajalcev."""
    zdruz = pov_izv.merge(
        tab_lastfm[["artist_key", "artist_name", "listeners", "playcount", "tags", "found"]],
        on="artist_key",
        how="left",
    )
    zdruz = zdruz.merge(
        tab_html[["artist_key", "best_rank", "weeks_on_chart", "in_html_chart"]],
        on="artist_key",
        how="left",
    )
    zdruz["in_html_chart"] = zdruz["in_html_chart"].fillna(False)
    return zdruz


def lastfm_graf(zdruz_izv):
    """Shrani primerjalni Last.fm graf."""
    podtab = zdruz_izv.dropna(subset=["listeners"]).copy()
    if podtab.empty:
        return
    podtab = podtab[podtab["listeners"] > 0].copy()
    podtab = podtab.sort_values(["avg_popularity", "listeners"], ascending=False).head(50).copy()
    podtab = podtab.sort_values("avg_popularity", ascending=True)
    fig, osi = plt.subplots(1, 2, figsize=(20, 26), sharey=True)
    osi[0].barh(podtab["main_artist"], podtab["avg_popularity"], color="seagreen")
    osi[0].set_title("Top 50 izvajalcev po povprečni Spotify popularnosti")
    osi[0].set_xlabel("Povprečna Spotify popularnost")
    osi[0].set_ylabel("Izvajalec")
    osi[1].barh(podtab["main_artist"], podtab["listeners"], color="steelblue")
    osi[1].set_title("Isti top 50 izvajalci po številu Last.fm poslušalcev")
    osi[1].set_xlabel("Število Last.fm poslušalcev")
    osi[1].set_xscale("log")
    plt.tight_layout()
    plt.savefig(prvi_lastfm_graf)
    plt.close()


def billboard_graf(zdruz_izv):
    """Shrani primerjalni Billboard graf."""
    podtab = zdruz_izv.dropna(subset=["best_rank", "weeks_on_chart"]).copy()
    if podtab.empty:
        return

    podtab = podtab.sort_values(["avg_popularity", "weeks_on_chart"], ascending=False).head(50).copy()
    podtab = podtab.sort_values("avg_popularity", ascending=True)

    fig, osi = plt.subplots(1, 2, figsize=(20, 26), sharey=True)

    osi[0].barh(podtab["main_artist"], podtab["avg_popularity"], color="seagreen")
    osi[0].set_title("Top izvajalci z Billboard lestvice po Spotify popularnosti")
    osi[0].set_xlabel("Povprečna Spotify popularnost")
    osi[0].set_ylabel("Izvajalec")

    osi[1].barh(podtab["main_artist"], podtab["weeks_on_chart"], color="darkorange")
    osi[1].set_title("Isti izvajalci po številu tednov na Billboard lestvici")
    osi[1].set_xlabel("Tedni na lestvici")

    plt.tight_layout()
    plt.savefig(html_graf)
    plt.close()


def glavni():
    """Naredi končno združeno analizo."""
    os.makedirs(rez_mapa, exist_ok=True)
    gl_tab = glavni_podatki()
    pov_izv = povzetek_izvajalcev(gl_tab)
    tab_lastfm = lastfm_podatki()
    tab_html = html_podatki()
    zdruz_izv = zdruzevanje_virov(pov_izv, tab_lastfm, tab_html)
    lastfm_graf(zdruz_izv)
    billboard_graf(zdruz_izv)


if __name__ == "__main__":
    glavni()
