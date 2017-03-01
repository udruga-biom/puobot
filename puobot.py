"""
puobot
Web robot koji radi katalog PUO i SPUO postupaka
nadležnog ministarstva za zaštitu okoliša i prirode RH
mzec 2017
v 0.1
"""

# -*- coding: utf-8 -*-
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
        twython_api_data = f.readlines()
    twitter = twython.Twython(twython_api_data[0].strip(),
                              twython_api_data[1].strip(),
                              twython_api_data[2].strip(),
                              twython_api_data[3].strip())
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

# funkcija za snimanje i čitanje
def puosave(save_dir):
    with open(save_dir + 'puo.tsv', 'w') as f:
        f.write('\n'.join(puo_tab))
    with open(save_dir + 'puo_pg.tsv', 'w') as f:
        f.write('\n'.join(puo_pg_tab))
    with open(save_dir + 'opuo.tsv', 'w') as f:
        f.write('\n'.join(opuo_tab))
    with open(save_dir + 'spuo_min.tsv', 'w') as f:
        f.write('\n'.join(spuo_min_tab))
    with open(save_dir + 'spuo_pg.tsv', 'w') as f:
        f.write('\n'.join(spuo_pg_tab))
    with open(save_dir + 'spuo_jlrs.tsv', 'w') as f:
        f.write('\n'.join(spuo_jlrs_tab))
    with open(save_dir + 'ospuo.tsv', 'w') as f:
        f.write('\n'.join(ospuo_tab))

def puoread(read_dir):
    with open(read_dir + 'puo.tsv', 'r') as f:
        puo = f.read().splitlines()
    with open(read_dir + 'puo_pg.tsv', 'r') as f:
        puo_pg = f.read().splitlines()
    with open(read_dir + 'opuo.tsv', 'r') as f:
        opuo = f.read().splitlines()
    with open(read_dir + 'spuo_min.tsv', 'r') as f:
        spuo_min = f.read().splitlines()
    with open(read_dir + 'spuo_pg.tsv', 'r') as f:
        spuo_pg = f.read().splitlines()
    with open(read_dir + 'spuo_jlrs.tsv', 'r') as f:
        spuo_jlrs = f.read().splitlines()
    with open(read_dir + 'ospuo.tsv', 'r') as f:
        ospuo = f.read().splitlines()
    return(puo, puo_pg, opuo, spuo_min, spuo_pg, spuo_jlrs, ospuo)

# funkcija za parse PUO/OPUO
def puoscrape(urlname, postupak='puo'):
    r = requests.get(urlname)

    url = 'http://puo.mzoip.hr'
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
        zahvat_imena = sadrzaj.find_all('h3', recursive=False)
        zahvat_kategorija = sadrzaj.find_all('div', recursive=False)
        if len(zahvat_imena) != len(zahvat_kategorija):
            print('broj zahvata i kategorija se ne podudara')
        else:
            for ime, zahvacena_kategorija in zip(zahvat_imena, zahvat_kategorija):
                kategorije = zahvacena_kategorija.find_all('h3')
                for kat_index, kategorija in enumerate(kategorije):
                    linkovi = (zahvacena_kategorija
                               .find_all('ul', 'docs')[kat_index]
                               .find_all('a'))
                    for linak in linkovi:
                        output.append(godina.text.strip() + '\t' +
                                      ime.text.strip() + '\t' +
                                      kategorija.text.strip() + '\t' +
                                      linak.text.strip() + '\t' +
                                      linak['href'])
    return output

# funkcija za parse SPUO i prekograničnih postupaka
def puoscrape_alt(urlname):
    r = requests.get(urlname)
    soup = BeautifulSoup(r.content, 'lxml')
    output = []
    sadrzaj = soup.find_all('div', 'accordion')[0]
    zahvat_ime = sadrzaj.find_all('h3', recursive = False)
    zahvat_kat = sadrzaj.find_all('div', recursive = False)
    for zahvat in range(len(zahvat_ime)):
        linkovi = zahvat_kat[zahvat].find_all('a')
        for linak in range(len(linkovi)):
            output.append(zahvat_ime[zahvat].text.strip() + '\t' +
                              linkovi[linak].text.strip() + '\t' +
                              linkovi[linak]['href'])
    return(output)



# PUO postupci
print('tražim PUO postupke...')

url_puo = 'http://puo.mzoip.hr/hr/puo.html'
puo_tab = puoscrape(url_puo, 'puo')

# OPUO postupci
print('tražim OPUO postupke...')

url_opuo = 'http://puo.mzoip.hr/hr/opuo.html'
opuo_tab = puoscrape(url_opuo, 'opuo')

# prekogranični PUO postupci
print('tražim prekogranične PUO postupke...')

url_pg = 'http://puo.mzoip.hr/hr/puo/prekogranicni-postupci-procjene-utjecaja-zahvata-na-okolis.html'
puo_pg_tab = puoscrape_alt(url_pg)

# SPUO postupci, nadležan MZOIE
print('tražim SPUO postupke za koje je nadležno MZOIE...')

url_spuo = 'http://puo.mzoip.hr/hr/spuo.html'
url_spuo_min = 'http://puo.mzoip.hr/hr/spuo/postupci-strateske-procjene-nadlezno-tijelo-je-ministarstvo-zastite-okolisa-i-energetike.html'
spuo_min_tab = puoscrape_alt(url_spuo_min)

