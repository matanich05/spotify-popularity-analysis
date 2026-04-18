# Analiza priljubljenosti glasbe na Spotifyju

## Opis projekta
Ta projekt se osredotoča na analizo dejavnikov, ki vplivajo na priljubljenost pesmi na platformi Spotify. Glavni cilj je ugotoviti, katere značilnosti pesmi in izvajalcev so najbolj povezane z višjo popularnostjo.

Projekt združuje podatke iz več virov, vključno s Spotify API, Last.fm API ter izbranimi spletnimi stranmi. Zbrane podatke obdelamo, očistimo in analiziramo s pomočjo programskega jezika Python.

## Cilji
- Zbiranje podatkov o pesmih preko Spotify API
- Razširitev podatkov z uporabo Last.fm API
- Po potrebi pridobivanje dodatnih podatkov z uporabo HTML parsanja
- Analiza povezav med značilnostmi pesmi in njihovo popularnostjo
- Vizualizacija rezultatov z grafi

## Viri podatkov
- Spotify API (audio značilnosti, popularnost, metapodatki)
- Last.fm API (število poslušanj, poslušalci, oznake)
- Spletne strani (dodatni podatki po potrebi)

## Uporabljene tehnologije
- Python
- requests
- pandas
- matplotlib / seaborn
- BeautifulSoup
- scikit-learn (po želji)

## Struktura projekta
- `data/` – surovi in obdelani podatki
- `src/` – izvorna koda za pridobivanje in analizo podatkov
- `results/` – rezultati analize in grafi

## Zagon projekta
1. Namesti potrebne knjižnice:
   ```bash
   pip install -r requirements.txt
