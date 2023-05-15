from get_links_with_API import get_dict_coins_id as get_ids
from get_coins_detail_save_mongo import get_coins
#from compare_alert import main_notification
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
import json


import random

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

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

def save_mongo_logs(errors):
    """ Save result errors dict in mongoDB """
    date_t = datetime.utcnow()
    dict_for_save = {}
    dict_for_save['_id'] = 'log_' + date_t.strftime("%Y-%m-%d_%H:%M")
    dict_for_save['Errors'] = errors
    db = client.test
    log_data = db['logs']
    log_data.insert_one(dict_for_save)


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

def graber(data, coin_name):
    """ Function scrap likes data from each coins page and return"""
    coin = {}
    plt = 'Error'
    try:
        plt = data.split('fa-star"></i>')[1].split('people')[0]
        #plt = plt.split('people')[0].split('<span class="ml-1">')[1] # add new
        plt = ''.join(plt.split(','))
        plt = int(plt)
    except:
        print('Error ', ' SCRAP in function graber')
    coin[coin_name] = plt
    return coin

async def get_html_io(client, coin_id, proxy):
    """ Connect to Coingecko for get response from coin """
    proxy = f'http://vvyyimhm:vu4t6rhgy97x @{proxy}'
    headers = { "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0" }
    headers_1 = {"name":"Accept","value":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"},{"name":"Accept-Encoding","value":"gzip, deflate, br"},{"name":"Accept-Language","value":"en-US,en;q=0.5"},{"name":"Cache-Control","value":"max-age=0"},{"name":"Connection","value":"keep-alive"},{"name":"Cookie","value":"_ga_LJR3232ZPB=GS1.1.1640358777.16.1.1640358777.0; _ga=GA1.2.359378639.1613921993; __gads=ID=64e4ddb9c2b8c5e6-220e9e8ad9ce001f:T=1614413752:S=ALNI_Mbx8jpOiNR5m7rISRT7AYpjumT93g; __atuvc=1%7C30; _gaexp=GAX1.2.SPxjkMasRayCjV6SpTBIMw.19031.2!iK3ermLkRXOQrPmLmmxe1w.19071.0!ziJPa17vSn-OMacw479Hzw.19020.0; _session_id=b0ad56f521267847b808a7e0a7b7a354; _gid=GA1.2.995925519.1640291589; cf_clearance=GHhHjm0kq3VdZOyARV9Tc18Y7In5sIcIUflK17Jq45M-1640293881-0-150; __cf_bm=R5uwPSSD5G61O0vNfeoW2fz05I8YivHNujLpLTARt.w-1640358778-0-AVquc1qvy8XKF/HIgeaOHnltLPEXwZ1xxIuWUHv+NvWYB39uC07I1GD9XEm/3wvqGmK3Oz4AnIcN2Tpo/VJ6PjAzBJv/mXMz6mAik4Gf1R/jbGHnAw2HGzmGoS3CvNJ0zN2DjYEq8btL9eZX1lyJUhWQ5P/g1kU+Nak0ll73dkFR"},{"name":"Host","value":"www.coingecko.com"},{"name":"Referer","value":"https://www.coingecko.com/en"},{"name":"Upgrade-Insecure-Requests","value":"1"},{"name":"User-Agent","value":"Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"}
    url = 'https://www.coingecko.com/en/coins/' + coin_id
    try:
        async with client.get(url, proxy=proxy, headers=headers) as response:
            if response.status == 503:
                cookies = response.cookies
                print("First", response.status)
                await asyncio.sleep(38)
                print("Second", response.status)
                async with client.get(url, proxy=proxy, headers=headers) as resp:
                    print("STATUS RESP", resp.status)
                    data = await response.text()


                #print("status after"response.status)

            if response.status != 200:
                if response.status == 404:
                    GEN_ERROR[coin_id] = f"{response.status}"
                    GEN_DICT[coin_id] = 0
                    return
                errors[coin_id] = f"{response.status}"
                return
            #data = await response.text()
            coin = graber(data, coin_id)
            GEN_DICT[coin_id] = coin[coin_id]
            return
    except Exception as e:
        print(e)
        print('Except get_html_io', coin_id)


async def get_data_io(coin_id, proxy):
    """Create aiohttp ClientSession for each request"""
    try:
        loop = asyncio.get_running_loop()
        #timeout = aiohttp.ClientTimeout(total=45)
        async with aiohttp.ClientSession(loop=loop, trust_env=True) as client:
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

def handler(coins, PROXIES_LIST):
    """ Run ayncio corutines. 100 coro for each loop """
    a = int(round(len(coins) / 100, 0))
    if a == 0:
        a = 1
    j = 100
    for i in range(a):
        t_now = time()
        if j > len(coins):
            if j == 100:
                asyncio.run(gen_main(coins, PROXIES_LIST))
            else:
                asyncio.run(gen_main(coins[j-100:], PROXIES_LIST))
        else:
            asyncio.run(gen_main(coins[j-100:j], PROXIES_LIST))

        dtime = time() - t_now
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

#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    errors = {}
    PROXIES_LIST = get_proxies_list('Webshare')
    coins = get_ids()
    GEN_ERROR = {}
    GEN_DICT = {}

    t0 = time()
    first_list = coins
    handler(coins, PROXIES_LIST) # Run general scrap loop
    stop = 10
    while len(errors) > 0 and stop != 0: # Run second loop for errors
        print(len(first_list), '  >  ', len(list(GEN_DICT.keys())))
        coins = list(errors.keys())
        errors = {}
        handler(coins, PROXIES_LIST)
        stop -= 1
        if len(first_list) > len(list(GEN_DICT.keys())):
            errors = compair_flist(first_list, list(GEN_DICT.keys()))
            sleep(4)

    GEN_ERROR['other_errrors'] = errors
    print('Load - ', len(first_list), 'get data -', len(GEN_DICT), 'errors - ', len(GEN_ERROR))

    save_mongo(GEN_DICT)
    if len(GEN_ERROR.keys()) > 0:
        save_mongo_logs(GEN_ERROR)
    markets = get_coins()
    #main_notification()
    print('Alerts send')
    print((time() - t0))
