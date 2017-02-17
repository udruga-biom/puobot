"""
Puobot
Web robot koji radi katalog PUO i SPUO postupaka
nadležnog ministarstva za zaštitu okoliša i prirode RH
mzec 2017
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# PUO postupci

url = 'http://puo.mzoip.hr'
r = requests.get(url)

soup = BeautifulSoup(r.text, 'lxml')
link_elem = soup.find_all('div', 'four mobile-four columns')[2]\
                .find_all('a', text = re.compile('PUO postupci 2[0-9]{3}'))
link = []
print('kategorije:')
for i in link_elem:
    link.append(url + i['href'])
    print(i.text)

tablica = []
for url_g in link:
    print('obrađujem: ' + url_g)
    r = requests.get(url_g)
    soup = BeautifulSoup(r, 'lxml')
    sadrzaj = soup.find_all('div', 'accordion')[0]
    zahvat_ime = sadrzaj.find_all('h3', recursive = False)
    zahvat_kat = sadrzaj.find_all('div', recursive = False)
    if len(zahvat_ime) != len(zahvat_kat):
        print('broj zahvata i kategorija se ne podudara')
    else:
        n_zahvata = len(zahvat_ime)
        for zahvat in range(n_zahvata):
            find.all       
            naziv = zahvat_ime[zahvat]

