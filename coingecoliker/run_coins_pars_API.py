import os
import requests
import json
import sys
import asyncio
import aiohttp
from datetime import datetime
from aiohttp import web
from bs4 import BeautifulSoup
import get_links_with_API
from pymongo import MongoClient

COINS = {}
ERR_5 = []
ERR_4 = []
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

async def get_json(client, url):
    coin = {}
    plt = ''
    async with client.get(url) as response:
        stat = response.status
        if stat == 200:
            if url in ERR_5:
                ERR_5.remove(url)
        if stat != 200:
            if stat == 500 or stat == 503 or stat == 504:
                ERR_5.append(url)
            else:
                ERR_4.append((url, stat))
        data = await response.text()
        plt = 'Error'
        try:
            plt = data.split('<i data-target="favorites.emptyStar"')[1].split('</i>')[1].split('</span>')[0]
            plt = plt.split('people')[0]
            plt = ''.join(plt.split(','))
            plt = int(plt)
        except:
            print('Error ', url)
        coin_name = url.split('/')[-1]
        coin[coin_name] = plt
        COINS[coin_name] = plt

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

def check_err_empty(err4, err5):
    errors_dict = {}
    if len(err4) > 0:
        errors_dict['ERRORS'] = err4
    if len(err5) > 0:
        errors_dict['ERR5'] = err5
    if len(errors_dict.keys()) > 0:
        save_mongo_logs(errors_dict)

async def check_err():
    loop = asyncio.get_running_loop()
    async with aiohttp.ClientSession(loop=loop) as client:
        await asyncio.wait([get_json(client, url) for url in ERR_5])
    return web.Response(text='Done')

async def main(data):
    print(datetime.now().strftime("%A, %B %d, %I:%M %p"))
    print('---------------------------')
    loop = asyncio.get_running_loop()
    async with aiohttp.ClientSession(loop=loop) as client:
        links = data
        print('downlod to parse ', len(links))
        await asyncio.wait([get_json(client, url) for url in links])
    return web.Response(text='Done')

def run_parser():
        data = get_links_with_API.get_links_for_parse()
        b = asyncio.run(main(data))
        i = 1
        while len(ERR_5) > 0 and i < 10:
            c = asyncio.run(check_err())
            i = i+1
        coin = COINS
        print('Was done ', len(COINS.keys()), ' coins from ', len(data), ' in coingecko')
        save_mongo(coin)
        err4 = ERR_4
        err5 = ERR_5
        check_err_empty(err4, err5)


if __name__ == '__main__':
    run_parser()
