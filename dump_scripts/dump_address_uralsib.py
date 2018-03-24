#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import codecs

from time import sleep

from selenium import webdriver


def get_banks_info(index, type_):
    banks_data = []

    url = 'https://www.uralsib.ru/bank/{}s/list.wbp?region={}'.format(type_, 100000000 + index)
    print url

    driver.get(url)
    sleep(2)

    region = driver.find_element_by_id('locator-toolbar'). \
        find_element_by_css_selector('div.item.place'). \
        find_element_by_css_selector('input.control.toolbox').\
        get_attribute('value')

    items = driver.find_element_by_id('locator-branches')
    items = items.find_elements_by_class_name('vcard')
    for item in items:
        if item.get_attribute('data-company-id') != 'uralsib':
            continue

        bank_info = {
            'name': item.find_element_by_css_selector('span.fn.org.title').text,
            'type': type_,
            'name_bank': u'Банк Уралсиб',
            'access24h': 'access-24h' in item.get_attribute('class').split(),
            'lat': '',
            'lon': ''
        }

        address = [
            region,
            item.find_element_by_class_name('locality').text,
            item.find_element_by_class_name('street-address').text
        ]
        address = ', '.join(address)
        bank_info['address'] = address

        for coords in item.find_elements_by_tag_name('a'):
            coords = coords.get_attribute('href')
            if 'map.wbp' in coords:
                lats = re.findall(r'lat=(\d+\.?\d*)', coords, flags=re.U)
                bank_info['lat'] = float(lats[0]) if len(lats) > 0 else ''

                lons = re.findall(r'lng=(\d+\.?\d*)', coords, flags=re.U)
                bank_info['lon'] = float(lons[0]) if len(lons) > 0 else ''

                break

        bank_info['name'] = re.sub('"', '""', bank_info['name'], flags=re.U)
        bank_info['address'] = re.sub('"', '""', bank_info['address'], flags=re.U)

        banks_data.append(bank_info)

    return banks_data


if __name__ == "__main__":
    lines_format = u'{name_bank},"{name}",{type},"{address}",{lat},{lon},{access24h}\n'

    f_addresses = codecs.open('base_addresses/base_uralsib.csv', mode='w', encoding='utf-8')
    f_addresses.write(u'bank,name,type,address,lat,lon,access24h\n')

    driver = webdriver.Firefox()

    for type_ in ['office', 'atm']:
        for index in range(1, 80):
            banks_info_batch = get_banks_info(index, type_)

            if len(banks_info_batch) > 0:
                for bank_info in banks_info_batch:
                    f_addresses.write(lines_format.format(**bank_info))

    driver.close()

    f_addresses.close()
