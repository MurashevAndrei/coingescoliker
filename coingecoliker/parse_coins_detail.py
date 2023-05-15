from get_links_with_API import get_dict_coins_id
import os
import requests
import asyncio
import aiohttp
from aiohttp import web
from datetime import datetime
import json
from pymongo import MongoClient

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

API_DATA = []

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

def select_data():
    data_list = []
    for coin in API_DATA:
        var_dict = {}
        var_dict['coin_id'] = coin['id']
        var_dict['coin_price'] = coin['current_price']
        var_dict['price_change_percentage_24h'] = coin['price_change_percentage_24h']
        var_dict['market_cap'] = coin['market_cap']
        var_dict['24_hour_trading_volume'] = coin['total_volume']
        var_dict['fully_diluted_valuation'] = coin['fully_diluted_valuation']
        var_dict['max_supply'] = coin['max_supply']
        data_list.append(var_dict)
    return data_list

def save_mongo(data, name):
    db = client.markets
    markets_db = db[name]
    markets_db.delete_many({})
    markets_db.insert_many(data)

def main():
    pages_vol = len(get_dict_coins_id()) // 250 + 1
    data = asyncio.run(run_asy_parse(get_all_urls(pages_vol)))
    data_list = select_data()
    save_mongo(data_list, 'coins_detail')
    print('details was done')




#--------------------------------
#              MAIN
#-------------------------------

if __name__ == '__main__':
    main()
