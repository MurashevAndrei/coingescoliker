import requests
import asyncio
import aiohttp
import json
from pymongo import MongoClient
from datetime import datetime
import os
from time import time, sleep

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)

#client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")
client = MongoClient("mongodb+srv://doadmin:O627m5J9EjxXQ081@db-mongodb-fra1-43282-c88d22b1.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
#GEN_DICT = {}

def get_dict_coins_id():

    headers = {
        'accept': 'application/json',
    }
    coins_id = requests.get('https://api.coingecko.com/api/v3/coins/list', headers=headers)
    coins_id = coins_id.json()
    coins_id_lists = []
    for coin in coins_id:
        if coin.get('id') == '':
            #print(coin)
            continue
        elif '.' in coin.get('id'):
            #print(coin)
            continue
        coins_id_lists.append(coin.get('id'))
    return coins_id_lists


def get_proxies_list(file_name):
    try:
        with open(os.path.join(BASE_DIR, file_name), 'r') as f:
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


def get_watchlists(id):
    headers = {
        'accept': 'application/json',
    }
    link = 'https://api.coingecko.com/api/v3/coins/' + id
    coin_data = requests.get(link, headers=headers).json()
    #print(link)

    #print(coin_data['watchlist_portfolio_users'])
    return coin_data

async def get_html_io(client, id, proxy):
    proxy = f'http://tactjknm:74alj06v8083 @{proxy}'
    headers = {
        'accept': 'application/json',
    }
    url = 'https://api.coingecko.com/api/v3/coins/' + id
    async with client.get(url, proxy=proxy, headers=headers) as response:
        if response.status != 200:
            if response.status == 404:
                GEN_ERROR[id] = f"{response.status}"
                GEN_DICT[id] = 0


            errors[id] = f"{response.status}"
            return 0
        data = await response.json()
        coin = data['watchlist_portfolio_users']
        GEN_DICT[id] = coin[id]
        try:
            return coin
        except:
            return 0

async def get_data_io(id, proxy):
    try:
        loop = asyncio.get_running_loop()
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(loop=loop, trust_env=True, timeout=timeout) as client:
            data = await get_html_io(client, id, proxy)
            all_coins_price[id] = data
            #print(id, data)

    except:
        errors[id] = 'Exception error'
        print(proxy)
        print(id)



async def get_main(ids, proxies_list):
    try:
        data = await asyncio.gather(*[get_data_io(id, p) for id, p in zip(ids, proxies_list)])

    except:
        raise

def handler(ids_list, PROXIES_LIST):
    a = int(round(len(ids_list) / 100, 0))
    if a == 0:
        a = 1
    j = 100
    for i in range(a):

        if j > len(ids_list):
            if j == 100:
                asyncio.run(get_main(ids_list, PROXIES_LIST))
            else:
                asyncio.run(get_main(ids_list[j-100:], PROXIES_LIST))
        else:
            asyncio.run(get_main(ids_list[j-100:j], PROXIES_LIST))


        #t = random.uniform(0.6, 1)
        #sleep(t)
        #print(j, 'time', (time() - t0) / 60, f' delta time {dtime}')
        j += 100
    return

def save_to_json(data):
    with open(os.path.join(BASE_DIR, 'scrapers/data.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


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


def compair_flist(flist, llist):
    """ Compair list ids and result list --> create list for next itteration"""
    leave_list = {}
    for i in flist:
        if i not in llist:
            leave_list[i] = 'empty'
    return leave_list


def run():
    PROXIES_LIST = get_proxies_list('Webshare')
    #for rdate in re_date:
    ids_list = get_dict_coins_id()


    all_coins_price = {}
    errors = {}
    print("Start handler")
    handler(ids_list, PROXIES_LIST) # first loop
    # Start work with errors rerequests
    #stop = 20
    #while len(errors) > 0 and stop != 0:

    #    handler(ids_list, PROXIES_LIST)
    #    stop -= 1
    save_to_json(all_coins_price)
    print(errors)



if __name__ == '__main__':
    '''
    list_ids = get_dict_coins_id()
    watchlists = []
    for id in list_ids[:2]:
        coin_data = get_watchlists(id)
        watchlists.append({id: coin_data})
    '''

    PROXIES_LIST = get_proxies_list('scrapers/Webshare')
    #for rdate in re_date:
    ids_list = get_dict_coins_id()
    ids_list = ids_list[:100]
    GEN_ERROR = {}
    GEN_DICT = {}

    first_list = ids_list


    all_coins_price = {}
    errors = {}
    print("Start handler")
    handler(ids_list, PROXIES_LIST) # first loop
    # Start work with errors rerequests
    '''
    stop=2
    while len(errors) > 0 and stop != 0: # Run second loop for errors
        print(len(first_list), '  >  ', len(list(GEN_DICT.keys())))
        coins = list(errors.keys())
        errors = {}
        handler(coins, PROXIES_LIST)
        stop -= 1
        if len(first_list) > len(list(GEN_DICT.keys())):
            errors = compair_flist(first_list, list(GEN_DICT.keys()))
            #sleep(4)
            '''
    GEN_ERROR['other_errrors'] = errors
    print('Load - ', len(first_list), 'get data -', len(GEN_DICT), 'errors - ', len(GEN_ERROR))


    save_to_json(all_coins_price)
    #save_to_json(GEN_DICT)
    print(len(errors))

    #run()
    with open(os.path.join(BASE_DIR, 'scrapers/data.json'), 'r') as f:
        data = json.load(f)
    save_mongo(data)
    #print(data)
    print('saved')
