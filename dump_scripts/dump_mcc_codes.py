#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

import pandas as pd


if __name__ == "__main__":
    url = 'https://mcc-codes.ru/code'
    r = requests.get(url)
    html_page = r.content

    soup = BeautifulSoup(html_page, 'html.parser')
    table = soup.find(lambda x: x.name == 'table' and
                        x.has_attr('id') and
                        x['id'] == 'all-mcc-table')

    header = table.find(name='thead').find_all('th')
    header = map(lambda x: x.text, header)

    rows = table.find(name='tbody').find_all('tr')
    data = [map(lambda x: x.text, row.find_all('td')) for row in rows]

    df = pd.DataFrame(data, columns=header)
    df.to_csv('mcc_codes_ru.csv', sep=',', encoding='utf-8', index=False)
