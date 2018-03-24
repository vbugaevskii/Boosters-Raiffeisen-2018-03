#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs

from time import sleep
from selenium import webdriver

driver = webdriver.Firefox()

driver.get("http://www.banki.ru/banks/")
sleep(5)

elem = driver.find_element_by_xpath('//*[@id="universal-select-region__trigger"]')
elem.click()
sleep(1)

elem = driver.find_element_by_xpath('//*[@id="universal-select-region"]/nav/ul/li[2]')
elem.click()
sleep(1)


def goto_region_tab():
    elems = driver.find_elements_by_class_name('universal-select-region__container')
    for elem in elems:
        if elem.get_attribute('data-tab-id') == '2':
            break
    return elem


regions = goto_region_tab().find_elements_by_class_name('city-column-list-item')
nb_regions = len(regions)

with codecs.open("banki_regions.tsv", mode='w', encoding='utf-8') as f_regions:
    try:
        for region_id in range(nb_regions):
            regions = goto_region_tab().find_elements_by_class_name('city-column-list-item')
            region = regions[region_id].find_element_by_tag_name('a')

            print region.text
            region.click()
            sleep(1.5)

            cities = goto_region_tab().find_elements_by_class_name('city-column-list-item')
            for city in cities:
                city = city.find_element_by_tag_name('a')
                f_regions.write(u'{}\t{}\n'.format(city.text, city.get_attribute('href')))

            driver.find_element_by_link_text(u'Изменить регион').click()
            sleep(1.5)
    finally:
        driver.close()
