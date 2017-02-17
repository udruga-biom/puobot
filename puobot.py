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

for url_g in link:
    print('obrađujem: ' + url_g)
    r = requests.get(url_g)
    soup = BeautifulSoup(r, 'lxml')


