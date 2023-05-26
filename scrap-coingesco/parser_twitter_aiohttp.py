from get_links_with_API import get_dict_coins_id as get_ids
from parser_aiohttp import get_proxies_list
#from parser_followings import load_Mongo_followings
import asyncio
import aiohttp
import sys
from pymongo import MongoClient
import requests
from datetime import datetime, timedelta
from time import sleep
from fake_useragent import UserAgent
import multiprocessing
from time import time, sleep
import json
import random

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

def save_mongo_communities(data_dict):
    dict_for_save = {}
    dict_for_save['_id'] = f"communities_data"
    dict_for_save['data'] = data_dict
    db = client.test
    pars_data = db['communities_data']
    try:
        pars_data.insert_one(dict_for_save)
    except:
        pars_data.drop() # Drop all data_dic from mongoDB
        pars_data.insert_one(dict_for_save) # Save new data_dic to mongoDB

def load_Mongo_communities(data_name):
    db = client.test.communities_data
    data_ = db.find_one({'_id': data_name})
    data_dict = data_.get('data')
    return data_dict

def update_Mongo_communities(old_data, new_data):
    db = client.test.communities_data
    var_db = db.find_one({'_id': data_name}).get('data')
    result = var_db.update(old_data, new_data)
    print(result)

def twitter_screen_name_graber(data, coin_id):
    """ Function scrap twitter screen_name for each coins page and return """
    coin = {}
    try:
        plt = data.split('rel="nofollow noopener" class="coin-link-tag " href="https://twitter.com/')[1].split('">')[0]
        coin[coin_id] = {'twitter_screen_name': plt, 'twitter_url': f'https://twitter.com/{plt}', 'twitter_id': False}
    except:
        coin[coin_id] = {'twitter_screen_name': False, 'twitter_id': False}
    return coin

async def get_html_io(client, coin_id, proxy):
    """ Connect to Coingecko for get response from coin """
    proxy = f'http://vvyyimhm:vu4t6rhgy97x @{proxy}'
    headers = { 'User-Agent': UserAgent().random }
    url = 'https://www.coingecko.com/en/coins/' + coin_id
    try:
        async with client.get(url, proxy=proxy, headers=headers) as response:
            if response.status != 200:
                if response.status == 404:
                    GEN_ERROR[coin_id] = f"{response.status}"
                    COMMUNITY_DICT[coin_id] = 0
                    return
                errors[coin_id] = f"{response.status}"
                return
            data = await response.text()
            coin = twitter_screen_name_graber(data, coin_id)
            COMMUNITY_DICT[coin_id] = coin[coin_id]
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
        print(j, 'time', (time() - t0) / 60, f' delta time {dtime}')
        j += 100
    return

def compair_flist(flist, llist):
    """ Compair list ids and result list --> create list for next itteration"""
    leave_list = {}
    for i in flist:
        if i not in llist:
            leave_list[i] = 'empty'
    return leave_list

def check_coins_twitter(communities_dict, checked_value):
    """ Check all coins from communities_dict. Return list id coins without 'checked_value' """
    result_list = []
    for coin in communities_dict.keys():
        try:
            if not communities_dict[coin][checked_value]:
                result_list.append(coin)
        except:
            no_data = 0
    return result_list


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        print(response.text)
        return response.text
        raise Exception(response.status_code, response.text)
    return response.json()

def get_twitter_id_value(screen_name):
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAALI%2FNAEAAAAAV%2BtcsYGeiAWoklZzSMsZWBOQ9eg%3D1eagO1TuTlmdhaLj49kE1C6c1YJgtqqwzG9DYNJVL2Nngq823M'
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    json_response = connect_to_endpoint(f'https://api.twitter.com/1.1/users/show.json?screen_name={screen_name}', headers)
    if json_response == '{"errors":[{"message":"Rate limit exceeded","code":88}]}':
        print('Sleep 200 seconds')
        sleep(200)
    elif json_response == '{"errors":[{"code":50,"message":"User not found."}]}' or json_response == '{"errors":[{"code":63,"message":"User has been suspended."}]}':
        return json_response.split(',"message":"')[1].split('."}]}')[0]

    return json_response['id']

def add_count_follower(followings, communities_dict):
    #for coin in communities_dict:
    pass

#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    errors = {}
    proxies_list = get_proxies_list('Webshare')
    coins = get_ids()
    GEN_ERROR = {}
    try:
        COMMUNITY_DICT = load_Mongo_communities('communities_data')
    except:
        COMMUNITY_DICT = {}

    coins = list(set(coins) - set(list(COMMUNITY_DICT.keys()))) # create coins list for new coins on Coingecko
    print(f'Load {len(coins)} new coins from Coingecko')
    sleep(1)
    coins = list(set(coins + check_coins_twitter(COMMUNITY_DICT, 'twitter_screen_name')))
    print(f'{len(coins)} coins will be check for existing twitter account')
    sleep(2)

    t0 = time()

    first_list = coins
    handler(coins, proxies_list) # Run general scrap loop

    stop = 10
    while len(errors) > 0 and stop != 0: # Run second loop for errors
        print(len(first_list), '  >  ', len(list(COMMUNITY_DICT.keys())))
        coins = list(errors.keys())
        errors = {}
        handler(coins, proxies_list)
        stop -= 1
        if len(first_list) > len(list(COMMUNITY_DICT.keys())):
            errors = compair_flist(first_list, list(COMMUNITY_DICT.keys()))
            sleep(4)

    save_mongo_communities(COMMUNITY_DICT)
    print('Load - ', len(first_list), 'get data -', len(COMMUNITY_DICT), 'errors - ', len(GEN_ERROR))


    coins_to_get_twitter_id = list(set(list(COMMUNITY_DICT.keys())) - set(check_coins_twitter(COMMUNITY_DICT, 'twitter_screen_name')))
    ids = set(check_coins_twitter(COMMUNITY_DICT, 'twitter_id'))
    print(len(ids))
    coins_to_get_twitter_id = list(set(coins_to_get_twitter_id) & ids)

    print(len(coins_to_get_twitter_id), ' load for get twitter id')
    timeout_show = timedelta(seconds=60.0*15/900+0.1).seconds # limit for 1 requsts for get twitter id from twitter API
    for coin in coins_to_get_twitter_id:
        start_time = time()
        try:
            twitter_id = get_twitter_id_value(COMMUNITY_DICT[coin]['twitter_screen_name'])
            if twitter_id == 'User has been suspended' or twitter_id == 'User not found':
                COMMUNITY_DICT[coin]['twitter_screen_name'] = twitter_id
            COMMUNITY_DICT[coin]['twitter_id'] = twitter_id
            print(COMMUNITY_DICT[coin])
            if time() - start_time < timeout_show:
                sleep(1)
        except:
            save_mongo_communities(COMMUNITY_DICT)
            print('no data ------- ', coin)
    save_mongo_communities(COMMUNITY_DICT)
    """
    try:
        followings = load_Mongo_followings('G_followings')
        COMMUNITY_DICT = pfadd_count_follower(followings, COMMUNITY_DICT)
    except:
        'no data'
    """
    print((time() - t0))
