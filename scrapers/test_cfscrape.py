import cloudscraper
import requests
#import urllib2
from requests.auth import HTTPProxyAuth
import random
from pymongo import MongoClient
from time import time, sleep
from datetime import datetime
import multiprocessing
from get_coins_detail_save_mongo import get_coins

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")
GEN_DICT = {}


def get_proxies_list(file_name):
    try:
        with open(file_name, 'r') as f:
            res = f.readlines()
        i = 0
        proxies_list = []
        while i<len(res):
            proxies_list.append(res[i].split(':vvyyimhm')[0])
            i+=1
        #print('List proxies load')
        return proxies_list
    except:
        print('List proxies did not load')


def get_dict_coins_id():

    headers = {
        'accept': 'application/json',
    }
    coins_id = requests.get('https://api.coingecko.com/api/v3/coins/list', headers=headers)
    coins_id = coins_id.json()
    coins_id_lists = []
    for coin in coins_id:
        if coin.get('id') == '':
            print(coin)
            continue
        elif '.' in coin.get('id'):
            print(coin)
            continue
        coins_id_lists.append(coin.get('id'))
    return coins_id_lists

def get_links_for_parse():
    coins_lists = get_dict_coins_id()
    links_list = []
    for coin in coins_lists:
        links_list.append('https://www.coingecko.com/en/coins/' + coin)
    print(len(links_list))
    return links_list

def get_page(url):
    proxies_list = get_proxies_list('Webshare')
    proxy = random.choice(proxies_list)
    proxies = {
        'http': f'socks5://vvyyimhm:vu4t6rhgy97x @{proxy}/',
        'https': f'socks5://vvyyimhm:vu4t6rhgy97x @{proxy}/'
    }
    try:
        scraper = cloudscraper.create_scraper()
        data = scraper.get(url, proxies=proxies).text
        return data
    except Exception as e:
        print(e)
        print(url)
        return url

def graber(data, coin_name):
    """ Function scrap likes data from each coins page and return"""
    coin = {}
    plt = 'Error'
    try:
        plt = data.split('star-color fa-star"></i>')[1].split('people')[0]
        #plt = plt.split('people')[0].split('<span class="ml-1">')[1] # add new
        plt = ''.join(plt.split(','))
        plt = int(plt)
        #print(plt)
    except:
        print('Error ', ' SCRAP in function graber')
    coin[coin_name] = plt
    return coin

def save_mongo(coin):
    """ Save result data dict for all coins in mongoDB """
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

def heandler(link):
    coin_name = link.split('/')[-1]
    try:
        data = get_page(link)
        coin_likes = graber(data, coin_name)
        print(coin_likes)
        return coin_likes
    except Exception as e:
        print(e)
        return {coin_name: None}


def corusel(links):
    print(multiprocessing.cpu_count(), ' in corusel ----- !')
    with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
        result_data = process.map(heandler, links)
    return result_data

def make_dict(gen_list):
    gen_dict = {}
    for coin in gen_list:
        gen_dict.update(coin)
    return gen_dict




if __name__ == '__main__':
    t0 = time()
    #proxies_list = get_proxies_list('Webshare')
    links = get_links_for_parse()
    gen_list = corusel(links)
    gen_dict = make_dict(gen_list)
    print((time() - t0)/60)
    save_mongo(gen_dict)
    markets = get_coins()
