"""
Puobot
Web robot koji radi katalog PUO i SPUO postupaka
nadležnog ministarstva za zaštitu okoliša i prirode RH
mzec 2017
"""

# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# PUO postupci

url = 'http://puo.mzoip.hr'
r = requests.get(url)

soup = BeautifulSoup(r.content, 'lxml')
link_elem = soup.find_all('div', 'four mobile-four columns')[2]\
                .find_all('a', text = re.compile('PUO postupci 2[0-9]{3}'))
link_pg = soup.find_all('div', 'four mobile-four columns')[2]\
        .find_all('a', text = re.compile('Prekogr'))[0]

puo_tab = []
for godina in range(len(link_elem)):
    url_g = url + link_elem[godina]['href']
    r = requests.get(url_g)
    soup = BeautifulSoup(r.content, 'lxml')
    sadrzaj = soup.find_all('div', 'accordion')[0]
    zahvat_ime = sadrzaj.find_all('h3', recursive = False)
    zahvat_kat = sadrzaj.find_all('div', recursive = False)
    if len(zahvat_ime) != len(zahvat_kat):
        print('broj zahvata i kategorija se ne podudara')
    else:
        n_zahvata = len(zahvat_ime)
        for zahvat in range(n_zahvata):
            naziv = zahvat_ime[zahvat]
            kategorije = zahvat_kat[zahvat].find_all('h3')
            for kategorija in range(len(kategorije)):
                linkovi = zahvat_kat[zahvat]\
                        .find_all('ul', 'docs')[kategorija]\
                        .find_all('a')
                for linak in range(len(linkovi)):
                    puo_tab.append(link_elem[godina].text.strip() + '\t' +
                                   zahvat_ime[zahvat].text.strip() + '\t' +
                                   kategorije[kategorija].text.strip() + '\t' +
                                   linkovi[linak].text.strip() + '\t' +
                                   linkovi[linak]['href'])

url_pg = url + link_pg['href']
r = requests.get(url_pg)
soup = BeautifulSoup(r.content, 'lxml')

puo_pg_tab = []
sadrzaj = soup.find_all('div', 'accordion')[0]
zahvat_ime = sadrzaj.find_all('h3', recursive = False)
zahvat_kat = sadrzaj.find_all('div', recursive = False)
for zahvat in range(len(zahvat_ime)):
    linkovi = zahvat_kat[zahvat].find_all('a')
    for linak in range(len(linkovi)):
        puo_pg_tab.append(zahvat_ime[zahvat].text.strip() + '\t' +
                          linkovi[linak].text.strip() + '\t' +
                          linkovi[linak]['href'])

    

# OPUO postupci

opuo_tab = []

with open('puo.tsv', 'w') as f:
    f.write('\n'.join(puo_tab))
with open('puo_pg.tsv', 'w') as f:
    f.write('\n'.join(puo_pg_tab))
