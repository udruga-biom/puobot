# -*- coding: utf-8 -*-

"""
puobot
Web robot koji radi katalog PUO i SPUO postupaka
nadležnog ministarstva za zaštitu okoliša i prirode RH
mzec 2017
v 0.2
"""

import argparse
from datetime import datetime
import os
import re
import sys
import requests
from bs4 import BeautifulSoup


BASE_URL = 'http://puo.mzoip.hr/hr/'
IMENA_POSTUPAKA = ['puo', 'puo_pg', 'opuo', 'spuo_min', 'spuo_pg', 'spuo_jlrs', 'ospuo']


def get_twitter_instance():
    """Kreira twitter instancu.

    Instanca se koristi za objavljivanje tweetova o novim postupcima.
    Potrebno je imati autentifikacijske podatke u zasebnoj datoteci.

    Returns:
        twython.Twython instanca.
    """
    import twython
    with open('input/twit_api_data.txt', 'r') as f:
        twython_api_data = f.read().splitlines()
    print('>> Twitter mode')
    return twython.Twython(*twython_api_data)


def kreiranje_foldera():
    """Kreira output foldere kod prvog pokretanja."""
    if 'output' not in os.listdir():
        os.mkdir('output')
    if 'arhiva' not in os.listdir('output'):
        os.mkdir('output/arhiva')
    if 'puo-arhiva-git' not in os.listdir('output'):
        os.mkdir('output/puo-arhiva-git')


def puosave(save_dir, postupci):
    """Snima sve postupke.

    Snimanje svih postupaka u .tsv formatu, u odabrani `save_dir` direktorij.

    Args:
        save_dir (str): relativni path do direktorija za snimanje.
        postupci (list): popis svih postupaka koje se snima.
    """
    for filename, postupak in zip(IMENA_POSTUPAKA, postupci):
        with open(save_dir + filename + '.tsv', 'w', encoding='utf-8') as f:
            f.write('\n'.join(postupak))


def puoread(read_dir):
    """Ucitava postojece postupke.

    Citanje ranije pohranjenih postupaka u .tsv formatu.
    Poziva ju `citanje_arhive` funkcija.

    Args:
        read_dir (str): relativni path do direktorija iz kojeg se cita.
    Returns:
        list: popis postupaka sa sadrzajima datoteka.
    """
    postojeci_postupci = []
    for filename in IMENA_POSTUPAKA:
        with open(read_dir + filename + '.tsv', 'r', encoding='utf-8') as f:
            in_file = f.read().splitlines()
        postojeci_postupci.append(in_file)
    return postojeci_postupci


def get_sadrzaj(full_url, clan=0):
    """Dohvaca sadrzaj s mreznih stranica.

    Args:
        full_url (str): path do mreznih stranica.
        clan (int): indeks clana kojeg se trazi.
    Returns:
        string: sadrzaj zeljenog clana.
    """
    r = requests.get(full_url)
    soup = BeautifulSoup(r.content, 'lxml')
    return soup.find_all('div', 'accordion')[clan]


def get_zahvat(full_url):
    """Trazi ime i kategoriju zahvata.

    Pozivaju je `parse_postupaka` i `parse_alt` funkcije.

    Args:
        full_url (str): path do mreznih stranica.
    Returns:
        tuple: ime i kategorija zahvata.
    """
    sadrzaj = get_sadrzaj(full_url)
    zahvat_ime = sadrzaj.find_all('h3', recursive=False)
    zahvat_kat = sadrzaj.find_all('div', recursive=False)
    return zahvat_ime, zahvat_kat


def trazenje_postupaka(postupak):
    """Trazi PUO/OPUO postupke.

    Obavjestava o trazenju postupka, poziva je `parse_postupaka` funkcija.

    Args:
        postupak (str): postupak koji se trazi, `puo` ili `opuo`.
    Returns:
        list: postupci po godinama.
    """
    print('tražim {} postupke...'.format(postupak.upper()))
    url = BASE_URL + '{}.html'.format(postupak)

    if postupak == 'puo':
        pattern = re.compile('PUO postupci 2[0-9]{3}')
    elif postupak == 'opuo':
        pattern = re.compile('OPUO postupci 2[0-9]{3}')

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    link_elem = (soup.find_all('div', 'four mobile-four columns')[2]
                 .find_all('a', text=pattern))
    return link_elem


