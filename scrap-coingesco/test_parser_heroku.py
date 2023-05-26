import get_links_with_API
from pymongo import MongoClient
import requests
from datetime import datetime
from time import sleep
from fake_useragent import UserAgent
import multiprocessing
from time import time, sleep
import json
from requests.auth import HTTPBasicAuth
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector

import random

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

ERR_4_5 = {}

def run_parser():
    data = get_links_with_API.get_links_for_parse()
    return data

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

def heandler(url):
    coin_name = url.split('/')[-1]
    data = {}
    try:
        headers = { 'User-Agent': UserAgent().random }
        p = requests.get(url, headers=headers)
        if p.status_code == 404:
            ERR_4_5[coin_name] = p.status_code
            data[coin_name] = 'Error'
            return data
        if p.status_code != 200:
            i = 0
            while i < 5 and p.status_code != 200:
                #print('!!!----------SLEEP STOP----------!!! ---- ', i)
                sleep(4)
                headers = { 'User-Agent': UserAgent().random }
                p = requests.get(url, headers=headers)
                i += 1
            if i == 5 and p.status_code != 200:
                #print('!!!!--------------------------------------ERROR SAVE----------------------!!!!')
                ERR_4_5[coin_name] = p.status_code
                data[coin_name] = 'Error'
                return data
        data = graber(p.text, coin_name)
    except:
        data[coin_name] = 'Error'
    return data

def corusel(links):
    #print(multiprocessing.cpu_count(), ' in corusel ----- !')
    with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
        result_data = process.map(heandler, links)
    return result_data

def save_mongo(coin):
    date_t = datetime.utcnow()
    dict_for_save = {}
    dict_for_save['_id'] = date_t.strftime("%Y-%m-%d_%H:%M")
    dict_for_save['data'] = coin
    db = client.test
    pars_data = db['each_hour']
    pars_data.insert_one(dict_for_save)
    var_data = db['list_ids']
    var_add = var_data.find_one()
    var_add['ids'].insert(0, date_t.strftime("%Y-%m-%d_%H:%M"))
    var_data.delete_many({})
    var_data.insert_one(var_add)

def save_mongo_logs(errors):
    date_t = datetime.utcnow()
    dict_for_save = {}
    dict_for_save['_id'] = 'log_' + date_t.strftime("%Y-%m-%d_%H:%M")
    dict_for_save['Errors'] = errors
    db = client.test
    log_data = db['logs']
    log_data.insert_one(dict_for_save)

def restore(data):
    data_f = {}
    for unit in data:
        data_f.update(unit)
    return data_f


if __name__ == '__main__':
    data = run_parser()
    t0 = time()
    res_data = corusel(data)
    save_mongo(restore(res_data))
    save_mongo_logs(ERR_4_5)
    print('Errors: ', len(ERR_4_5.keys()))
    print((time() - t0))
    print('From -- ', len(data), ' -- get -- ', len(res_data))
