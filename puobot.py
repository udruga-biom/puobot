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

# funkcija za parse PUO/OPUO
def puoscrape(urlname, postupak = 'puo'):
    r = requests.get(urlname)
    
    if postupak == 'puo':
        pattern = re.compile('PUO postupci 2[0-9]{3}')
    elif postupak == 'opuo':
        pattern = re.compile('OPUO postupci 2[0-9]{3}')
    
    soup = BeautifulSoup(r.content, 'lxml')
    link_elem = soup.find_all('div', 'four mobile-four columns')[2]\
                    .find_all('a', text = pattern)
    
    output = []
    for godina in range(len(link_elem)):
        print(link_elem[godina].text.strip())
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
                        output.append(link_elem[godina].text.strip() + '\t' +
                                      zahvat_ime[zahvat].text.strip() + '\t' +
                                      kategorije[kategorija].text.strip() + '\t' +
                                      linkovi[linak].text.strip() + '\t' +
                                      linkovi[linak]['href'])
    return(output)

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

url = 'http://puo.mzoip.hr'

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


# Snimanje
with open('output/puo.tsv', 'w') as f:
    f.write('\n'.join(puo_tab))
with open('output/puo_pg.tsv', 'w') as f:
    f.write('\n'.join(puo_pg_tab))
with open('output/opuo.tsv', 'w') as f:
    f.write('\n'.join(opuo_tab))
with open('output/spuo_min.tsv', 'w') as f:
    f.write('\n'.join(spuo_min_tab))
with open('output/spuo_pg.tsv', 'w') as f:
    f.write('\n'.join(spuo_pg_tab))
with open('output/spuo_jlrs.tsv', 'w') as f:
    f.write('\n'.join(spuo_jlrs_tab))
with open('output/ospuo.tsv', 'w') as f:
    f.write('\n'.join(ospuo_tab))