def parse_postupaka(postupak):
    """Parsanje postupaka.

    Za svaku pojedinu godinu izvlaci godinu, ime i kategoriju postupka, te
    link. Vraca listu tih vrijednosti.

    Args:
        postupak (str): postupak koji se trazi, `puo` ili `opuo`.
    Returns:
        list: detaljni (godina, ime, kategorija, link) popis svih postupaka.
    """
    link_elem = trazenje_postupaka(postupak)
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


def parse_alt(url):
    """Parsa SPUO i prekogranične postupke.

    Pozivaju je `trazenje_prekogranicnih` i `trazenje_spuo` funkcije.

    Args:
        url (str): relativni path do mreznih stranica.
    Returns:
        list: detaljni (ime, link) popis svih postupaka.
    """
    zahvati = get_zahvat(BASE_URL + url)
    output = []
    for ime, kategorija in zip(*zahvati):
        linkovi = kategorija.find_all('a')
        for linak in linkovi:
            polja = [ime.text.strip(), linak.text.strip(), linak['href']]
            output.append('\t'.join(polja))
    return output


def trazenje_prekogranicnih(url):
    """Trazi prekogranične postupke.

    Obavjestava o trazenju postupka, poziva `parse_alt` funkciju.

    Args:
        url (str): relativni path do mreznih stranica.
    Returns:
        list: detaljni (ime, link) popis svih postupaka.
    """
    postupak = url.split('/')[0]
    print('tražim prekogranične {} postupke...'.format(postupak.upper()))
    return parse_alt(url)


def parse_jlrs(url):
    """Parsa SPUO postupke za koje je nadlezno drugo tijelo ili JLRS.

    Poziva je `trazenje_spuo` funkcija.

    Args:
        url (str): relativni path do mreznih stranica.
    Returns:
        list: detaljni (ime, nadleznost, link) popis svih postupaka.
    """
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


def trazenje_spuo(url, nadleznost):
    """Trazi SPUO postupke.

    Ovisno o tome cija je nadleznost (MZOIE ili drugi), poziva ili
    `parse_alt` ili `parse_jlrs` funkciju.

    Args:
        url (str): relativni path do mreznih stranica.
        nadleznost (str): `MZOIE` ili `JLRS`.
    Returns:
        list: popis postupaka.
    """
    if nadleznost == 'MZOIE':
        print('tražim SPUO postupke za koje je nadležno MZOIE...')
        return parse_alt(url)
    else:
        print('tražim SPUO postupke za koje je nadležno drugo središnje tijelo ili JLRS...')
        return parse_jlrs(url)


def trazenje_ospuo(url):
    """Trazi OSPUO postupke.

    Args:
        url (str): relativni path do mreznih stranica.
    Returns:
        list: popis postupaka.
    """
    print('tražim OSPUO postupke...')
    sadrzaj = get_sadrzaj(BASE_URL + url, clan=1)

    postupci = []
    for i in sadrzaj.find_all('a'):
        link = i['href']
        tekst = i.parent.parent.parent.parent.find('h3').text.strip()
        postupci.append('\t'.join([tekst, link]))
    return postupci


def dohvat_postupaka():
    """Dohvat svih postupaka.

    Returns:
        list: popis svih postupaka.
    """
    puo_tab = parse_postupaka('puo')
    opuo_tab = parse_postupaka('opuo')
    puo_pg_tab = trazenje_prekogranicnih('puo/prekogranicni-postupci'
                                         '-procjene-utjecaja-zahvata-na-okolis.html')
    spuo_pg_tab = trazenje_prekogranicnih('spuo/prekogranicni-postupci-strateske-procjene.html')

    SPUO_BASE_URL = 'spuo/postupci-strateske-procjene-nadlezno-tijelo-je-'
    url_spuo_min = SPUO_BASE_URL + 'ministarstvo-zastite-okolisa-i-energetike.html'
    spuo_min_tab = trazenje_spuo(url_spuo_min, nadleznost='MZOIE')

    url_spuo_jlrs = (SPUO_BASE_URL + 'drugo-sredisnje-tijelo-drzavne-uprave'
                     '-ili-jedinica-podrucne-regionalne-ili-lokalne-samouprave.html')
    spuo_jlrs_tab = trazenje_spuo(url_spuo_jlrs, nadleznost='JLRS')

    ospuo_tab = trazenje_ospuo('spuo/ocjena-o-potrebi-provedbe-strateske-procjene.html')

    postupci = [puo_tab, puo_pg_tab, opuo_tab, spuo_min_tab, spuo_pg_tab, spuo_jlrs_tab, ospuo_tab]
    puosave('output/puo-arhiva-git/', postupci)

    return postupci


