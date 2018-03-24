#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import codecs

from time import sleep
from selenium import webdriver


def get_banks_address_office(url):
    banks_info = []

    driver.get(url)

    # Прокликивать каждый элемент совсем необязательно :)
    """
    n_banks = len(driver.find_elements_by_class_name('b-office'))

    for bank_i in range(n_banks):
        bank_chosen = driver.find_elements_by_class_name('b-office-link')[bank_i]
        bank_chosen.click()

    sleep(1)
    """

    items = driver.find_elements_by_class_name('b-office')

    for item in items:
        bank_short = item.find_element_by_class_name('b-office-short')
        bank_full = item.find_element_by_class_name('b-office-full')

        bank_info = {
            'name': bank_short.find_element_by_class_name('b-office-col-twice').
                find_element_by_tag_name('h3').text,
            'address': bank_short.find_element_by_class_name('b-office-col-twice').
                find_element_by_tag_name('p').text,
            'type': 'office',
            'name_bank': u'Россельхозбанк',
            'access24h': False
        }

        bank_l_column = bank_full.find_element_by_class_name('b-office-full-left')

        coords = bank_l_column.find_element_by_class_name('b-office-full-map').get_attribute('data-center')
        coords = map(lambda x: float(x.strip()), coords.split(','))
        bank_info['lat'], bank_info['lon'] = coords

        bank_info['name'] = re.sub('"', '""', bank_info['name'], flags=re.U)
        bank_info['address'] = re.sub('"', '""', bank_info['address'], flags=re.U)

        banks_info.append(bank_info)

    return banks_info


def get_banks_address_atm(url):
    banks_info = []

    driver.get(url)

    # Прокликивать каждый элемент совсем необязательно :)
    """
    n_banks = len(driver.find_elements_by_class_name('b-atm'))

    for bank_i in range(n_banks):
        bank_chosen = driver.find_elements_by_class_name('b-atm-link')[bank_i]
        bank_chosen.click()

    sleep(1)
    """

    items = driver.find_elements_by_class_name('b-atm')
    for item in items:
        bank_short = item.find_element_by_class_name('b-atm-short')
        bank_full = item.find_element_by_class_name('b-office-full')

        bank_info = {
            'name': bank_short.find_element_by_class_name('b-atm-col1').
                find_element_by_tag_name('p').text,
            'address': bank_short.find_element_by_class_name('b-atm-col1').
                find_element_by_class_name('b-atm-link').text,
            'type': 'atm',
            'name_bank': u'Россельхозбанк',
            'access24h': u'круглосуточно' in bank_short.find_element_by_class_name('b-atm-col2').text.lower(),
        }

        bank_l_column = bank_full.find_element_by_class_name('b-office-full-left')

        coords = bank_l_column.find_element_by_class_name('b-office-full-map').get_attribute('data-center')
        coords = map(lambda x: float(x.strip()), coords.split(','))
        bank_info['lat'], bank_info['lon'] = coords

        bank_info['name'] = re.sub('"', '""', bank_info['name'], flags=re.U)
        bank_info['address'] = re.sub('"', '""', bank_info['address'], flags=re.U)

        banks_info.append(bank_info)

    return banks_info


def get_banks_address(url, type_, n_attempts=5):
    func = {
        'atm': get_banks_address_atm,
        'office': get_banks_address_office
    }

    for attempt_i in range(n_attempts):
        try:
            return func[type_](url)
        except Exception as e:
            print 'An error occurred!'
            print e
            if attempt_i + 1 != n_attempts:
                print 'Another attempt!'
            else:
                raise e


if __name__ == '__main__':
    f_addresses = codecs.open('base_addresses/base_rshb.csv', mode='w', encoding='utf-8')

    driver = webdriver.Firefox()

    try:
        lines_format = u'{name_bank},"{name}",{type},"{address}",{lat},{lon},{access24h}\n'
        f_addresses.write(u'bank,name,type,address,lat,lon,access24h\n')

        url = 'https://www.rshb.ru/offices/moscow/'
        driver.get(url)

        regions = driver.find_element_by_class_name('b-city-select-label').click()
        sleep(1)

        regions = driver.find_element_by_class_name('b-branches').\
            find_elements_by_class_name('b-branches-item-link')
        regions = map(lambda x: x.get_attribute('data-branch-code'), regions)

        region_id = None
        bank_id = None

        while True:
            if region_id is None:
                region_id = -1
            region_id += 1

            if region_id >= len(regions):
                break

            if (region_id + 1) % 10 == 0:
                # Перезагрузи webdriver, т.к. очень много кушает ОЗУ данный сайт
                driver.close()
                driver = webdriver.Firefox()

            url = 'https://www.rshb.ru/{type}s/{region}/'.format(type='office', region=regions[region_id])
            print region_id, url
            banks_info_batch = get_banks_address(url, 'office')
            print "Dumped:", len(banks_info_batch)

            for bank_info in banks_info_batch:
                f_addresses.write(lines_format.format(**bank_info))

            url = 'https://www.rshb.ru/{type}s/{region}/'.format(type='atm', region=regions[region_id])
            print region_id, url
            banks_info_batch = get_banks_address(url, 'atm')
            print "Dumped:", len(banks_info_batch)

            for bank_info in banks_info_batch:
                f_addresses.write(lines_format.format(**bank_info))

    finally:
        f_addresses.close()
        driver.close()
