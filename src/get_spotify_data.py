import csv
import time

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"


ZACETNI_ID_PESMI = [
    "3sK8wGT43QFpWrvNQsrQya",
    "5O4erNlJ74PIF6kGol1ZrC",
    "7J1uxwnxfQLu4APicE5Rnj",
    "3FNy4yzOhHhFBeA5p4ofoq",
    "5fZJQrFKWQLb7FpJXZ1g7K",
    "452KBpASS5lZLeJWX9Ixub",
]

IZHODNA_DATOTEKA = "data/spotify_tracks.csv"
NAJVEC_ALBUMOV = 2
CAS_CAKANJA = 1


def ustvari_spotify_client():
    """Vrne pripravljen Spotify client za nadaljnje API klice."""
    upravitelj_prijave = SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    return spotipy.Spotify(auth_manager=upravitelj_prijave)


def pridobi_podrobnosti_pesmi(spotify, id_pesmi):
    """Vrne slovar s podrobnostmi ene pesmi iz Spotify API."""
    pesem = spotify.track(id_pesmi)
    time.sleep(CAS_CAKANJA)

    imena_izvajalcev = []
    id_ji_izvajalcev = []
    for izvajalec in pesem["artists"]:
        imena_izvajalcev.append(izvajalec["name"])
        if izvajalec.get("id"):
            id_ji_izvajalcev.append(izvajalec["id"])

    return {
        "track_id": pesem["id"],
        "track_name": pesem["name"],
        "main_artist": imena_izvajalcev[0] if imena_izvajalcev else "",
        "artists": ", ".join(imena_izvajalcev),
        "artist_ids": ", ".join(id_ji_izvajalcev),
        "album_id": pesem["album"].get("id", ""),
        "album_name": pesem["album"]["name"],
        "duration_ms": pesem.get("duration_ms", ""),
        "explicit": pesem.get("explicit", ""),
        "track_number": pesem.get("track_number", ""),
        "spotify_url": pesem["external_urls"].get("spotify", "")
    }


def pridobi_idje_albumov_izvajalca(spotify, id_izvajalca):
    """Vrne seznam ID-jev albumov za enega izvajalca."""
    rezultat = spotify.artist_albums(
        id_izvajalca,
        album_type="album",
        limit=NAJVEC_ALBUMOV
    )
    time.sleep(CAS_CAKANJA)

    seznam_albumov = []
    for album in rezultat["items"]:
        if album.get("id"):
            seznam_albumov.append(album["id"])

    return seznam_albumov


def pridobi_idje_pesmi_albuma(spotify, id_albuma):
    """Vrne seznam ID-jev vseh pesmi z izbranega albuma."""
    rezultat = spotify.album_tracks(id_albuma)
    time.sleep(CAS_CAKANJA)

    seznam_pesmi = []
    for pesem in rezultat["items"]:
        if pesem.get("id"):
            seznam_pesmi.append(pesem["id"])

    return seznam_pesmi


def shrani_v_csv(vrstice, ime_datoteke):
    """Vrne None in shrani zbrane Spotify podatke v CSV datoteko."""
    if not vrstice:
        print("Ni podatkov za shranjevanje.")
        return

    imena_stolpcev = list(vrstice[0].keys())

    with open(ime_datoteke, "w", newline="", encoding="utf-8") as datoteka:
        pisec = csv.DictWriter(datoteka, fieldnames=imena_stolpcev)
        pisec.writeheader()
        pisec.writerows(vrstice)


def glavni_program():
    """Vrne None in iz nekaj zacetnih pesmi zgradi manjso Spotify zbirko."""
    spotify = ustvari_spotify_client()
    vse_vrstice = []
    videni_id_ji_pesmi = set()
    videni_id_ji_albumov = set()
    videni_id_ji_izvajalcev = set()

    print("Povezava na Spotify API je uspela.")
    print()

    try:
        for zacetni_id_pesmi in ZACETNI_ID_PESMI:
            try:
                zacetna_pesem = pridobi_podrobnosti_pesmi(spotify, zacetni_id_pesmi)
                id_albuma = zacetna_pesem["album_id"]

                print("Zacetna pesem:", zacetna_pesem["track_name"])
                print("Album:", zacetna_pesem["album_name"])
                print()

                seznam_id_jev_izvajalcev = []
                if zacetna_pesem["artist_ids"]:
                    seznam_id_jev_izvajalcev = zacetna_pesem["artist_ids"].split(", ")

                for id_izvajalca in seznam_id_jev_izvajalcev:
                    if id_izvajalca in videni_id_ji_izvajalcev:
                        continue

                    videni_id_ji_izvajalcev.add(id_izvajalca)
                    id_ji_albumov = pridobi_idje_albumov_izvajalca(spotify, id_izvajalca)

                    for trenutni_id_albuma in id_ji_albumov:
                        if trenutni_id_albuma in videni_id_ji_albumov:
                            continue

                        videni_id_ji_albumov.add(trenutni_id_albuma)
                        id_ji_pesmi = pridobi_idje_pesmi_albuma(spotify, trenutni_id_albuma)

                        for id_pesmi in id_ji_pesmi:
                            if id_pesmi in videni_id_ji_pesmi:
                                continue

                            vrstica = pridobi_podrobnosti_pesmi(spotify, id_pesmi)
                            vse_vrstice.append(vrstica)
                            videni_id_ji_pesmi.add(id_pesmi)

                        shrani_v_csv(vse_vrstice, IZHODNA_DATOTEKA)

                if id_albuma and id_albuma not in videni_id_ji_albumov:
                    videni_id_ji_albumov.add(id_albuma)
                    id_ji_pesmi = pridobi_idje_pesmi_albuma(spotify, id_albuma)

                    for id_pesmi in id_ji_pesmi:
                        if id_pesmi in videni_id_ji_pesmi:
                            continue

                        vrstica = pridobi_podrobnosti_pesmi(spotify, id_pesmi)
                        vse_vrstice.append(vrstica)
                        videni_id_ji_pesmi.add(id_pesmi)

                    shrani_v_csv(vse_vrstice, IZHODNA_DATOTEKA)
            except Exception as napaka:
                print(f"Napaka pri track_id {zacetni_id_pesmi}: {napaka}")
                print("Ta pesem bo preskocena.")
                print()
    except KeyboardInterrupt:
        print()
        print("Program je bil prekinjen.")
        print("Delni rezultati bodo shranjeni.")
    finally:
        shrani_v_csv(vse_vrstice, IZHODNA_DATOTEKA)
        print(f"Stevilo shranjenih pesmi: {len(vse_vrstice)}")
        print(f"Podatki so shranjeni v: {IZHODNA_DATOTEKA}")


if __name__ == "__main__":
    glavni_program()
