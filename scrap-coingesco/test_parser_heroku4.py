import get_links_with_API
from pymongo import MongoClient
import requests
from datetime import datetime
from time import sleep
from fake_useragent import UserAgent
import multiprocessing
from time import time, sleep
import json


import random

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

def run_parser():
    data = get_links_with_API.get_links_for_parse()
    return data

def graber(data, coin_name):
    coin = {}
    plt = 'Error'
    try:
        plt = data.split('<i data-target="favorites.solidStar"')[1].split('</i>')[1].split('</span>')[0]
        plt = plt.split('people')[0].split('<span class="ml-1">')[1] # add new
        plt = ''.join(plt.split(','))
        plt = int(plt)
    except:
        print('Error ', ' SCRAP')
    coin[coin_name] = plt
    return coin

def heandler(url):
    coin_name = url.split('/')[-1]
    data = {}
    prox = random.choice(PROXIES_LIST)
    proxies = {
        'http': '//tactjknm-US-rotate:74alj06v8083@{}'.format(prox),
        'https': '//tactjknm-US-rotate:74alj06v8083@{}'.format(prox)
    }
    headers = { 'User-Agent': UserAgent().random }
    #headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    try:
        p = requests.get(url, headers=headers, proxies=proxies, timeout=20)
        #print(p.text)
        if p.status_code == 404:
            data['Error'] = {'coin_name': coin_name, 'Error': f'Status_code {p.status_code}'}
            return data
        if p.status_code != 200:
            i = 0
            while i < 3 and p.status_code != 200:
                #time.sleep(6)
                print(coin_name, 'for proxie', prox, ' !!!CONNECT ERROR !!! ---- ITER', i, ' Status code = ', p.status_code)
                prox = random.choice(PROXIES_LIST)
                proxies = {
                    'http': '//tactjknm-US-rotate:74alj06v8083@{}'.format(prox),
                    'https': '//tactjknm-US-rotate:74alj06v8083@{}'.format(prox)
                }
                headers = { 'User-Agent': UserAgent().random }
                p = requests.get(url, headers=headers, proxies=proxies, timeout=15)
                i += 1
            if i == 3 and p.status_code != 200:
                print('!!!!--------------------------------------ERROR SAVE----------------------!!!!')
                data['Error'] = {'coin_name': coin_name, 'Error': f'Status_code {p.status_code}'}
                return data
        data = graber(p.text, coin_name)
        #print('Ok ', coin_name)
    except Exception as e:
        data['Error'] = {'coin_name': coin_name, 'Error': f'Except error {e.__class__}'}
        print(f'EXCEPT ERROR {coin_name}', e.__class__)
    return data

def corusel(links):
    print(multiprocessing.cpu_count(), ' in corusel ----- !')
    try:
        with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
            result_data = process.map(heandler, links)
    except Exception as e:
        print('multiprocessing exception ', e.__class__)
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
    data_errors = {}
    for unit in data:
        if 'Error' in unit.keys():
            try:
                print(unit)
                data_errors.update({unit['Error']['coin_name']: unit['Error']['Error']})
                data_f.update({unit['Error']['coin_name']: 0})
            except:
                print(f'Do not save in log {unit}')
        elif 'Error' in unit.values():
            data_errors.update(unit)
        else:
            data_f.update(unit)
    return data_f, data_errors

def get_proxies_list(file_name):
    try:
        with open(file_name, 'r') as f:
            res = f.readlines()
        i = 0
        proxies_list = []
        while i<len(res):
            proxies_list.append(res[i].split(':tactjknm')[0])
            i+=1
        print('List proxies load')
        return proxies_list
    except:
        print('List proxies did not load')
        return

if __name__ == '__main__':

    PROXIES_LIST = get_proxies_list('Webshare')
    data = run_parser()
    t0 = time()
    res_data = corusel(data)
    data_fin, data_errors = restore(res_data)
    save_mongo(data_fin)
    if len(data_errors.keys()) > 0:
        save_mongo_logs(data_errors)

    print((time() - t0))
    print('From -- ', len(data), ' -- get -- ', len(res_data))
