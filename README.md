# danzame.it

Sito dell'Associazione Culturale DANZ@M.E di Acireale e archivio delle coreografie di C. Enrico Musmeci, in italiano, inglese e francese.

Ogni modifica salvata in questo repository ripubblica il sito da sola in un paio di minuti. Tutto si può fare dal browser, su github.com, senza installare niente.

## Dove sta cosa

| Cosa | Dove |
|---|---|
| Una scheda per ogni coreografia | `contenuti/coreografie/` (un file `.yml` per lavoro) |
| Il Mò.DANCEFEST in evidenza in home | `contenuti/festival.yml` |
| Testi della home e biografia | `contenuti/home/it.yml`, `en.yml`, `fr.yml` |
| Foto delle coreografie | `img/coreografie/` |
| Locandine e foto del festival | `img/festival/` |
| Ritratto e foto d'archivio | `img/biografia/` |
| Grafica e codice | `strumenti/` (di solito non serve toccarlo) |

## Aggiungere una coreografia

1. Carica le foto: apri `img/coreografie/`, poi **Add file → Upload files**. Vanno bene anche gli originali grandi, il sito li riduce da solo. Dai ai file un nome parlante, per esempio `unerwartete-materie-01.jpg`.
2. Apri `contenuti/coreografie/_modello.yml` e copia il contenuto.
3. Torna in `contenuti/coreografie/`, poi **Add file → Create new file**. Chiama il file con un nome corto, minuscolo e senza spazi (`titolo-del-lavoro.yml`), incolla il modello e compila i campi.
4. In fondo clicca **Commit changes**.

Le repliche si scrivono tutte insieme: il sito mostra da solo quelle future come "Prossime date" e quelle passate come "Repliche". Date, "danzatori", "Prima" e le altre etichette si traducono automaticamente in inglese e francese. Titoli, teatri e compositori restano come sono.

## Cambiare i lavori mostrati in home

Nella scheda, `in_home: true` mette il lavoro tra i "Lavori recenti". Ne vengono mostrati al massimo 6, i più recenti. Per toglierne uno, cancella la riga o scrivi `in_home: false`.

## Nuova edizione del Mò.DANCEFEST

In `contenuti/festival.yml`:
1. sposta l'edizione appena finita in `edizioni_precedenti` (anno, locandina, didascalia);
2. aggiorna `edizione`, `anno`, `date`, `locandina` e i `giorni` con il programma;
3. carica la nuova locandina in `img/festival/`.

Le foto dell'edizione vanno in `img/festival/` e si elencano sotto `foto:`. Finché la lista è vuota, in home al loro posto compare un riquadro "in arrivo".

## Se qualcosa non va

Dopo ogni modifica, nella scheda **Actions** del repository compare la pubblicazione in corso. Se diventa rossa, aprila: il passaggio "genera" dice in italiano cosa correggere (per esempio una foto con il nome sbagliato o un campo mancante). Finché non si corregge, online resta la versione precedente, quindi il sito non si rompe mai.

## Generare il sito sul proprio computer (facoltativo)

```
pip install -r requirements.txt
python strumenti/genera.py
```

Il risultato è nella cartella `_site/`.
