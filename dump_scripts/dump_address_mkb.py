#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import codecs

import requests
from bs4 import BeautifulSoup


def get_banks_info(url, type_):
    r = requests.get(url)

    html_page = r.content

    soup = BeautifulSoup(html_page, 'html.parser')
    bank_info = {
        'name': soup.find_all('h1')[0].text,
        'address': soup.find_all('div', class_='branch__address')[0].text.strip(),
        'type': type_,
        'name_bank': u'Московский Кредитный Банк',
        'lat': '',
        'lon': ''
    }

    timetable = soup.find_all('div', class_='branch__info-col branch__info-col_descr')[0].text.lower()
    bank_info['access24h'] = u'круглосуточно' in timetable

    scripts = soup.find_all('script', type='text/javascript')
    for script in scripts:
        script = str(script)
        if 'coordinates' in script:
            coords = re.findall(r'var coordinates = \{lat: (\d+\.?\d*), lng: (\d+\.?\d*)\};', script)[0]
            bank_info['lat'], bank_info['lon'] = map(float, coords)

    bank_info['name'] = re.sub('"', '""', bank_info['name'], flags=re.U)
    bank_info['address'] = re.sub('"', '""', bank_info['address'], flags=re.U)

    return bank_info


if __name__ == '__main__':
    lines_format = u'{name_bank},"{name}",{type},"{address}",{lat},{lon},{access24h}\n'

    with codecs.open('base_addresses/base_mkb.csv', mode='w', encoding='utf-8') as f_addresses:
        f_addresses.write(u'bank,name,type,address,lat,lon,access24h\n')

        for i in range(1, 2000):
            url = 'https://mkb.ru/about/address/atm/{}'.format(i)
            print url
            try:
                bank_info = get_banks_info(url, 'atm')
                f_addresses.write(lines_format.format(**bank_info))
            except:
                print "Atm with id={} is not found".format(i)

        for i in range(1, 1000):
            url = 'https://mkb.ru/about/address/branch/{}'.format(i)
            print url
            try:
                bank_info = get_banks_info(url, 'office')
                f_addresses.write(lines_format.format(**bank_info))
            except:
                print "Atm with id={} is not found".format(i)
