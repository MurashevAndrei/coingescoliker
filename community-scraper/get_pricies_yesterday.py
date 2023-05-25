from get_links_with_API import get_dict_coins_id as get_ids
import asyncio
import aiohttp
import sys
from pymongo import MongoClient
import requests
import time
from datetime import datetime, date, timedelta
from fake_useragent import UserAgent
from time import time, sleep
import json
import random

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")


def get_proxies_list(file_name):
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


async def get_html_io(client, id, proxy, rdate):
    proxy = f'http://vvyyimhm:vu4t6rhgy97x @{proxy}'
    headers = { 'User-Agent': UserAgent().random }
    url = f'https://api.coingecko.com/api/v3/coins/{id}/history?date={rdate}&localization=en'
    async with client.get(url, proxy=proxy, headers=headers) as response:
        if response.status != 200:
            errors[id] = f"{response.status}"
            return 0
        data = await response.json()
        try:
            return round(float(data['market_data']['current_price']['usd']), 2)
        except:
            return 0

async def get_data_io(id, proxy, rdate):
    try:
        loop = asyncio.get_running_loop()
        timeout = aiohttp.ClientTimeout(total=10.2)
        async with aiohttp.ClientSession(loop=loop, trust_env=True, timeout=timeout) as client:
            data = await get_html_io(client, id, proxy, rdate)
            all_coins_price[id] = data
    except:
        errors[id] = 'Exception error'



async def gen_main(ids, proxies_list, rdate):
    try:
        data = await asyncio.gather(*[get_data_io(id, p, rdate) for id, p in zip(ids, proxies_list)])
    except:
        raise

def handler(ids_list, PROXIES_LIST, rdate):
    a = int(round(len(ids_list) / 100, 0))
    if a == 0:
        a = 1
    j = 100
    for i in range(a):
        t_now = time()
        if j > len(ids_list):
            if j == 100:
                asyncio.run(gen_main(ids_list, PROXIES_LIST, rdate))
            else:
                asyncio.run(gen_main(ids_list[j-100:], PROXIES_LIST, rdate))
        else:
            asyncio.run(gen_main(ids_list[j-100:j], PROXIES_LIST, rdate))

        dtime = time() - t_now
        #t = random.uniform(0.6, 1)
        #sleep(t)
        #print(j, 'time', (time() - t0) / 60, f' delta time {dtime}')
        j += 100
    return


def write_json(data, file_name):
    with open(f'{file_name}.json', 'w') as f:
         json.dump(data, f, indent=4)

def compair_flist(flist, llist):
    leave_list = {}
    for i in flist:
        if i not in llist:
            leave_list[i] = 'empty'
    return leave_list

def save_mongo(price, rdate):
    dict_for_save = {}
    dict_for_save['_id'] = f"price_{rdate}"
    dict_for_save['data'] = price
    db = client.test
    pars_data = db['pricies']
    pars_data.insert_one(dict_for_save)


#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    t0 = time()

    rdate = (date.today() - timedelta(days=1)).strftime('%d-%m-%Y')
    PROXIES_LIST = get_proxies_list('Webshare')

    ids_list = get_ids()
    first_list = ids_list
    print(rdate, len(ids_list))
    all_coins_price = {}
    errors = {}
    handler(ids_list, PROXIES_LIST, rdate) # first loop
    # Start work with errors rerequests
    stop = 20
    while len(errors) > 0 and stop != 0:
        print(len(first_list), '  >  ', len(list(all_coins_price.keys())))
        ids_list = list(errors.keys())
        errors = {}
        handler(ids_list, PROXIES_LIST, rdate)
        stop -= 1

        if len(first_list) > len(list(all_coins_price.keys())):
            #print(len(first_list), '  >  ', len(list(all_coins_price.keys())))
            errors = compair_flist(first_list, list(all_coins_price.keys()))
            sleep(4)
    save_mongo(all_coins_price, rdate) # TODO MongoDB
    if len(errors) > 0:
        write_json(errors, f'errors_{rdate}')
    print(len(all_coins_price))
    print(len(errors))

    print((time() - t0) / 60)
