#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import codecs

from time import sleep
from selenium import webdriver


def url_format(bank_ids, city, bank_types="all", page=1):
    url_format = "http://www.banki.ru/banks/map/{city}/#/!b1:{bank_ids}!s3:{bank_types}!s4:list!p1:{page}"
    return url_format.format(
        city=city,
        bank_ids=','.join(map(str, bank_ids)),
        bank_types=bank_types,
        page=page
    )


def get_banks_info_multiple(url, driver, is_first_load, n_attempts=5):
    for attempt_i in range(n_attempts):
        try:
            return get_banks_info(url, driver, 15 if is_first_load else 2 + attempt_i)
        except Exception as e:
            print 'An error occurred!'
            print e
            if attempt_i + 1 != n_attempts:
                print 'Another attempt!'
                is_first_load = False
                driver.get("https://ya.ru/")
            else:
                raise e


def get_banks_info(url, driver, t_sleep):
    driver.get(url)
    sleep(t_sleep)

    banks_data = []
    items = driver.find_elements_by_class_name("list__item")

    for item in items[1:]:
        bank_info = {
            'name': item.get_attribute("data-name"),
            'type': item.get_attribute("data-type"),
            'address': item.get_attribute("data-address"),
            'lat': item.get_attribute("data-latitude"),
            'lon': item.get_attribute("data-longitude"),
            'name_bank': item.find_element_by_class_name("item__name__bank").text,
            'access24h': u'круглосуточно' in item.find_element_by_class_name("item__schedule").text.lower()
        }

        if bank_info['lat'] is not None:
            bank_info['lat'] = float(bank_info['lat'])

        if bank_info['lon'] is not None:
            bank_info['lon'] = float(bank_info['lon'])

        bank_info['name'] = re.sub('"', '""', bank_info['name'], flags=re.U)
        bank_info['address'] = re.sub('"', '""', bank_info['address'], flags=re.U)

        banks_data.append(bank_info)

    return banks_data


if __name__ == "__main__":
    banks_list = [63520, 960, 2764, 7292, 4389, 3697, 4725, 193407, 4045]

    driver = webdriver.Firefox()

    city_links = []
    with codecs.open('base_addresses/banki_regions.tsv', mode='r', encoding='utf-8') as f_addresses:
        for line in f_addresses:
            line = line.strip().split('\t')[1]
            line = re.findall(r'banks/(.*?)/list', line)[0]
            city_links.append(line)

    city_links = city_links[city_links.index('sverdlovskaya_oblast~/tretiy_severnyiy'):]

    city_links.extend([
        'moskva_i_oblast~/pavlovskiy_posad',
        'tul~skaya_oblast~/osinovaya_gora',
        'moskva_i_oblast~/sluchaynyiy',
        'moskva_i_oblast~/poselok_sovhoza_imeni_lenina',
        'respublika_tatarstan/malaya_shil~na',
        'sankt-peterburg_i_oblast~/villozskoe',
        'nizhegorodskaya_oblast~/vyiezdnoe',
        'chelyabinskaya_oblast~/nagornyiy',
        'sankt-peterburg_i_oblast~/poselok_imeni_morozova',
        'sverdlovskaya_oblast~/istok'
    ])

    f_addresses = codecs.open('base_bankiru.csv', mode='a', encoding='utf-8')
    lines_format = u'{name_bank},"{name}",{type},"{address}",{lat},{lon},{access24h}\n'
    # f_addresses.write(u'bank,name,type,address,lat,lon,access24h\n')

    is_first = True

    try:
        page_id = 1

        for city in city_links:
            while True:
                url = url_format(banks_list, city, page=page_id)
                print url

                banks_info_batch = get_banks_info_multiple(url, driver, is_first)
                is_first = False

                if len(banks_info_batch) > 0:
                    for bank_info in banks_info_batch:
                        f_addresses.write(lines_format.format(**bank_info))
                else:
                    break

                page_id += 1

                driver.get("https://ya.ru/")
                sleep(0.5)
            page_id = 1
    finally:
        f_addresses.close()
        driver.close()
