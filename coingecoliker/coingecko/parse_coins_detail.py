from .get_links_with_API import get_dict_coins_id
import os
import requests
import asyncio
import aiohttp
from aiohttp import web
from datetime import datetime
import json
import locale
from pymongo import MongoClient
from .settings import BASE_DIR, MONGO_DB

client = MongoClient(MONGO_DB)

API_DATA = []

def load_detail_MongoDB():
    db = client.markets.coins_detail
    data = db.find()
    list_data = []
    for i in data:
        list_data.append(i)
    return list_data

def get_all_urls(var):
    i = 1
    urls_api = []
    while i <= var:
        urls_api.append('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={}&sparkline=false'.format(i))
        i = i + 1
    return urls_api

async def get_api_data(client, url):
    async with client.get(url) as response:
        r = await response.json()
        API_DATA.extend(r)


async def run_asy_parse(urls):
    loop = asyncio.get_running_loop()
    async with aiohttp.ClientSession(loop=loop) as client:
        await asyncio.wait([get_api_data(client, url) for url in urls])
    return web.Response(text='Done')

def select_data(data_detail):
    data_list = []
    for coin in data_detail:
        var_dict = {}
        var_dict['coin_id'] = coin['id']
        var_dict['coin_price'] = coin['current_price']
        if coin['price_change_percentage_24h'] != None:
            var_dict['price_change_percentage_24h'] = round(float(coin['price_change_percentage_24h']), 2)
        else:
            var_dict['price_change_percentage_24h'] = '-'
        #locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')

        if coin['market_cap'] != None:
            var_dict['market_cap'] = '$' + locale.format('%d', int(coin['market_cap']), grouping=True)
        else:
            var_dict['market_cap'] = '-'
        if coin['total_volume'] != None:
            var_dict['24_hour_trading_volume'] = '$' + locale.format('%d', int(coin['total_volume']), grouping=True) #round(float(coin['total_volume']), 2)
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
    markets_db.insert_many(data)

def get_coins():
    #pages_vol = len(get_dict_coins_id()) // 250 + 1
    #data = asyncio.run(run_asy_parse(get_all_urls(pages_vol)))
    data = load_detail_MongoDB() # use data from mongoDB (updating everyhour by parser_aiohttp)
    data_list = select_data(data)
    return data_list




#--------------------------------
#              MAIN
#-------------------------------

if __name__ == '__main__':
    main()
    #get_coins()
