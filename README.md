# puobot

## Uvod

puobot je web robot koji radi katalog PUO i SPUO postupaka nadležnog ministarstva za zaštitu okoliša i prirode RH. Powering [Robo-MZOIP](https://twitter.com/robo_mzoip).

### Problem

Dokumenti o postupcima procjene utjecaja na okoliš na web stranici [nadležnog ministarstva za zaštitu okoliša i prirode](http://puo.mzoip.hr/) se dodaju na način da je nemoguće sustavno i redovito pratiti objave novih dokumenata.

### Rješenje

Web scraper koji redovito prati nove dodane dokumente i radi katalog zahvata i dokumenata, te po potrebi nove zahvate objavljuje putem twitter-a. 

## Korištenje

```
python3 puobot.py [--twitter 1]
```

Za twitter funkcionalnost potrebno je imati Twitter Api key i staviti ga u datoteku `/input/twit_api_key.txt`.

## Zahtjevi

- Python 3
- BeautifulSoup4
- twython
- lxml parser
