from get_links_with_API import get_dict_coins_id as get_ids

import os
import requests
import asyncio
import aiohttp
from aiohttp import web
from datetime import datetime
import json
import locale
from pymongo import MongoClient
import random
from time import time, sleep

client = MongoClient("mongodb+srv://doadmin:O627m5J9EjxXQ081@db-mongodb-fra1-43282-c88d22b1.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def get_proxies_list(file_name):
    try:
        with open(os.path.join(BASE_DIR, file_name), 'r') as f:
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

def get_links_for_APIrequests():
    coins_lists = get_ids()
    links_list = []
    for coin in coins_lists:
        links_list.append(f'https://api.coingecko.com/api/v3/coins/{coin}?localization=false&tickers=false&market_data=false&sparkline=false')
    #print(links_list)
    return links_list

def load_api_dev_data_mongo():
    date_today = datetime.utcnow().strftime("%Y-%m-%d")
    db = client.test.coins_data
    try:
        data = db.find_one({'_id': date_today})
    except:
        date_yerstoday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        data = db.find_one({'_id': date_yerstoday})
    return data['coins']

def create_mongo_document():
    date_today = datetime.utcnow().strftime("%Y-%m-%d")
    db = client.test.coins_data
    resp = db.update_one( {"_id": date_today},
                          {"$set": {"update": "yes"}},
                          upsert=True)


def create_mongo_twscrname():
    db = client.test.twscrname
    resp = db.update_one( {"_id": "twscrname"},
                          {"$set": {"update": "yes"}},
                          upsert=True)


# TO DO update function
def update_Mongo_document(new_data, coin_id):
    date_today = datetime.utcnow().strftime("%Y-%m-%d")
    db = client.test.coins_data
    try:
        #db.update_one({"_id": date_today}, {"$addToSet": {"coins": new_data}}, upsert=True) # "coins.id": {"$ne" : coin_id }  , upsert=True
        db.update_one( {"_id": date_today, "coins.id": {"$ne": coin_id}},
                       {"$push": {"coins": new_data}},
                       False, True)
        print('MONGO UPDATED')
    except Exception as e:
        print('MONGO ERROR')
        print(e)



def update_Mongo_twscrname(new_data, coin_id):
    db = client.test.twscrname
    try:
        db.update_one( {"_id": 'twscrname', "coins.id": {"$ne": coin_id}},
                       {"$push": {"coins": new_data}},
                       False, True)
    except Exception as e:
        print("twscrname error")
        print(e)


def write_error_mongoDB(url_error):
    date_today = datetime.utcnow().strftime("%Y-%m-%d")
    db = client.test.coins_data_errors
    db.update_one({"_id": date_today}, {"$addToSet": {"url": url_error}}, upsert=True)


def check_list_errors():
    date_today = datetime.utcnow().strftime("%Y-%m-%d")
    errors = client.test.coins_data_errors
    db = client.test.coins_data
    if errors.find_one({'_id': date_today}) != None:  # TO DO CHECK THIS Function
        urls_error_list = errors.find_one({'_id': date_today})["url"]
        for url in urls_error_list:
            coin_id = url.split('v3/coins/')[1].split('?localization=false')[0]
            if db.find_one({"$and": [{"_id": date_today}, {"coins": {"$elemMatch": {'id': coin_id}}}]}, {"id": coin_id}) != None:
                errors.update_one({"_id": date_today},
                    {"$pull": {"url": f'https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=false&sparkline=false'}}
                    )
        urls_error_list = errors.find_one({'_id': date_today})["url"]
        if len(urls_error_list) == 0:
            errors.delete_one({'_id': date_today})
            return []
        return urls_error_list
    return []

# TO DO create function
def create_coinData_dict(data):
    result_data = {
                'id': data['id'],
                'tw_f': data['community_data']['twitter_followers'],
                'tel_users_count': data['community_data']['telegram_channel_user_count'],
                'stars': data['developer_data']['stars'],
                'subscribers': data['developer_data']['subscribers'],
                't_i': data['developer_data']['total_issues'],
                'c_i': data['developer_data']['closed_issues'],
                'p_r_m': data['developer_data']['pull_requests_merged'],
                'p_r_c': data['developer_data']['pull_request_contributors'],
                'categories': data['categories'],
            #    'TwSN': data['links']['twitter_screen_name']
            }
    print(result_data)
    update_Mongo_document(result_data, data['id'])


def push_tw_screen_name(data):
    result_data = {
                'id': data['id'],
                'TwSN': data['links']['twitter_screen_name']
            }
    update_Mongo_twscrname(result_data, data['id'])



async def get_api_data(client, url, proxy):
    proxy = f'http://vvyyimhm:vu4t6rhgy97x @{proxy}'
    headers = {
        'accept': 'application/json',
    }
    try:
        async with client.get(url, proxy=proxy, headers=headers) as response:
            print(proxy, url)
            print(response.status)
        #async with client.get('https://coinmarketcap.com/', proxy=proxy) as response:
            r = await response.json()

            create_coinData_dict(r)
            try:
                push_tw_screen_name(r)
            except:
                print('push tw screen name error')
            #TO DO update mongo doucument
    except Exception as e:
        #print('Exception in get_api_data', e)
        write_error_mongoDB(url)
        await asyncio.sleep(30)
        print('Exception in get_api_data', e)

async def create_clients(url, proxy):
    """Create aiohttp ClientSession for each request"""
    try:
        loop = asyncio.get_running_loop()
        async with aiohttp.ClientSession(loop=loop, trust_env=True) as client:
            await get_api_data(client, url, proxy)
    except:
        print('Exception in create_clients')

async def gen_main(urls, proxies_list):
    """Create tasks for aiohttp corutine"""
    try:
        data = await asyncio.gather(*[create_clients(url, proxy) for url, proxy in zip(urls, proxies_list)])
        #print('Ok')
    except:
        print('Exception error get_main function asyncio')

def proxies_list_long(proxies_list, count):
    long_list = []
    i = 0
    while i < count:
        long_list.append(random.choice(proxies_list))
        i+=1
    return long_list

def handler(coins, proxies_list):
    """ Run ayncio corutines. 100 coro for each loop """
    len_proxies_list = len(proxies_list)
    a = int(round(len(coins) / len_proxies_list, 0))
    if a == 0:
        a = 1
    j = len_proxies_list
    for i in range(a):
        t_now = time()
        if j > len(coins):
            if j == len_proxies_list:
                asyncio.run(gen_main(coins, proxies_list))
            else:
                asyncio.run(gen_main(coins[j-len_proxies_list:], proxies_list))
        else:
            asyncio.run(gen_main(coins[j-len_proxies_list:j], proxies_list))

        dtime = time() - t_now
        #print(j, 'time', (time() - t0) / 60, f' delta time {dtime}')
        print(j)
        j += len_proxies_list


def errors_handler(urls_error_list, proxies_list):
    i = 0
    print("Start work with errors")
    while i < 5 and len(urls_error_list) > 0:
        handler(urls_error_list, proxies_list)
        urls_error_list = check_list_errors()
        i+=1


def add_coins_cat(list_cat, list_coins):
    result_list = []
    for unit in list_cat:
        unit['coins'] = []
        for coin in list_coins:
            if unit['name'] in coin['categories']:
                unit['coins'].append(coin['id'])
        result_list.append(unit)
    return result_list


def get_request_list_cat():
    url = "https://api.coingecko.com/api/v3/coins/categories/list"
    headers = {
        'accept': 'application/json',
    }
    result_list = []
    get_request = requests.get(url, headers=headers)
    list_cat = get_request.json()
    return list_cat


def create_list_categories():
    list_cat = get_request_list_cat()
    list_coins = load_api_dev_data_mongo()
    result_list = add_coins_cat(list_cat, list_coins)
    return result_list

def save_mongo_categories(result_list):
    db = client.test
    pars_data = db['categories']
    save_dict = {'data': result_list}
    try:
        pars_data.drop()
    except:
        print("No data for del")
    pars_data.insert_one(save_dict)



def get_coins():
    proxies_list = get_proxies_list('scrapers/Webshare')
    #print(proxies_list)
    create_mongo_document()
    try:
        create_mongo_twscrname()
    except:
        print("Can't create new twscrname doucument")
    handler(get_links_for_APIrequests(), proxies_list)
    errors_handler(check_list_errors(), proxies_list)
    save_mongo_categories(create_list_categories())
    return

#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print(BASE_DIR)
    get_coins()
    #save_mongo_categories(create_list_categories())