# SPUO postupci, prekogranični
print('tražim prekogranične SPUO postupke...')

url_spuo_pg = 'http://puo.mzoip.hr/hr/spuo/prekogranicni-postupci-strateske-procjene.html'
spuo_pg_tab = puoscrape_alt(url_spuo_pg)

# SPUO postupci, nadležno drugo središnje tijelo ili jedinice JLRS
print('tražim SPUO postupke za koje je nadležno drugo središnje tijelo ili JLRS...')

url_spuo_jlrs = 'http://puo.mzoip.hr/hr/spuo/postupci-strateske-procjene-nadlezno-tijelo-je-drugo-sredisnje-tijelo-drzavne-uprave-ili-jedinica-podrucne-regionalne-ili-lokalne-samouprave.html'
r = requests.get(url_spuo_jlrs)
soup = BeautifulSoup(r.content, 'lxml')
sadrzaj = soup.find_all('h2', text = re.compile('Postupci stra.*'))[0].parent.parent.find_all('ul')[1]

spuo_jlrs_tab = []
for i in sadrzaj.find_all('li'):
    zahvat = re.search('^(.*?)(Nadle.*?)http.*', i.text).group(1)
    nadlezan = re.search('^(.*?)(Nadle.*?)http.*', i.text).group(2)
    link = i.find('a')['href']
    spuo_jlrs_tab.append(zahvat + '\t' +
                         nadlezan + '\t' +
                         link)

# OSPUO postupci
print('tražim OSPUO postupke...')

url_ospuo = 'http://puo.mzoip.hr/hr/spuo/ocjena-o-potrebi-provedbe-strateske-procjene.html'
r = requests.get(url_ospuo)
soup = BeautifulSoup(r.content, 'lxml')
sadrzaj = soup.find_all('div', 'accordion')[1]

ospuo_tab = []
for i in sadrzaj.find_all('a'):
    link = i['href']
    tekst = i.parent.parent.parent.parent.find('h3').text.strip()
    ospuo_tab.append(tekst + '\t' + link)

puosave('output/puo-arhiva-git/')

# čitanje/pisanje arhive
vrijeme = datetime.now()
stamp = vrijeme.strftime('%Y-%m-%d-%H-%M')

arhiva_trenutni = 'output/arhiva/' + stamp + '/'

try:
    arhiva_dir = os.listdir('output/arhiva/')
    arhiva_dir.sort(reverse = True)
except OSError:
    os.mkdir(arhiva_trenutni)
    puosave(arhiva_trenutni)
    sys.exit('prvo pokretanje, nema arhive, snimam snapshot u output/arhiva/' + stamp + '/')

if arhiva_dir is None or arhiva_dir == []:
    os.mkdir(arhiva_trenutni)
    puosave(arhiva_trenutni)
    sys.exit('prvo pokretanje, nema arhive, snimam snapshot u output/arhiva/' + stamp + '/')

# ako postoji arhiva, usporedba trenutne i posljednje verzije
arhiva_zadnji = 'output/arhiva/' + arhiva_dir[0] + '/'
puo_old, puo_pg_old, opuo_old, spuo_min_old, spuo_pg_old, spuo_jlrs_old, ospuo_old = puoread(arhiva_zadnji)

# funkcija koja pronalazi razlike između _tab i _old varijabli
diff = []
diff= list(set(puo_tab) - set(puo_old)) +\
      list(set(puo_pg_tab) - set(puo_pg_old)) +\
      list(set(opuo_tab) - set(opuo_old)) +\
      list(set(spuo_min_tab) - set(spuo_min_old)) +\
      list(set(spuo_pg_tab) - set(spuo_pg_old)) +\
      list(set(spuo_jlrs_tab) - set(spuo_jlrs_old)) +\
      list(set(ospuo_tab) - set(ospuo_old))

for i in diff:
    pattern = re.compile('^(.*?) \[PDF\]')
    dijelovi = i.split('\t')
    if len(dijelovi) == 5:
        godina = dijelovi[0][-5:-1]
        kategorija = dijelovi[2]
        if re.match(pattern, dijelovi[1]):
            ime_file = re.search(pattern, dijelovi[1]).group(1)
        else:
            ime_file = dijelovi[1]
        ime_file = ime_file[:57] + '...'
        free_len = 140 - 3 - len(godina) - len(kategorija)- len(ime_file) - 25
        ime_zahvat = dijelovi[1][:free_len]
        link = dijelovi[4]
        update = godina + '-' + ime_zahvat + '-' + kategorija + '-' + ime_file + ' ' + link
    elif len(dijelovi) == 3:
        if re.match(pattern, dijelovi[1]):
            ime_file = re.search(pattern, dijelovi[1]).group(1)
        else:
            ime_file = dijelovi[1]
        ime_file = ime_file[:57] + '...'
        free_len = 140 - 1 - len(ime_file) - 24
        ime_zahvat = dijelovi[0][:free_len]
        link = dijelovi[2]
        update = ime_zahvat + '-' + ime_file + ' ' + link
    elif len(dijelovi) == 2:
        ime_zahvata = dijelovi[0][:110]
        link = dijelovi[1]
        update = ime_zahvata + ' ' + link
    print(update)
    if args.twitter:
        twitter.update_status(status = update)
    print(len(update))

os.mkdir(arhiva_trenutni)
puosave(arhiva_trenutni)
