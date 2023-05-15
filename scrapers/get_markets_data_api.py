import os
import requests
import asyncio
import aiohttp
from datetime import datetime
from fake_useragent import UserAgent
import multiprocessing
from time import time, sleep
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient
import random


client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

LIST_PAIR = []
URLS_LIST = []
FINISH_LIST = []

def update_markets_mongo(new_data):
    date_today = datetime.utcnow().strftime("%Y-%m-%d")
    db = client.markets.markets_data
    try:
        #db.update_one({"_id": date_today}, {"$addToSet": {"coins": new_data}}, upsert=True) # "coins.id": {"$ne" : coin_id }  , upsert=True
        db.update_one({}, {"$addToSet": {'pairs':new_data}}, upsert=True)
    except Exception as e:
        print(e)
    return

def api_exchanges():
    headers = {
        'accept': 'application/json',
    }
    response = requests.get('https://api.coingecko.com/api/v3/exchanges/list', headers=headers)
    return response.json()

def api_tikers(exchange_id):
    pass

def get_ids_exch_list(exchanges_list):
    list_exch_urls = []
    for exchange in exchanges_list:
        list_exch_urls.append(f'https://api.coingecko.com/api/v3/exchanges/{exchange["id"]}/tickers?depth=true')
    return list_exch_urls

def add_links(data):
    main_page = 'https://www.coingecko.com/en/exchanges/'
    data_dict = {}
    for i in data:
        i['url'] = main_page + i['id']
        data_dict[i['id']] = {'url': main_page + i['id']}
    return data_dict

def save_mongo(data, name):
    db = client.markets
    markets_db = db[name]
    markets_db.delete_many({})
    if name == 'list_exchanges':
        markets_db.insert_one(data)
    else:
        markets_db.insert_many(data)

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

def handler_exchenges(exchanges_ids, proxies_list):
    """ Run ayncio corutines. 100 coro for each loop """
    a = int(round(len(exchanges_ids) / 100, 0))
    if a == 0:
        a = 1
    j = 100
    for i in range(a):
        t_now = time()
        if j > len(exchanges_ids):
            if j == 100:
                asyncio.run(gen_main(exchanges_ids, proxies_list))
            else:
                asyncio.run(gen_main(exchanges_ids[j-100:], proxies_list))
        else:
            asyncio.run(gen_main(exchanges_ids[j-100:j], proxies_list))

        dtime = time() - t_now
        #print(j, 'time', (time() - t0) / 60, f' delta time {dtime}')
        j += 100
    return

def append_statistics(filepath, new_data):
    try:
        with open(filepath, 'r') as fp:
            information = json.load(fp)
        information["pairs"].append(new_data)
    except:
        information = {"pairs": [new_data]}
        print('No file')

    with open(filepath, 'w') as fp:
        json.dump(information, fp, indent=4)
    return

def graber(data):
    date_today = datetime.utcnow().strftime("%Y-%m-%d")
    list_data = []
    for pair in data:
        try:
            var_dict = {}
            var_dict['exchange'] = pair['market']['identifier']
            var_dict['coin_name'] = pair['coin_id']
            var_dict['pair'] = f"{pair['base']}/{pair['target']}"
            try:
                var_dict['price'] = round(pair['converted_volume']['usd'], 2)
                var_dict['spread'] = round(pair['bid_ask_spread_percentage'], 2)
                var_dict['depthUpper2'] = round(pair['cost_to_move_up_usd'], 2)
                var_dict['depthDownper2'] = round(pair['cost_to_move_down_usd'], 2)
                var_dict['volume_ex'] = round(pair['volume'], 2)
            except:
                var_dict['price'] = pair['converted_volume']['usd']
                var_dict['spread'] = pair['bid_ask_spread_percentage']
                var_dict['depthUpper2'] = pair['cost_to_move_up_usd']
                var_dict['depthDownper2'] = pair['cost_to_move_down_usd']
                var_dict['volume_ex'] = pair['volume']
            var_dict['total_volume'] = 0
            var_dict['date_update'] = date_today
            list_data.append(var_dict)
        except:
            'Graber error'
    return list_data
        #append_statistics('datas.json', var_dict)
        #update_markets_mongo(var_dict)
        #print(var_dict)
        #print(LIST_PAIR)
        #print('-------------------------------------')
        #yield var_dict


async def get_html_io(client, url, proxy):
    """ Connect to Coingecko for get response from coin """
    proxy = f'http://vvyyimhm-dest:vu4t6rhgy97x @{proxy}'
    try:
        async with client.get(url, proxy=proxy) as response:
            data = await response.json()
            if "&page" not in url:
                try:
                    pages_count = response.headers["Link"].split('>; rel="last"')[0].split('?depth=true&page=')[1]
                    exch = url.split('v3/exchanges/')[1].split('/tickers?depth')[0]
                    URLS_LIST.append({"exchange": exch, "pages_count": pages_count})
                except Exception as e:
                    'No'
            LIST_PAIR.extend(data["tickers"])
            #graber(data)

    except Exception as e:
        print('Except get_html_io', e)


async def get_data_io(url, proxy):
    """Create aiohttp ClientSession for each request"""
    try:
        loop = asyncio.get_running_loop()
        timeout = aiohttp.ClientTimeout(total=100)
        async with aiohttp.ClientSession(loop=loop, trust_env=True, timeout=timeout) as client:
            data = await get_html_io(client, url, proxy)
    except:
        print('Exception error get_data_io')

async def gen_main(urls, proxies_list):
    """Create tasks for aiohttp corutine"""
    try:
        data = await asyncio.gather(*[get_data_io(url, p) for url, p in zip(urls, proxies_list)])
        #print('Ok')
    except:
        print('Exception error get_main function asyncio')

def create_links_other_pages(urls_list):
    all_urls = []
    for unit in urls_list:
        i = 2
        while i <= int(unit["pages_count"]):
            all_urls.append(f'https://api.coingecko.com/api/v3/exchanges/{unit["exchange"]}/tickers?depth=true&page={i}>')
            i+=1
    return all_urls

def check_list(data):
    pairs = []
    for unit in data:
        pairs.append(unit['exchange'] + unit['pair'])
    print("Check result list")
    print(len(pairs))
    print(len(set(pairs)))
    return


#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    proxies_list = get_proxies_list('Webshare')
    exch_dict = add_links(api_exchanges())
    save_mongo(exch_dict, 'list_exchanges')
    handler_exchenges(get_ids_exch_list(api_exchanges()), proxies_list)
    other_urls = create_links_other_pages(URLS_LIST)
    handler_exchenges(other_urls, proxies_list)
    result_list = graber(LIST_PAIR)
    #check_list(result_list)
    save_mongo(result_list, "markets_data")
