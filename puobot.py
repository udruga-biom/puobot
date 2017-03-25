# -*- coding: utf-8 -*-

"""
puobot
Web robot koji radi katalog PUO i SPUO postupaka
nadležnog ministarstva za zaštitu okoliša i prirode RH
mzec 2017
v 0.1
"""

import argparse
from datetime import datetime
import os
import re
import sys
import requests
from bs4 import BeautifulSoup


parser = argparse.ArgumentParser()
parser.add_argument('--twitter', help = 'optional argument to update twitter')
args = parser.parse_args()

# provjera treba li baciti update na twitter:
if args.twitter:
    import twython
    with open('input/twit_api_data.txt', 'r') as f:
        twython_api_data = f.read().splitlines()
    twitter = twython.Twython(*twython_api_data)
    print('>> Twitter mode')
else:
    print('>> Twitterless mode')

# kreiranje output foldera za prvo pokretanje
if 'output' not in os.listdir():
    os.mkdir('output')
if 'arhiva' not in os.listdir('output'):
    os.mkdir('output/arhiva')
if 'puo-arhiva-git' not in os.listdir('output'):
    os.mkdir('output/puo-arhiva-git')

# funkcija za snimanje
def puosave(save_dir):
    postupci = {
        'puo': puo_tab,
        'puo_pg': puo_pg_tab,
        'opuo': opuo_tab,
        'spuo_min': spuo_min_tab,
        'spuo_pg': spuo_pg_tab,
        'spuo_jlrs': spuo_jlrs_tab,
        'ospuo': ospuo_tab,
    }
    for filename, postupak in postupci.items():
        with open(save_dir + filename + '.tsv', 'w') as f:
            f.write('\n'.join(postupak))


# funkcija za čitanje
def puoread(read_dir, filename):
    with open(read_dir + filename + '.tsv', 'r') as f:
        in_file = f.read().splitlines()
    return in_file


def get_sadrzaj(url, clan=0):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    return soup.find_all('div', 'accordion')[clan]

def get_zahvat(url):
    sadrzaj = get_sadrzaj(url)
    zahvat_ime = sadrzaj.find_all('h3', recursive=False)
    zahvat_kat = sadrzaj.find_all('div', recursive=False)
    return zahvat_ime, zahvat_kat


# funkcija za parse PUO/OPUO
def puoscrape(urlname, postupak='puo'):
    if postupak == 'puo':
        pattern = re.compile('PUO postupci 2[0-9]{3}')
    elif postupak == 'opuo':
        pattern = re.compile('OPUO postupci 2[0-9]{3}')

    r = requests.get(urlname)
    soup = BeautifulSoup(r.content, 'lxml')
    link_elem = (soup.find_all('div', 'four mobile-four columns')[2]
                     .find_all('a', text=pattern))

    url = 'http://puo.mzoip.hr'
    output = []
    for godina in link_elem:
        print(godina.text.strip())
        url_g = url + godina['href']
        zahvati = get_zahvat(url_g)
        if len(zahvati[0]) != len(zahvati[1]):
            print('broj zahvata i kategorija se ne podudara')
        else:
            for ime, zahvacena_kategorija in zip(*zahvati):
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
    zahvati = get_zahvat(urlname)
    output = []
    for ime, kategorija in zip(*zahvati):
        linkovi = kategorija.find_all('a')
        for linak in linkovi:
            polja = [ime.text.strip(), linak.text.strip(), linak['href']]
            output.append('\t'.join(polja))
    return output


BASE_URL = 'http://puo.mzoip.hr/hr/'


def trazenje(postupak):
    print('tražim {} postupke...'.format(postupak.upper()))
    url = BASE_URL + '{}.html'.format(postupak)
    return puoscrape(url, postupak)


def trazenje_prekogranicnih(url):
    postupak = url.split('/')[0]
    print('tražim prekogranične {} postupke...'.format(postupak.upper()))
    return puoscrape_alt(BASE_URL + url)


def trazenje_spuo(url, nadleznost):
    if nadleznost == 'MZOIE':
        print('tražim SPUO postupke za koje je nadležno MZOIE...')
        return puoscrape_alt(BASE_URL + url)
    else:
        print('tražim SPUO postupke za koje je nadležno drugo središnje tijelo ili JLRS...')
        r = requests.get(BASE_URL + url)
        soup = BeautifulSoup(r.content, 'lxml')
        sadrzaj = (soup.find_all('h2', text=re.compile('Postupci stra.*'))[0]
                   .parent.parent.find_all('ul')[1])

        postupci = []
        for i in sadrzaj.find_all('li'):
            trazenje = re.search('^(.*?)(Nadle.*?)http.*', i.text)
            zahvat = trazenje.group(1)
            nadlezan = trazenje.group(2)
            link = i.find('a')['href']
            postupci.append('\t'.join([zahvat, nadlezan, link]))
        return postupci


