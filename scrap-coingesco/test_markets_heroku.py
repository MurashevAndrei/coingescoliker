import os
import requests
from datetime import datetime
from fake_useragent import UserAgent
import multiprocessing
from time import time, sleep
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient
import random


client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")
ERR_4_5 = {}
ERR_EXCH = []

def api_exchanges():
    headers = {
        'accept': 'application/json',
    }
    response = requests.get('https://api.coingecko.com/api/v3/exchanges/list', headers=headers)
    return response.json()

def add_links(data):
    main_page = 'https://www.coingecko.com/en/exchanges/'
    data_dict = {}
    for i in data:
        i['url'] = main_page + i['id']
        data_dict[i['id']] = {'url': main_page + i['id']}
    return data_dict

def save_mongo(data, name):
    db = client.markets
    markets_db = db[name]
    markets_db.delete_many({})
    if name == 'list_exchanges':
        markets_db.insert_one(data)
    else:
        markets_db.insert_many(data)

def restore(data):
    data_f = {}
    for unit in data:
        data_f.update(unit)
    return data_f

def restore_list(data):
    data_f = []
    for unit in data:
        if unit != 'Error':
            data_f.extend(unit)
    return data_f

def heandler(url):
    exch_name = url.split('/')[-1]
    data = {}
    proxies = {
        'http': '//vvyyimhm:vu4t6rhgy97x @{}'.format(random.choice(PROXIES_LIST)),
        'https': '//vvyyimhm:vu4t6rhgy97x @{}'.format(random.choice(PROXIES_LIST))
    }
    try:
        headers = { 'User-Agent': UserAgent().random }
        p = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        if p.status_code == 404:
            data[exch_name] = 0
            return data
        if p.status_code != 200:
            i = 0
            while i < 5 and p.status_code != 200:
                print('!!!----------STOP----------!!! ---- ', i)
                headers = { 'User-Agent': UserAgent().random }
                proxies = {
                    'http': '//vvyyimhm:vu4t6rhgy97x @{}'.format(random.choice(PROXIES_LIST)),
                    'https': '//vvyyimhm:vu4t6rhgy97x @{}'.format(random.choice(PROXIES_LIST))
                }
                p = requests.get(url, headers=headers, proxies=proxies, timeout=10)
                i += 1
            if i == 5 and p.status_code != 200:
                #print('!!!!--------------------------------------ERROR SAVE----------------------!!!!')
                ERR_4_5[exch_name] = p.status_code
                data[exch_name] = 0
                return data
        p = p.text
        soup = BeautifulSoup(p, 'lxml')
        el_div = soup.findAll("div", {"class": "px-4 text-center py-2 py-lg-0"})
        data[exch_name] = int(el_div[-1].div.next)
    except:
        print('except')
        data[exch_name] = 0
    return data

