from pycoingecko import CoinGeckoAPI
from get_links_with_API import get_dict_coins_id as get_ids
import asyncio
import aiohttp
import sys
from pymongo import MongoClient
import requests
from datetime import datetime
from fake_useragent import UserAgent
from time import time, sleep
import json
import random



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


async def get_html_io(client, id, proxies_list, date):
    prox = random.choice(proxies_list)
    proxy = f'http://tactjknm-dest:74alj06v8083 @{prox}'
    headers = { 'User-Agent': UserAgent().random }
    url = f'https://api.coingecko.com/api/v3/coins/{id}/history?date={date}&localization=en'
    async with client.get(url, proxy=proxy, headers=headers) as response:
        if response.status != 200:
            errors[id] = f"{response.status}"
            return 0
        return await response.json()

async def get_data_io(client, id, proxies_list, date):
    data = await get_html_io(client, id, proxies_list, date)
    try:
        return round(float(data['market_data']['current_price']['usd']), 2)
    except:
        return 0



async def gen_main(id, proxies_list, date):
    try:
        #loop = asyncio.get_running_loop()
        timeout = aiohttp.ClientTimeout(total=11)
        async with aiohttp.ClientSession(loop=loop, trust_env=True, timeout=timeout) as client:
            data = await get_data_io(client, id, proxies_list, date)
            all_coins_price[id] = data
    except:
        errors[id] = 'Exception error'


def write_json(data, file_name):
    with open(f'{file_name}.json', 'w') as f:
         json.dump(data, f, indent=4)

def compair_flist(flist, llist):
    leave_list = {}
    for i in flist:
        if i not in llist:
            leave_list[i] = 'empty'
    return leave_list




#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    t0 = time()
    cg = CoinGeckoAPI()
    ids_list = get_ids()
    date = '31-12-2020'
    first_list = ids_list
    print(len(ids_list))
    all_coins_price = {}
    errors = {}
    PROXIES_LIST = get_proxies_list('Webshare')
    a = int(round(len(ids_list) / 40, 0))
    j = 40
    for i in range(a):
        loop = asyncio.get_event_loop()
        if j > len(ids_list):
            future = [asyncio.ensure_future(gen_main(id, PROXIES_LIST, date)) for id in ids_list[j-40:]]
        future = [asyncio.ensure_future(gen_main(id, PROXIES_LIST, date)) for id in ids_list[j-40:j]]
        loop.run_until_complete(asyncio.wait(future))
        t = random.uniform(0.33, 1.09)
        sleep(t)
        j += 40
        print(j, 'last sleep - ', t, ' - time', (time() - t0))

    # Start work with errors rerequests
    stop = 5
    while len(errors) > 0 and stop != 0:
        ids_list = list(errors.keys())
        errors = {}
        a = int(round(len(ids_list) / 40, 0))
        j = 40
        for i in range(a):
            loop = asyncio.get_event_loop()
            if j > len(ids_list):
                future = [asyncio.ensure_future(gen_main(id, PROXIES_LIST, date)) for id in ids_list[j-40:]]
            future = [asyncio.ensure_future(gen_main(id, PROXIES_LIST, date)) for id in ids_list[j-40:j]]
            loop.run_until_complete(asyncio.wait(future))
            t = random.uniform(0.33, 1.09)
            sleep(t)
            j += 40
            print(j, 'last sleep - ', t, ' - time', (time() - t0))
        stop -= 1

        if len(first_list) > len(list(all_coins_price.keys())):
            print(len(first_list), '  >  ', len(list(all_coins_price.keys())))
            leave_list = compair_flist(first_list, list(all_coins_price.keys()))
            errors = leave_list




    print(len(leave_list))

    write_json(leave_list, 'leave_list')
    write_json(all_coins_price, 'all_coins_price')
    write_json(errors, 'errors')


    print(len(all_coins_price))
    print(len(errors))
    print((time() - t0))
