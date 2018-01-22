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

## Ulazni podaci

### Twitter

Za twitter funkcionalnost potrebno je imati Twitter oauth podatke u zasebnim redovima u datoteci `/input/twit_api_key.txt`.

`twit_api_key.txt`:
```
[API Key]
[API Secret]
[Access token]
[Access token secret]
```

## Izlazni podaci

Svi pronađeni dokumenti pospremaju se u arhivu u zasebne `.tsv` datoteke:

- `puo.tsv` - [PUO postupci](http://puo.mzoip.hr/hr/puo.html) (procjena utjecaja na okoliš)
- `puo_pg.tsv` - [Prekogranični PUO postupci](http://puo.mzoip.hr/hr/puo/prekogranicni-postupci-procjene-utjecaja-zahvata-na-okolis.html)
- `opuo.tsv` - [OPUO postupci](http://puo.mzoip.hr/hr/opuo.html) (ocjena o potrebi procjene utjecaja na okoliš, "screening")
- `spuo_min.tsv` - [SPUO postupci za koje je nadležno Ministarstvo](http://puo.mzoip.hr/hr/spuo/postupci-strateske-procjene-nadlezno-tijelo-je-ministarstvo-zastite-okolisa-i-energetike.html) (strateška procjena utjecaja na okoliš)
- `spuo_jlrs.tsv` - [SPUO postupci za koje su nadležna druga upravna tijela (npr. JLRS)](http://puo.mzoip.hr/hr/spuo/postupci-strateske-procjene-nadlezno-tijelo-je-drugo-sredisnje-tijelo-drzavne-uprave-ili-jedinica-podrucne-regionalne-ili-lokalne-samouprave.html) (strateška procjena utjecaja na okoliš)
- `spuo_pg.tsv` - [Prekogranični SPUO postupci](http://puo.mzoip.hr/hr/spuo/prekogranicni-postupci-strateske-procjene.html)
- `ospuo.tsv` - [OSPUO](http://puo.mzoip.hr/hr/spuo/ocjena-o-potrebi-provedbe-strateske-procjene.html) (ocjena o potrebi strateške procjene, "screening")

Sve razlike između posljednje verzije arhive spremljene u `output/` folderu ispisuju se na standardni output (konzolu)

## Zahtjevi

- Python 3
- requests (2.12.4)
- BeautifulSoup4 (4.5.3)
- lxml parser (3.7.2)
- scraperwiki (0.5.1)
- twython
