from pymongo import MongoClient
import requests
import asyncio
import aiohttp
from datetime import datetime
#from selenium import webdriver
from time import sleep
#from selenium.webdriver.common.keys import Keys
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
import multiprocessing
from time import time, sleep
import json
from requests.auth import HTTPBasicAuth
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector

import random

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

ERR_4_5 = []

def graber(data, coin_name):
    coin = {}
    plt = 'Error'
    try:
        plt = data.split('<i data-target="favorites.emptyStar"')[1].split('</i>')[1].split('</span>')[0]
        plt = plt.split('people')[0]
        plt = ''.join(plt.split(','))
        plt = int(plt)
    except:
        print('Error ')
    coin[coin_name] = plt
    return coin

def load_mongo():
    db = client.test
    pars_data = db['coins_list']
    data = pars_data.find_one()
    return data.get('urls')

def heandler(url):
    coin_name = url.split('/')[-1]
    data = {}
    headers = { 'User-Agent': UserAgent().random }
    #proxy_auth = str(random.randint(10000, 2147483647)) + ':' + 'passwrd' # TEST
    #proxy = {'http': 'socks5//{}@localhost:9050'.format(proxy_auth), 'https': 'socks5//{}@localhost:9050'.format(proxy_auth)} # TEST
    p = requests.get(url, headers=headers)
    r = requests.get('https://api.ipify.org', headers=headers)
    print('Get ok', p.status_code, 'stats ---- P ', url)
    print('Get ok', r.text)
    if p.status_code == 404:
        ERR_4_5.append((p.status_code, url))
        data[coin_name] = 'Error'
        return data
    if p.status_code != 200:
        i = 0
        while i < 5 and p.status_code != 200:
            print('!!!----------SLEEP STOP----------!!! ---- ', i)
            sleep(4)
            headers = { 'User-Agent': UserAgent().random }
            p = requests.get(url, headers=headers)
            i += 1
        if i == 5 and p.status_code != 200:
            print('!!!!--------------------------------------ERROR SAVE----------------------!!!!')
            ERR_4_5.append(url)
            data[coin_name] = 'Error'
            return data
    data = graber(p.text, coin_name)
    return data

def corusel(links):
    print(multiprocessing.cpu_count(), ' in corusel ----- !')
    with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
        result_data = process.map(heandler, links)
    return result_data

def save_mongo(data):
    db = client.consol_heroku
    pars_data = db['ch_parts']
    data_f = {}
    for unit in data:
        data_f.update(unit)
    d = {'data': data_f}
    pars_data.insert_one(d)


if __name__ == '__main__':
    data = load_mongo()
    data = data[:100]
    #data = run_parser()
    t0 = time()
    print(multiprocessing.cpu_count())
    res_data = corusel(data)
    save_mongo(res_data)
    print(ERR_4_5)
    print('Errors: ', len(ERR_4_5))
    print((time() - t0))
    print('From -- ', len(data), ' -- get -- ', len(res_data))
