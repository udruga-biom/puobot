# -*- coding: utf-8 -*-

"""
puobot
Web robot koji radi katalog PUO i SPUO postupaka
nadležnog ministarstva za zaštitu okoliša i prirode RH
verzija prilagođena za scraperwiki i morph.io
mzec 2017
v 0.1
"""

import os
os.environ['SCRAPERWIKI_DATABASE_NAME'] = 'sqlite:///data.sqlite'

from datetime import datetime
import re
import sys
import requests
from bs4 import BeautifulSoup
import scraperwiki

# funkcija za parse PUO/OPUO
def puoscrape(urlname, postupak='puo'):
    r = requests.get(urlname)

    url = 'http://puo.mzoe.hr'
    if postupak == 'puo':
        pattern = re.compile('PUO postupci 2[0-9]{3}')
    elif postupak == 'opuo':
        pattern = re.compile('OPUO postupci 2[0-9]{3}')

    soup = BeautifulSoup(r.content, 'lxml')
    link_elem = (soup.find_all('div', 'four mobile-four columns')[2]
                     .find_all('a', text=pattern))

    output = []
    for godina in link_elem:
        print(godina.text.strip())
        url_g = url + godina['href']
        r = requests.get(url_g)
        soup = BeautifulSoup(r.content, 'lxml')
        sadrzaj = soup.find_all('div', 'accordion')[0]
        zahvat_ime = sadrzaj.find_all('h3', recursive=False)
        zahvat_kat = sadrzaj.find_all('div', recursive=False)
        if len(zahvat_ime) != len(zahvat_kat):
            print('broj zahvata i kategorija se ne podudara')
        else:
            for ime, zahvacena_kategorija in zip(zahvat_ime, zahvat_kat):
                kategorije = zahvacena_kategorija.find_all('h3')
                for kat_index, kategorija in enumerate(kategorije):
                    linkovi = (zahvacena_kategorija
                               .find_all('ul', 'docs')[kat_index]
                               .find_all('a'))
                    for linak in linkovi:
                        polja = [polje.text.strip() for polje in
                                 [godina, ime, kategorija, linak]]
                        polja.append(linak['href'])
                        output.append('\t'.join(polja))
    return output

# funkcija za parse SPUO i prekograničnih postupaka
def puoscrape_alt(urlname):
    r = requests.get(urlname)
    soup = BeautifulSoup(r.content, 'lxml')
    output = []
    sadrzaj = soup.find_all('div', 'accordion')[0]
    zahvat_ime = sadrzaj.find_all('h3', recursive=False)
    zahvat_kat = sadrzaj.find_all('div', recursive=False)
    for ime, kategorija in zip(zahvat_ime, zahvat_kat):
        linkovi = kategorija.find_all('a')
        for linak in linkovi:
            polja = [ime.text.strip(), linak.text.strip(), linak['href']]
            output.append('\t'.join(polja))
    return output


BASE_URL = 'http://puo.mzoe.hr/hr/'

def trazenje(postupak):
    print('tražim {} postupke...'.format(postupak.upper()))
    url = BASE_URL + '{}.html'.format(postupak)
    return puoscrape(url, postupak)

# PUO postupci
puo_tab = trazenje('puo')

# OPUO postupci
opuo_tab = trazenje('opuo')

def trazenje_prekogranicnih(url):
    postupak = url.split('/')[0]
    print('tražim prekogranične {} postupke...'.format(postupak.upper()))
    return puoscrape_alt(BASE_URL + url)

# prekogranični PUO postupci
puo_pg_tab = trazenje_prekogranicnih('puo/prekogranicni-postupci-procjene-utjecaja-zahvata-na-okolis.html')

# SPUO postupci, prekogranični
spuo_pg_tab = trazenje_prekogranicnih('spuo/prekogranicni-postupci-strateske-procjene.html')


# SPUO postupci, nadležan MZOIE
print('tražim SPUO postupke za koje je nadležno MZOIE...')

url_spuo = BASE_URL + 'spuo.html'
url_spuo_min = BASE_URL + 'spuo/postupci-strateske-procjene-nadlezno-tijelo-je-ministarstvo-zastite-okolisa-i-energetike.html'
spuo_min_tab = puoscrape_alt(url_spuo_min)

