import csv

import requests
from bs4 import BeautifulSoup


URL_STRANI = "https://en.wikipedia.org/wiki/List_of_best-selling_music_artists"
IZHODNA_DATOTEKA = "data/html_best_selling_artists.csv"
GLAVE_ZAHTEVKA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}


def pocisti_besedilo(besedilo):
    """Vrne poenoteno besedilo brez odvecnih presledkov."""
    return " ".join(besedilo.split())


def shrani_v_csv(vrstice, ime_datoteke):
    """Vrne None in shrani seznam slovarjev v CSV datoteko."""
    if not vrstice:
        print("Ni podatkov za shranjevanje.")
        return

    imena_stolpcev = list(vrstice[0].keys())

    with open(ime_datoteke, "w", newline="", encoding="utf-8") as datoteka:
        pisec = csv.DictWriter(datoteka, fieldnames=imena_stolpcev)
        pisec.writeheader()
        pisec.writerows(vrstice)


def poisci_ciljne_tabele(juha):
    """Vrne seznam HTML tabel, ki vsebujejo podatke o najbolje prodajanih izvajalcih."""
    vse_tabele = juha.find_all("table", class_="wikitable")
    ciljne_tabele = []

    for tabela in vse_tabele:
        celice_glave = tabela.find_all("th")
        glave = [pocisti_besedilo(celica.get_text(" ", strip=True)).lower() for celica in celice_glave[:10]]
        besedilo_glave = " ".join(glave)

        if "artist" in besedilo_glave and "claimed sales" in besedilo_glave:
            ciljne_tabele.append(tabela)

    return ciljne_tabele


def izloci_vrstice(tabela):
    """Vrne seznam vrstic iz ene HTML tabele v obliki slovarjev."""
    vrstice = []
    vrstice_tabele = tabela.find_all("tr")

    for vrstica in vrstice_tabele[1:]:
        celice = vrstica.find_all(["th", "td"])

        if len(celice) < 5:
            continue

        for celica in celice:
            for opomba in celica.find_all("sup"):
                opomba.decompose()

        podatki_vrstice = {
            "artist_name": pocisti_besedilo(celice[0].get_text(" ", strip=True)),
            "claimed_sales": pocisti_besedilo(celice[1].get_text(" ", strip=True)),
            "period_active": pocisti_besedilo(celice[2].get_text(" ", strip=True)),
            "genre": pocisti_besedilo(celice[3].get_text(" ", strip=True)),
            "country": pocisti_besedilo(celice[4].get_text(" ", strip=True))
        }

        if podatki_vrstice["artist_name"] and podatki_vrstice["artist_name"].lower() != "artist":
            vrstice.append(podatki_vrstice)

    return vrstice


def glavni_program():
    """Vrne None in shrani HTML podatke o najbolje prodajanih izvajalcih v CSV."""
    odgovor = requests.get(URL_STRANI, headers=GLAVE_ZAHTEVKA, timeout=20)
    odgovor.raise_for_status()

    juha = BeautifulSoup(odgovor.text, "html.parser")
    ciljne_tabele = poisci_ciljne_tabele(juha)

    if not ciljne_tabele:
        print("Glavne tabele niso bile najdene.")
        return

    vse_vrstice = []
    videni_izvajalci = set()

    for tabela in ciljne_tabele:
        vrstice_tabele = izloci_vrstice(tabela)

        for vrstica in vrstice_tabele:
            ime_izvajalca = vrstica["artist_name"].lower()
            if ime_izvajalca in videni_izvajalci:
                continue

            vse_vrstice.append(vrstica)
            videni_izvajalci.add(ime_izvajalca)

    shrani_v_csv(vse_vrstice, IZHODNA_DATOTEKA)

    print("HTML scraping je uspel.")
    print("Stevilo vrstic:", len(vse_vrstice))
    print(f"Podatki so shranjeni v: {IZHODNA_DATOTEKA}")


if __name__ == "__main__":
    glavni_program()
