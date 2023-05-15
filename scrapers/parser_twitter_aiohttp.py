from get_links_with_API import get_dict_coins_id as get_ids
from parser_aiohttp import get_proxies_list
import asyncio
import aiohttp
import sys
#from pymongo import MongoClient
from base import client, connect_db, load_mongo, bearer_token
import requests
from datetime import datetime, timedelta
import multiprocessing
from time import time, sleep
import json
import random


def save_mongo_communities(data_dict):
    dict_for_save = {}
    dict_for_save['_id'] = 'communities_data'
    dict_for_save['data'] = data_dict
    pars_data = connect_db('t', 'communities_data')
    try:
        pars_data.insert_one(dict_for_save)
    except:
        pars_data.drop() # Drop all data_dic from mongoDB
        pars_data.insert_one(dict_for_save) # Save new data_dic to mongoDB


def twitter_screen_name_graber(data, coin_id):
    # Function scrap twitter screen_name for each coins page and return
    coin = {}
    try:
        plt = data["TwSN"]
        if plt == '':
            plt = False
        coin[coin_id] = {'twitter_screen_name': plt, 'twitter_url': f'https://twitter.com/{plt}', 'twitter_id': False}
    except:
        coin[coin_id] = {'twitter_screen_name': False, 'twitter_id': False}
    return coin[coin_id]

def coins_get_tw_accounts(coins_ids_list, communities_dict):
    data_list = load_mongo('test', 'twscrname', 'twscrname', data_get='coins')
    for coin in data_list:
        if coin["id"] in coins_ids_list:
            communities_dict[coin["id"]] = twitter_screen_name_graber(coin, coin["id"])
    return communities_dict


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
    #bearer_token = 'AAAAAAAAAAAAAAAAAAAAALI%2FNAEAAAAAV%2BtcsYGeiAWoklZzSMsZWBOQ9eg%3D1eagO1TuTlmdhaLj49kE1C6c1YJgtqqwzG9DYNJVL2Nngq823M'
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    json_response = connect_to_endpoint(f'https://api.twitter.com/1.1/users/show.json?screen_name={screen_name}', headers)
    if json_response == '{"errors":[{"message":"Rate limit exceeded","code":88}]}':
        print('Sleep 200 seconds')
        sleep(200)
    elif json_response == '{"errors":[{"code":50,"message":"User not found."}]}' or json_response == '{"errors":[{"code":63,"message":"User has been suspended."}]}':
        return json_response.split(',"message":"')[1].split('."}]}')[0]

    return json_response['id']

def add_count_follower(followings, communities_dict):
    for coin in communities_dict:
        try:
            i = 0
            for item in followings:
                try:
                    if communities_dict[coin]["twitter_id"] in item["followings_list"]:
                        i += 1
                except:
                    continue

            communities_dict[coin]['followers_amount'] = i
        except:
            continue
    return communities_dict


def get_communities_dict():
    try:
        communities_dict = load_mongo('test', 'communities_data', 'communities_data')
    except:
        communities_dict = {}
    return communities_dict


def get_coins_list_to_check_twId(coins, communities_dict):
    coins = list(set(coins) - set(list(communities_dict.keys()))) # create coins list for new coins on Coingecko
    print(f'Load {len(coins)} new coins from Coingecko')
    sleep(1)
    coins = list(set(coins + check_coins_twitter(communities_dict, 'twitter_screen_name')))

    print(f'{len(coins)} coins will be check for existing twitter account')
    sleep(2)

    return coins


def coins_to_get_twitter_id(communities_dict):
    coins_to_get_twitter_id = list(set(list(communities_dict.keys())) - set(check_coins_twitter(communities_dict, 'twitter_screen_name')))
    ids = set(check_coins_twitter(communities_dict, 'twitter_id'))
    print(len(ids))
    #coins_to_get_twitter_id = list(ids)
    coins_to_get_twitter_id = list(set(coins_to_get_twitter_id) & ids)

    print(len(coins_to_get_twitter_id), ' load for get twitter id')
    return coins_to_get_twitter_id

def get_result_comunities_dict(coins, coins_to_get_twitter_id, communities_dict):
    for coin in coins_to_get_twitter_id:
            start_time = time()
            try:
                twitter_id = get_twitter_id_value(communities_dict[coin]['twitter_screen_name'])
                if twitter_id == 'User has been suspended' or twitter_id == 'User not found':
                    communities_dict[coin]['twitter_screen_name'] = twitter_id
                communities_dict[coin]['twitter_id'] = twitter_id
                print(communities_dict[coin])
                if time() - start_time < timeout_show:
                    sleep(1)
            except:
                save_mongo_communities(communities_dict)
                print('no data ------- ', coin)
    return communities_dict


def get_communities_dict_with_followings(communities_dict):
    try:
        followings = load_mongo('test', 'twitter_followings', 'G_followings')
        communities_dict = add_count_follower(followings, communities_dict)

        save_mongo_communities(communities_dict)
    except:
        'no data'

#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    errors = {}
    #proxies_list = get_proxies_list('Webshare')
    GEN_ERROR = {}
    coins = get_ids()
    #communities_dict = get_communities_dict()
    communities_dict  = {}
    t0 = time()

    coins = get_coins_list_to_check_twId(coins, communities_dict)
    communities_dict = coins_get_tw_accounts(coins, communities_dict)
    save_mongo_communities(communities_dict)

    timeout_show = timedelta(seconds=60.0*15/900+0.1).seconds

    coins_to_get_twitter_id = coins_to_get_twitter_id(communities_dict)
    communities_dict = get_result_comunities_dict(coins, coins_to_get_twitter_id, communities_dict)
    save_mongo_communities(communities_dict)
    print((time() - t0))
'''
    def main(communities_dict):
        coins
        communities_dict
        save_mongo_communities(communities_dict)

'''