def heandler_2(url):
    var_list = []
    exch_name = url.split('/show_more')[0].split('/')[-1]
    proxies = {
        'http': '//vvyyimhm:vu4t6rhgy97x @{}'.format(random.choice(PROXIES_LIST)),
        'https': '//vvyyimhm:vu4t6rhgy97x @{}'.format(random.choice(PROXIES_LIST))
    }
    try:
        headers = { 'User-Agent': UserAgent().random }
        p = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        if p.status_code == 404:
            return 'Error'
        if p.status_code != 200:
            i = 0
            while i < 5 and p.status_code != 200:
                print('!!!----------STOP----------!!! ---- ', i)
                proxies = {
                    'http': '//vvyyimhm:vu4t6rhgy97x @{}'.format(random.choice(PROXIES_LIST)),
                    'https': '//vvyyimhm:vu4t6rhgy97x @{}'.format(random.choice(PROXIES_LIST))
                }
                headers = { 'User-Agent': UserAgent().random }
                p = requests.get(url, headers=headers, proxies=proxies, timeout=10)
                i += 1
            if i == 5 and p.status_code != 200:
                #print('!!!!--------------------------------------ERROR SAVE----------------------!!!!')
                ERR_4_5[exch_name] = p.status_code
                return 'Error'
        p = p.text
        soup = BeautifulSoup(p, 'lxml')
        el_div = soup.findAll("tr")
        for tr in el_div:
            var_dict = {}
            var_dict['exchange'] = exch_name
            td = tr.findAll('td')
            var_dict['coin_name'] = td[1].text.strip()
            var_dict['pair'] = td[3].text.strip()
            var_dict['price'] = td[4].text.strip().split('$')[1].split('\n\n')[0]
            if var_dict['price'] != '-' and var_dict['price'] != '':
                var_dict['price'] = float(var_dict['price'].replace(',', ''))
            var_dict['spread'] = td[5].text.strip()
            if var_dict['spread'] != '-' and var_dict['spread'] != '':
                var_dict['spread'] = float(var_dict['spread'].replace('%', ''))
            var_dict['depth+per2'] = td[6].text.strip()
            if var_dict['depth+per2'] != '-' and var_dict['depth+per2'] != '':
                var_dict['depth+per2'] = float(var_dict['depth+per2'].replace('$', '').replace(',', ''))
            var_dict['depth-per2'] = td[7].text.strip()
            if var_dict['depth-per2'] != '-' and var_dict['depth-per2'] != '':
                var_dict['depth-per2'] = float(var_dict['depth-per2'].replace('$', '').replace(',', ''))
            if ',' in td[8].text:
                var_dict['volume_ex'] = float(td[8].text.strip().split('$')[1].split('\n')[0].replace(',',''))
            else:
                var_dict['volume_ex'] = float(td[8].text.strip().split('$')[1].split('\n')[0])
            if td[2].text.strip() == '':
                var_dict['total_volume'] = 0
            elif ',' in td[2].text:
                var_dict['total_volume'] = round(float(td[2].text.strip().split('$')[1].replace(',','')), 2)
            else:
                var_dict['total_volume'] = round(float(td[2].text.strip().split('$')[1]), 2)
            if var_dict['total_volume'] != 0:
                var_dict['volume_per'] = round(var_dict['volume_ex']/var_dict['total_volume']*100, 2)
            else:
                var_dict['volume_per'] = 0
            var_list.append(var_dict)
        return var_list
    except:
        return 'Error'


def corusel(links, var):
    if var == 1:
        result_dict = {}
        with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
            result_data = process.map(heandler, links)
        result_dict = restore(result_data)
        return result_dict
    elif var == 2:
        result_list = []
        with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
            result_data = process.map(heandler_2, links)
        result_list = restore_list(result_data)
        return result_list

def get_total_coins(exch):
    """Get dict of all exchanges and return all coins for each exchanges."""
    urls = []
    for ex in exch:
        urls.append(exch[ex]['url'])
    page = corusel(urls, 1)

def create_links(val, exch_name):
    i = 0
    main_page = 'https://www.coingecko.com/en/exchanges/'
    if val != 0:
        pages = val // 100
        data_links = []
        while i != (pages+1):
            data_links.append('{}{}/show_more_tickers?page={}&per_page=100&verified_ticker=true'.format(main_page, exch_name, i))
            i = i + 1
        return data_links
    return []

def get_total_coins(exch):
    """Get dict of all exchanges and return all coins for each exchanges. Use iohttp"""
    urls = []
    for ex in exch:
        urls.append(exch[ex]['url'])
    return urls

def get_urls_list(pair):
    urls = []
    for key in pair:
        urls.extend(create_links(pair.get(key), key))
    return urls

def get_proxies_list(file_name):
    try:
        with open(file_name, 'r') as f:
            res = f.readlines()
        i = 0
        proxies_list = []
        while i<len(res):
            proxies_list.append(res[i].split(':vvyyimhm')[0])
            i+=1
        print('List proxies load')
        return proxies_list
    except:
        print('List proxies did not load')
        return

if __name__ == '__main__':
    PROXIES_LIST = get_proxies_list('Webshare')
    exch_dict = add_links(api_exchanges())
    t0 = time()
    res_data = corusel(get_total_coins(exch_dict), 1)
    all_urls = get_urls_list(res_data)
    result_parse = corusel(all_urls, 2)
    save_mongo(result_parse, 'markets_data')
    save_mongo(exch_dict, 'list_exchanges')
    print((time() - t0))
