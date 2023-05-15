from get_links_with_API import get_dict_coins_id as get_ids
import asyncio
import aiohttp
import sys
from pymongo import MongoClient
import requests
import time
from datetime import datetime, date, timedelta
#from fake_useragent import UserAgent
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
    #headers = { 'User-Agent': UserAgent().random }
    headers = {

        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',

    }
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
    len_proxies = len(PROXIES_LIST)
    a = int(round(len(ids_list) / len_proxies, 0))
    if a == 0:
        a = 1
    j = len_proxies
    for i in range(a):
        t_now = time()
        if j > len(ids_list):
            if j == len_proxies:
                asyncio.run(gen_main(ids_list, PROXIES_LIST, rdate))
            else:
                asyncio.run(gen_main(ids_list[j-len_proxies:], PROXIES_LIST, rdate))
        else:
            asyncio.run(gen_main(ids_list[j-len_proxies:j], PROXIES_LIST, rdate))

        dtime = time() - t_now
        #t = random.uniform(0.6, 1)
        #sleep(t)
        print(j, 'time', (time() - t0) / 60, f' delta time {dtime}')
        j += len_proxies
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

def list_date_from(date_from):
    list_dates = []
    date_t = datetime.utcnow()
    date_t = date_t.strftime("%d-%m-%Y")
    while date_from != date_t:
        list_dates.append(date_from)
        date_from = datetime.strptime(date_from, "%d-%m-%Y") + timedelta(days=1)
        date_from = date_from.strftime("%d-%m-%Y")
    return list_dates



#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    t0 = time()

    #rdate = (date.today() - timedelta(days=1)).strftime('%d-%m-%Y')

    #re_date = ['11-01-2022', '12-01-2022','13-01-2022','14-01-2022','15-01-2022', '16-01-2022', '17-01-2022', '18-01-2022', '19-01-2022', "20-01-2022", "21-01-2022", "22-01-2022", "23-01-2022"]
    re_date = list_date_from('24-03-2022')
    PROXIES_LIST = get_proxies_list('Webshare')
    for rdate in re_date:
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
