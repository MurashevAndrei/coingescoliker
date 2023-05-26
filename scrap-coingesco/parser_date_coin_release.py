from get_links_with_API import get_dict_coins_id as get_ids
import asyncio
import aiohttp
import sys
from pymongo import MongoClient
import requests
from datetime import datetime
from time import sleep
from fake_useragent import UserAgent
import multiprocessing
from time import time, sleep
import time as time_
import json


import random

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

def save_date_mongo(data, name):
    data = {"date": data}
    db = client.markets
    markets_db = db[name]
    try:
        markets_db.delete_many({})
    except:
        print('No date data')
    markets_db.insert_one(data)

def load_date_mongo():
    db = client.markets.date_release
    return db.find_one()['date']


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

def get_date_release(data, coin_id):
    """ Function scrap likes data from each coins page and return"""
    coin = {}
    data = data["prices"]
    date_release = int(str(data[0][0])[:10])
    if date_release == 0:
        return False
    date_release = time_.strftime("%Y-%m-%d", time_.localtime(date_release))
    coin[coin_id] = date_release
    return coin

async def get_html_io(client, coin_id, proxy):
    """ Connect to Coingecko for get response from coin """
    proxy = f'http://vvyyimhm:vu4t6rhgy97x @{proxy}'
    headers = { 'User-Agent': UserAgent().random }
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=max'
    try:
        async with client.get(url, proxy=proxy, headers=headers) as response:
            if response.status != 200:
                if response.status == 404:
                    GEN_ERROR[coin_id] = f"{response.status}"
                    GEN_DICT[coin_id] = 0
                    return
                errors[coin_id] = f"{response.status}"
                return
            data = await response.json()
            coin = get_date_release(data, coin_id)
            if coin == False:
                GEN_DICT[coin_id] = '-'
                return
            GEN_DICT[coin_id] = coin[coin_id]
            return
    except:
        print('Except get_html_io')


async def get_data_io(coin_id, proxy):
    """Create aiohttp ClientSession for each request"""
    try:
        loop = asyncio.get_running_loop()
        timeout = aiohttp.ClientTimeout(total=10.2)
        async with aiohttp.ClientSession(loop=loop, trust_env=True, timeout=timeout) as client:
            data = await get_html_io(client, coin_id, proxy)
    except:
        print('Exception error get_data_io')

async def gen_main(coins, proxies_list):
    """Create tasks for aiohttp corutine"""
    try:
        data = await asyncio.gather(*[get_data_io(coin_id, p) for coin_id, p in zip(coins, proxies_list)])
        #print('Ok')
    except:
        print('Exception error get_main function asyncio')

def handler(coins, proxies_list):
    """ Run ayncio corutines. 100 coro for each loop """
    a = int(round(len(coins) / 100, 0))
    if a == 0:
        a = 1
    j = 100
    for i in range(a):
        t_now = time()
        if j > len(coins):
            if j == 100:
                asyncio.run(gen_main(coins, proxies_list))
            else:
                asyncio.run(gen_main(coins[j-100:], proxies_list))
        else:
            asyncio.run(gen_main(coins[j-100:j], proxies_list))

        dtime = time() - t_now
        print('Ok', j)
        #print(j, 'time', (time() - t0) / 60, f' delta time {dtime}')
        j += 100
    return

def compair_flist(flist, llist):
    """ Compair list ids and result list --> create list for next itteration"""
    leave_list = {}
    for i in flist:
        if i not in llist:
            leave_list[i] = 'empty'
    return leave_list

def check_old_vs_new_coins(new_coins, old_coins):
    old_coins = list(old_coins.keys())
    new_coins = list(set(new_coins) - set(old_coins))
    return new_coins

def adding_new_daties(new_data, old_data):
    for coin in new_data:
        old_data[coin] = new_data[coin]
    return old_data

#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    errors = {}
    proxies_list= get_proxies_list('Webshare')
    coins = get_ids()
    GEN_ERROR = {}
    GEN_DICT = {}
    try:
        delleting = load_date_mongo()
        del_list = []
        for coin in delleting:
            try:
                if delleting[coin] == '1970-01-01' or delleting[coin] == '-':
                    del_list.append(coin)
            except:
                'No old data'
        for deleter in del_list:
            val = delleting.pop(deleter)
        save_date_mongo(delleting, 'date_release')
    except:
        'No old data'
    try:
        coins = check_old_vs_new_coins(coins, load_date_mongo())
    except:
        'No old data'

    t0 = time()
    first_list = coins
    handler(coins, proxies_list) # Run general scrap loop
    stop = 10
    while len(errors) > 0 and stop != 0: # Run second loop for errors
        print(len(first_list), '  >  ', len(list(GEN_DICT.keys())))
        coins = list(errors.keys())
        errors = {}
        handler(coins, proxies_list)
        stop -= 1
        if len(first_list) > len(list(GEN_DICT.keys())):
            errors = compair_flist(first_list, list(GEN_DICT.keys()))
            sleep(4)
    try:
        GEN_DICT = adding_new_daties(GEN_DICT, load_date_mongo())
    except:
        'No old data'
    #print(len(GEN_DICT), len(load_date_mongo()))
    print(GEN_DICT)
    save_date_mongo(GEN_DICT, 'date_release')
    GEN_ERROR['other_errrors'] = errors
    #print('Load - ', len(first_list), 'get data -', len(GEN_DICT), 'errors - ', len(GEN_ERROR))

    #TODO SAVE DICT DATE save_mongo(GEN_DICT)
