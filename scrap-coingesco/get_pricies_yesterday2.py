from get_links_with_API import get_dict_coins_id as get_ids
import asyncio
import aiohttp
import sys
import os
from pymongo import MongoClient
import requests
import time
from datetime import datetime, date, timedelta
from time import time, sleep
import json
import random
import sys


sys.path.append( os.path.dirname(os.path.dirname(os.path.abspath(__file__))) )
import base

# using
print(base.BASE_DIR)


client = MongoClient(base.CLIENT)

def get_proxies_list(file_name):
    try:
        with open(os.path.join(base.BASE_DIR, file_name), 'r') as f:
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


async def get_html_io(client, id, proxy, rdate):
    proxy = f'http://tactjknm:74alj06v8083 @{proxy}'
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

def error_decorator(function):
    # Внутри себя декоратор определяет функцию-"обёртку". Она будет обёрнута вокруг декорируемой,
    # получая возможность исполнять произвольный код до и после неё.
    def the_wrapper(ids_list, PROXIES_LIST, rdate, errors, first_list, all_coins_price):
        function(ids_list, PROXIES_LIST, rdate, errors, first_list, all_coins_price)
        ''''
        stop = 20
        while len(errors) > 0 and stop != 0:
            print(len(first_list), '  >  ', len(list(all_coins_price.keys())))
            ids_list = list(errors.keys())
            errors = {}

            function(ids_list, PROXIES_LIST, rdate)

        stop -= 1

        if len(first_list) > len(list(all_coins_price.keys())):
            #print(len(first_list), '  >  ', len(list(all_coins_price.keys())))
            errors = compair_flist(first_list, list(all_coins_price.keys()))
            sleep(4)
        '''
    return the_wrapper


@error_decorator
def handler(ids_list, PROXIES_LIST, rdate, errors, first_list, all_coins_price):
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


def save_to_json(data):
    with open(os.path.join(base.BASE_DIR, 'scrap-coingesco/data.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_date_yesterday():

    rdate = (date.today() - timedelta(days=1)).strftime('%d-%m-%Y')
    return rdate


#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    #data for hendler

    all_coins_price = {}
    errors = {}
    rdate = get_date_yesterday()
    #re_date = ['19-06-2021', '20-06-2021','21-06-2021','22-06-2021','23-06-2021']
    PROXIES_LIST = get_proxies_list('Webshare')
    #for rdate in re_date:
    ids_list = get_ids()
    first_list = ids_list
    print(rdate, len(ids_list))

    handler(ids_list, PROXIES_LIST, rdate, errors, first_list, all_coins_price) # first loop

    '''
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
    '''
    try:
        save_mongo(all_coins_price, rdate) # TODO MongoB
        print('saved mongo')
    except:
        save_to_json(all_coins_price)
        print('saved json')

    if len(errors) > 0:
        write_json(errors, f'errors_{rdate}')
    print(len(all_coins_price))
    print(len(errors))

    #print((time() - t0) / 60)
    '''
    with open(os.path.join(base.BASE_DIR, 'scrap-coingesco/data.json'), 'r') as f:
        data = json.load(f)
    save_mongo(data, rdate)
    print(rdate)
    '''