def trazenje_ospuo(url):
    print('tražim OSPUO postupke...')
    sadrzaj = get_sadrzaj(BASE_URL + url, clan=1)

    postupci = []
    for i in sadrzaj.find_all('a'):
        link = i['href']
        tekst = i.parent.parent.parent.parent.find('h3').text.strip()
        postupci.append('\t'.join([tekst, link]))
    return postupci


# PUO postupci
puo_tab = trazenje('puo')

# OPUO postupci
opuo_tab = trazenje('opuo')

# prekogranični PUO postupci
puo_pg_tab = trazenje_prekogranicnih('puo/prekogranicni-postupci-procjene-utjecaja-zahvata-na-okolis.html')

# SPUO postupci, prekogranični
spuo_pg_tab = trazenje_prekogranicnih('spuo/prekogranicni-postupci-strateske-procjene.html')

# SPUO postupci, nadležan MZOIE
SPUO_BASE_URL = 'spuo/postupci-strateske-procjene-nadlezno-tijelo-je-'
url_spuo_min = SPUO_BASE_URL + 'ministarstvo-zastite-okolisa-i-energetike.html'
spuo_min_tab = trazenje_spuo(url_spuo_min, 'MZOIE')

# SPUO postupci, nadležno drugo središnje tijelo ili jedinice JLRS
url_spuo_jlrs = (SPUO_BASE_URL + 'drugo-sredisnje-tijelo-drzavne-uprave'
                 '-ili-jedinica-podrucne-regionalne-ili-lokalne-samouprave.html')
spuo_jlrs_tab = trazenje_spuo(url_spuo_jlrs, 'JLRS')

# OSPUO postupci
ospuo_tab = trazenje_ospuo('spuo/ocjena-o-potrebi-provedbe-strateske-procjene.html')


puosave('output/puo-arhiva-git/')

# čitanje/pisanje arhive
vrijeme = datetime.now()
stamp = vrijeme.strftime('%Y-%m-%d-%H-%M')

arhiva_trenutni = 'output/arhiva/' + stamp + '/'

arhiva_dir = os.listdir('output/arhiva/')
arhiva_dir.sort()

if not arhiva_dir:
    os.mkdir(arhiva_trenutni)
    puosave(arhiva_trenutni)
    sys.exit('prvo pokretanje, nema arhive, snimam snapshot u ' + arhiva_trenutni)

# ako postoji arhiva, usporedba trenutne i posljednje verzije
arhiva_zadnji = 'output/arhiva/' + arhiva_dir[-1] + '/'
puo_old = puoread(arhiva_zadnji, 'puo')
puo_pg_old = puoread(arhiva_zadnji, 'puo_pg')
opuo_old = puoread(arhiva_zadnji, 'opuo')
spuo_min_old = puoread(arhiva_zadnji, 'spuo_min')
spuo_pg_old = puoread(arhiva_zadnji, 'spuo_pg')
spuo_jlrs_old = puoread(arhiva_zadnji, 'spuo_jlrs')
ospuo_old = puoread(arhiva_zadnji, 'ospuo')

# funkcija koja pronalazi razlike između _tab i _old varijabli
diff = []
tabovi = [puo_tab, puo_pg_tab, opuo_tab, spuo_min_tab, spuo_pg_tab, spuo_jlrs_tab, ospuo_tab]
oldies = [puo_old, puo_pg_old, opuo_old, spuo_min_old, spuo_pg_old, spuo_jlrs_old, ospuo_old]
for tab, old in zip(tabovi, oldies):
    razlika = list(set(tab) - set(old))
    diff.extend(razlika)

for i in diff:
    pattern = re.compile('^(.*?) \[PDF\]')
    dijelovi = i.split('\t')
    if re.match(pattern, dijelovi[1]):
        ime_file = re.search(pattern, dijelovi[1]).group(1)
    else:
        ime_file = dijelovi[1]
    ime_file = ime_file[:57] + '...'
    link = dijelovi[-1]

    if len(dijelovi) == 5:
        godina = dijelovi[0][-5:-1]
        kategorija = dijelovi[2]
        free_len = 140 - 3 - len(godina) - len(kategorija)- len(ime_file) - 25
        ime_zahvat = dijelovi[1][:free_len]
        update = '-'.join([godina, ime_zahvat, kategorija, ime_file]) + ' ' + link
    elif len(dijelovi) == 3:
        free_len = 140 - 1 - len(ime_file) - 24
        ime_zahvat = dijelovi[0][:free_len]
        update = ime_zahvat + '-' + ime_file + ' ' + link
    elif len(dijelovi) == 2:
        ime_zahvata = dijelovi[0][:110]
        update = ' '.join([ime_zahvata, link])
    print(update)
    if args.twitter:
        twitter.update_status(status=update)
    print(len(update))

if stamp not in os.listdir('output/arhiva/'):
    os.mkdir(arhiva_trenutni)
puosave(arhiva_trenutni)