# SPUO postupci, nadležno drugo središnje tijelo ili jedinice JLRS
print('tražim SPUO postupke za koje je nadležno drugo središnje tijelo ili JLRS...')

url_spuo_jlrs = BASE_URL + 'spuo/postupci-strateske-procjene-nadlezno-tijelo-je-drugo-sredisnje-tijelo-drzavne-uprave-ili-jedinica-podrucne-regionalne-ili-lokalne-samouprave.html'
r = requests.get(url_spuo_jlrs)
soup = BeautifulSoup(r.content, 'lxml')
sadrzaj = soup.find_all('h2', text=re.compile('Postupci stra.*'))[0].parent.parent.find_all('ul')[1]

spuo_jlrs_tab = []
for i in sadrzaj.find_all('li'):
    trazenje = re.search('^(.*?)(Nadle.*?)http.*', i.text)
    zahvat = trazenje.group(1)
    nadlezan = trazenje.group(2)
    link = i.find('a')['href']
    spuo_jlrs_tab.append('\t'.join([zahvat, nadlezan, link]))

# OSPUO postupci
print('tražim OSPUO postupke...')

url_ospuo = BASE_URL + 'spuo/ocjena-o-potrebi-provedbe-strateske-procjene.html'
r = requests.get(url_ospuo)
soup = BeautifulSoup(r.content, 'lxml')
sadrzaj = soup.find_all('div', 'accordion')[1]

ospuo_tab = []
for i in sadrzaj.find_all('a'):
    link = i['href']
    tekst = i.parent.parent.parent.parent.find('h3').text.strip()
    ospuo_tab.append('\t'.join([tekst, link]))


puo_tab_rev = list(reversed(puo_tab))
for i in puo_tab_rev:
    line = i.split('\t')
    scraperwiki.sqlite.save(unique_keys=['file_link'], 
                            data={'kategorija': line[0],
                                  'ime': line[1],
                                  'dokument': line[2],
                                  'file_ime': line[3],
                                  'file_link': line[4]},
                            table_name='data')

opuo_tab_rev = list(reversed(opuo_tab))
for i in opuo_tab_rev:
    line = i.split('\t')
    scraperwiki.sqlite.save(unique_keys=['file_link'], 
                            data={'kategorija': line[0],
                                  'ime': line[1],
                                  'dokument': line[2],
                                  'file_ime': line[3],
                                  'file_link': line[4]},
                            table_name='opuo')

puo_pg_tab_rev = list(reversed(puo_pg_tab))
for i in puo_pg_tab_rev:
    line = i.split('\t')
    scraperwiki.sqlite.save(unique_keys=['file_link'], 
                            data={'ime': line[0],
                                  'file_ime': line[1],
                                  'file_link': line[2]},
                            table_name='puo-prekogranicni')

spuo_pg_tab_rev = list(reversed(spuo_pg_tab))
for i in spuo_pg_tab_rev:
    line = i.split('\t')
    scraperwiki.sqlite.save(unique_keys=['file_link'], 
                            data={'ime': line[0],
                                  'file_ime': line[1],
                                  'file_link': line[2]},
                            table_name='spuo-prekogranicni')

spuo_min_tab_rev = list(reversed(spuo_min_tab))
for i in spuo_min_tab_rev:
    line = i.split('\t')
    scraperwiki.sqlite.save(unique_keys=['file_link'], 
                            data={'ime': line[0],
                                  'file_ime': line[1],
                                  'file_link': line[2]},
                            table_name='spuo-ministarstvo')

spuo_jlrs_tab_rev = list(reversed(spuo_jlrs_tab))
for i in spuo_jlrs_tab_rev:
    line = i.split('\t')
    scraperwiki.sqlite.save(unique_keys=['link'], 
                            data={'ime': line[0],
                                  'nadlezno-tijelo': line[1],
                                  'link': line[2]},
                            table_name='spuo-jlrs')

ospuo_tab_rev = list(reversed(ospuo_tab))
for i in ospuo_tab_rev:
    line = i.split('\t')
    scraperwiki.sqlite.save(unique_keys=['link'], 
                            data={'ime': line[0],
                                  'link': line[1]},
                            table_name='ospuo')

