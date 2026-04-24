# Analiza priljubljenosti glasbe na Spotifyju

## Opis projekta
Projekt analizira priljubljenost glasbe s pomočjo več virov podatkov. Glavni vir je velik Spotify dataset, ki vsebuje podatke o pesmih, njihovi popularnosti in zvočnih lastnostih. Projekt je razširjen še z Last.fm API podatki o izvajalcih ter z Billboard Canadian Hot 100 podatki, pridobljenimi s HTML parsanja.

Glavni namen projekta je ugotoviti:
- kako so posamezne lastnosti pesmi povezane s popularnostjo,
- kako se popularnost razlikuje med skupinami žanrov,
- ali so izvajalci z več Last.fm poslušalci v povprečju tudi bolj popularni na Spotifyju,
- in ali se uspeh na Billboard lestvici povezuje z višjo Spotify popularnostjo.

## Cilji
- očistiti in pripraviti velik Spotify dataset za analizo,
- analizirati povezavo med popularnostjo in izbranimi lastnostmi pesmi,
- prikazati popularnost po skupinah žanrov,
- pridobiti dodatne podatke o izvajalcih iz Last.fm API,
- pridobiti podatke z Billboard Canadian Hot 100 spletne strani,
- združiti vse vire v skupno končno analizo,
- rezultate predstaviti z grafi.

## Viri podatkov
- veliki Spotify dataset: `data/spotify-tracks-dataset-detailed.csv`
- Last.fm API: podatki o izvajalcih, poslušalcih, predvajanjih in oznakah
- Billboard Canadian Hot 100: podatki o izvajalcih, uvrstitvah in tednih na lestvici

## Uporabljene tehnologije
- Python
- pandas
- matplotlib
- requests
- BeautifulSoup (`bs4`)
- csv

## Glavni programi
- `src/analyze_big_spotify_dataset.py`
  očisti glavni Spotify dataset in izdela osnovne analitične grafe

- `src/get_lastfm_from_big_dataset.py`
  izbere izvajalce iz glavnega dataseta in za njih pridobi podatke iz Last.fm API

- `src/get_html_data.py`
  s pomočjo HTML parsanja pridobi podatke z Billboard Canadian Hot 100

- `src/analyze_all_sources.py`
  združi Spotify, Last.fm in Billboard podatke ter izdela končne primerjalne grafe

## Struktura projekta
- `data/` – vhodne in ustvarjene CSV datoteke
- `src/` – Python programi za obdelavo in analizo
- `results/` – ustvarjeni grafi

## Glavne ustvarjene datoteke
- `data/spotify_analysis_clean.csv`
  očiščena verzija velikega Spotify dataseta

- `data/lastfm_big_artists.csv`
  Last.fm podatki za izbrane izvajalce

- `data/html_billboard_hot_100.csv`
  Billboard Canadian Hot 100 podatki, pridobljeni iz HTML-ja

- `results/big_popularity_histogram.png`
  histogram popularnosti pesmi

- `results/top_genres_by_average_popularity.png`
  povprečna popularnost po skupinah žanrov

- `results/popularity_correlations.png`
  korelacije med popularnostjo in izbranimi lastnostmi pesmi

- `results/artist_popularity_vs_lastfm_listeners.png`
  primerjava izvajalcev po povprečni Spotify popularnosti in Last.fm poslušalcih

- `results/artist_popularity_vs_billboard.png`
  primerjava izvajalcev po povprečni Spotify popularnosti in številu tednov na Billboard lestvici

## Zagon projekta
Najprej namesti potrebne knjižnice:

```bash
pip install pandas matplotlib requests beautifulsoup4
```

Nato v terminalu poženi programe v tem vrstnem redu:

```bash
py src/analyze_big_spotify_dataset.py
py src/get_lastfm_from_big_dataset.py
py src/get_html_data.py
py src/analyze_all_sources.py
```

## Kaj naredi vsak zagon
`analyze_big_spotify_dataset.py`
- prebere veliki Spotify dataset,
- očisti podatke,
- ustvari `spotify_analysis_clean.csv`,
- izdela osnovne Spotify grafe.

`get_lastfm_from_big_dataset.py`
- izbere izvajalce iz očiščenega Spotify dataseta,
- zanje pridobi Last.fm podatke,
- shrani jih v `lastfm_big_artists.csv`.

`get_html_data.py`
- prebere Billboard Canadian Hot 100 spletno stran,
- izlušči podatke iz HTML-ja,
- shrani jih v `html_billboard_hot_100.csv`.

`analyze_all_sources.py`
- poveže Spotify, Last.fm in Billboard podatke,
- pripravi skupno analizo izvajalcev,
- izdela končna primerjalna grafa.

## Povzetek
Projekt prikaže, kako lahko z uporabo več različnih virov podatkov analiziramo priljubljenost glasbe. Glavni del temelji na velikem Spotify datasetu, dodatno pa projekt uporabi še Last.fm API in HTML parsing Billboard lestvice, da dobi širšo sliko o uspešnosti pesmi in izvajalcev.
