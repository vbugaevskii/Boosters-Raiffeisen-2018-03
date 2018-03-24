#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import codecs

import requests
from bs4 import BeautifulSoup


def url_format(city, type_):
    url = 'http://www.energotransbank.com/about/contacts/{city}/{city}/{type}/'.format(
        city=city, type=type_
    )
    return url


def get_banks_info(url, type_):
    banks_data = []

    r = requests.get(url)
    html_page = r.content

    soup = BeautifulSoup(html_page, 'html.parser')
    items = soup.find_all('ul', class_="coords")
    items = items[0].find_all('li')

    for item in items:
        bank_info = {
            'name': item['data-jcode'],
            'type': type_,
            'lat': float(item['data-coords'].split(',')[0]),
            'lon': float(item['data-coords'].split(',')[1]),
            'name_bank': u'Энерготрансбанк'
        }

        address = item.find_all('div', class_='address')[0].text
        address = address.strip().split('\n')[0]
        bank_info['address'] = address.strip()

        timetable = item.find_all('table')
        if len(timetable) > 0:
            timetable = ' '.join(map(lambda x: x.text, timetable)).lower()
        else:
            timetable = ''

        bank_info['access24h'] = u'круглосуточно' in timetable
        bank_info['name'] = re.sub('"', '""', bank_info['name'], flags=re.U)
        bank_info['address'] = re.sub('"', '""', bank_info['address'], flags=re.U)

        banks_data.append(bank_info)

    return banks_data


if __name__ == "__main__":
    lines_format = u'{name_bank},"{name}",{type},"{address}",{lat},{lon},{access24h}\n'

    f_addresses = codecs.open('base_addresses/base_energotrans.csv', mode='w', encoding='utf-8')
    f_addresses.write(u'bank,name,type,address,lat,lon,access24h\n')

    for city in ['Moscow', 'St.+Petersburg', 'Kaliningrad']:
        for name, type_ in [('terminaly', 'atm'), ('bankomaty', 'atm'), ('podrazdeleniya', 'office')]:
            url = url_format(city, name)
            print url

            banks_info_batch = get_banks_info(url, type_)
            if len(banks_info_batch) > 0:
                for bank_info in banks_info_batch:
                    f_addresses.write(lines_format.format(**bank_info))

    f_addresses.close()
