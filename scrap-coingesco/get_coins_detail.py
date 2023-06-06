from get_links_with_API import get_dict_coins_id as get_ids
import asyncio
import aiohttp
import sys
import os
from pymongo import MongoClient
import requests
import time
from datetime import datetime, date, timedelta
#from fake_useragent import UserAgent
from time import time, sleep
import json
import random


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
ALL_COINS_DATA = []
client = MongoClient("mongodb+srv://doadmin:O627m5J9EjxXQ081@db-mongodb-fra1-43282-c88d22b1.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")


def get_proxies_list(file_name):
    try:
        with open(os.path.join(BASE_DIR, file_name), 'r') as f:
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

def get_all_urls(var):
    page = 1
    urls_api = []
    while page <= var:
        urls_api.append(f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}&sparkline=false&locale=en')
        page = page + 1
    return urls_api


async def get_request(client, url, proxy):
        data_detail = {}
        #proxy = f'http://tactjknm:74alj06v8083 @{proxy}'
        proxy = f'http://vvyyimhm:vu4t6rhgy97x @{proxy}'
        #headers = { 'User-Agent': UserAgent().random }
        headers = {
            'accept': 'application/json',
        }
        async with client.get(url, proxy=proxy, headers=headers) as response:
            data = await response.json()
            return data


def select_data(data):
    all_data = []

    for coin in data:
        data_detail = {}
        data_detail['id'] = coin.get('id')
        data_detail['current_price'] = coin.get('current_price')
        data_detail['price_change_percentage_24h'] = coin.get('price_change_percentage_24h')
        data_detail['market_cap'] = coin.get('market_cap')
        data_detail['total_volume'] = coin.get('total_volume')
        data_detail['fully_diluted_valuation'] = coin.get('fully_diluted_valuation')
        data_detail['max_supply'] = coin.get('max_supply')
        all_data.append(data_detail)
    return all_data


async def get_data_io(url, proxy):
    print(url, proxy)
    try:
        loop = asyncio.get_running_loop()
        timeout = aiohttp.ClientTimeout(total=10.2)
        async with aiohttp.ClientSession(loop=loop, trust_env=True, timeout=timeout) as client:
            data = await get_request(client, url, proxy)
            print(data)
            ALL_COINS_DATA.extend(data)
            #all_coins_detail.extend(data)
    except Exception as e:
        print(e)
        print('Exception error')

async def gen_main(urls, proxies_list):
    try:
        #data = await asyncio.gather(*[get_data_io(url, proxy) for url, proxy in zip(urls, proxies_list)])
        data = await asyncio.gather(*[get_data_io(url, random.choice(proxies_list)) for url in urls])

    except:
        print('__________')
        raise

def handler(urls, PROXIES_LIST):
    asyncio.run(gen_main(urls, PROXIES_LIST))


def save_mongo(data, name):
    db = client.markets
    markets_db = db[name]
    markets_db.delete_many({})
    markets_db.insert_many(data)


def save_to_json(data):
    with open(os.path.join(BASE_DIR, 'scrap-coingesco/data_detail.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    pages = len(get_ids()) // 250 + 1
    print(pages)
    all_coins_detail = []
    proxies_list = get_proxies_list('scrap-coingesco/Webshare')
    urls = get_all_urls(pages)
    print(urls)
    handler(urls, proxies_list)
    data = select_data(ALL_COINS_DATA)
    print(len(data))
    save_to_json(data)
    save_mongo(data, 'coins_detail')