def citanje_arhive():
    """Cita podatke iz arhive, ukoliko arhiva postoji.

    Ako arhiva ne postoji, ne ucitava postojece podatke.

    Returns:
        list: popis svih postupaka iz arhive, ukoliko ona postoji.
              U suprotnom vraca None.
    """
    arhiva_dir = os.listdir('output/arhiva/')
    arhiva_dir.sort()

    if not arhiva_dir:
        return None

    arhiva_zadnji = 'output/arhiva/' + arhiva_dir[-1] + '/'
    return puoread(arhiva_zadnji)


def pisanje_arhive(postupci):
    """Sprema nove podatke u arhivu.

    Radi novu mapu "trenutni datum i vrijeme" u koju sprema dohvacene postupke.

    Returns:
        string: ime mape u koju su spremljene datoteke.
    """
    vrijeme = datetime.now()
    stamp = vrijeme.strftime('%Y-%m-%d-%H-%M')

    arhiva_trenutni = 'output/arhiva/' + stamp + '/'
    os.mkdir(arhiva_trenutni)

    puosave(arhiva_trenutni, postupci)
    return arhiva_trenutni


def trazi_razlike(staro, novo):
    """Pronalazi razlike između starih i novih verzija dokumenata.

    Pronadjene razlike printa.
    Ukoliko je prilikom pokretanja programa dodan twitter argument,
    sve uocene novosti objavljuje na twitteru.

    Args:
        staro (list): podatci iz arhive.
        novo (list): dohvaceni podatci.
    """
    razlike = []
    for old, new in zip(staro, novo):
        razlika = set(new) - set(old)
        razlike.extend(list(razlika))

    POCETNI_ZNAKOVI = 60
    pattern = re.compile(r'^(.*?) \[PDF\]')
    novosti = []
    for razlika in razlike:
        dijelovi = razlika.split('\t')
        if re.match(pattern, dijelovi[1]):
            ime_file = re.search(pattern, dijelovi[1]).group(1)
        else:
            ime_file = dijelovi[1]
        link = dijelovi[-1]

        if len(dijelovi) == 5:
            godina = dijelovi[0][-5:-1]
            ime_zahvat = dijelovi[1]
            kategorija = dijelovi[2]
            free_len = 140 - 3 - len(godina) - len(kategorija) - 25

            if ime_zahvat[:POCETNI_ZNAKOVI] == ime_file[:POCETNI_ZNAKOVI]:
                ime_file = ime_file[:free_len]
                update = '|'.join([godina, kategorija, ime_file])
            else:
                ime_file = ime_file[:POCETNI_ZNAKOVI] + '...'
                free_len -= POCETNI_ZNAKOVI + 4
                ime_zahvat = ime_zahvat[:free_len]
                update = '|'.join([godina, ime_zahvat, kategorija, ime_file])

        elif len(dijelovi) == 3:
            ime_zahvat = dijelovi[0]
            free_len = 140 - 1 - 25
            if ime_zahvat[:POCETNI_ZNAKOVI] == ime_file[:POCETNI_ZNAKOVI]:
                update = ime_file[:free_len]
            else:
                ime_file = ime_file[:POCETNI_ZNAKOVI] + '...'
                free_len -= POCETNI_ZNAKOVI + 4
                ime_zahvat = ime_zahvat[:free_len]
                update = '|'.join([ime_zahvat, ime_file])

        elif len(dijelovi) == 2:
            ime_zahvat = dijelovi[0][:110]
            update = ime_zahvat

        update += ' ' + link
        print(update)
        novosti.append(update)
    return novosti


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--twitter', help='optional argument to update twitter')
    args = parser.parse_args()

    kreiranje_foldera()
    novi_postupci = dohvat_postupaka()
    stari_postupci = citanje_arhive()
    folder = pisanje_arhive(novi_postupci)
    if not stari_postupci:
        sys.exit('prvo pokretanje, nema arhive, snapshot snimljen u ' + folder)

    novosti = trazi_razlike(stari_postupci, novi_postupci)

    if args.twitter:
        twitter = get_twitter_instance()
        for novost in novosti:
            twitter.update_status(status=novost)


if __name__ == '__main__':
    main()
