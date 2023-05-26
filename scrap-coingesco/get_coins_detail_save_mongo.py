import os
import requests
import asyncio
import aiohttp
from aiohttp import web
from datetime import datetime
import json
import locale
from pymongo import MongoClient
import random
from get_links_with_API import get_dict_coins_id as get_ids

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

API_DATA = []

def get_proxies_list(file_name):
    """ Get proxies from local file """
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
"""
def get_ids():
    headers = {
        'accept': 'application/json',
    }
    coins_id = requests.get('https://api.coingecko.com/api/v3/coins/list', headers=headers)
    coins_id = coins_id.json()
    coins_id_lists = []
    for coin in coins_id:
        coins_id_lists.append(coin.get('id'))
    return coins_id_lists
"""

def get_all_urls(var):
    i = 1
    urls_api = []
    while i <= var:
        urls_api.append('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={}&sparkline=false'.format(i))
        i = i + 1
    return urls_api

async def get_api_data(client, url, proxy):
    proxy = f'http://vvyyimhm:vu4t6rhgy97x @{proxy}'
    try:
        async with client.get(url, proxy=proxy) as response:
            r = await response.json()
            API_DATA.extend(r)
    except:
        print('Exception in get_api_data')

async def create_clients(url, proxy):
    """Create aiohttp ClientSession for each request"""
    try:
        loop = asyncio.get_running_loop()
        async with aiohttp.ClientSession(loop=loop) as client:
            await get_api_data(client, url, proxy)
    except:
        print('Exception in create_clients')

async def run_asy_parse(urls, proxies_list):
    """Create tasks for aiohttp corutine"""
    try:
        data = await asyncio.gather(*[create_clients(url, proxy) for url, proxy in zip(urls, proxies_list)])
        #print('Ok')
    except:
        print('Exception error get_main function asyncio')

def select_data():
    data_list = []
    for coin in API_DATA:
        var_dict = {}
        var_dict['coin_id'] = coin['id']
        var_dict['coin_price'] = coin['current_price']
        if coin['price_change_percentage_24h'] != None:
            var_dict['price_change_percentage_24h'] = round(float(coin['price_change_percentage_24h']), 2)
        else:
            var_dict['price_change_percentage_24h'] = '-'
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        if coin['market_cap'] != None:
            var_dict['market_cap'] = int(coin['market_cap'])
        else:
            var_dict['market_cap'] = '-'
        if coin['total_volume'] != None:
            var_dict['24_hour_trading_volume'] = round(float(coin['total_volume']), 2)
        else:
            var_dict['24_hour_trading_volume'] = '-'
        if coin['fully_diluted_valuation']:
            var_dict['fully_diluted_valuation'] = '$' + locale.format('%d', int(coin['fully_diluted_valuation']), grouping=True)
        else:
            var_dict['fully_diluted_valuation'] = '-'
        var_dict['max_supply'] = coin['max_supply']
        data_list.append(var_dict)
    return data_list

def save_mongo(data, name):
    db = client.markets
    markets_db = db[name]
    markets_db.delete_many({})
    try:
        markets_db.insert_many(data)
    except Exception as e:
        print(data)
        print(e)

def get_coins():
    proxies_list = get_proxies_list('Webshare')
    pages_vol = len(get_ids()) // 250 + 1
    data = asyncio.run(run_asy_parse(get_all_urls(pages_vol), proxies_list))
    for unit in API_DATA:
        for key, value in unit.items():
            if isinstance(value, int) and value > 9223372036854775807:
                unit[key] = float(value)
    save_mongo(API_DATA, 'coins_detail')
    print('coins_detail saved in mongoDB')
    return API_DATA




#--------------------------------
#              MAIN
#-------------------------------

if __name__ == '__main__':
    get_coins()
