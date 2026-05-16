# Opis
Program je namenjen urejanju slik, pri čemer jim doda tekst v največ dveh vrsticah s prosojnim črnim oknom okoli teksta.

![Primer](https://github.com/davidzindovic/Cinematic-subtitles-in-photos/blob/main/tole_edited.jpg)

# Priprava
V mapi naj bodo:
- skripta ali .exe datoteka
- oba fonta (.ttf datoteki)
- slika, ki jo želite urediti (z imenom ```tole```, končnica ni pomembna)

# Navodila za uporabo
Ob zagonu .exe datoteke (ali python skripte) bo program od vas zahteval 2 vnosa. Vsakič vnesite tekst dobesedno tako kot želite, da je izpisan. 

Če želite prisiliti novo vrstico, potem vnesite drugi del teksta pod drugi vnos (po pritisku tipke "Enter" prvič).

V primeru zapisa ```[Nek zapis]``` bo le ta ležeč (italic).

# Samostojno urejanje
V python skripti lahko spremenite:
- font, ki ga lahko poiščete na ```fonts.google.com```
- prosojnost okna
- velikost fonta
- odmik okna od spodnjega roba slike
- zaobljenost vogalov okna

.exe ustvarimo lahko z ukazom ```pyinstaller --onedir subtitles_in_pics.py```
