from get_links_with_API import get_dict_coins_id as get_ids
from parser_aiohttp import get_proxies_list
from parser_twitter_aiohttp import load_Mongo_communities, save_mongo_communities, add_count_follower
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

class TokenBearer():
    """docstring for ."""

    def __init__(self):
        self.start_time = time()
        self.counter = 0
        self.bearer_token = "AAAAAAAAAAAAAAAAAAAAALI%2FNAEAAAAAV%2BtcsYGeiAWoklZzSMsZWBOQ9eg%3D1eagO1TuTlmdhaLj49kE1C6c1YJgtqqwzG9DYNJVL2Nngq823M"
        self.bearer_token1 = "AAAAAAAAAAAAAAAAAAAAALI%2FNAEAAAAAV%2BtcsYGeiAWoklZzSMsZWBOQ9eg%3D1eagO1TuTlmdhaLj49kE1C6c1YJgtqqwzG9DYNJVL2Nngq823M"
        self.bearer_token2 = "AAAAAAAAAAAAAAAAAAAAAGLXSwEAAAAAyTqZujOFy04nUJ0F18DsrG0X0FE%3DfpJ1eeJJ9bHuWBD8PJLgQK1V2ukDu5LBT9kWfgjlVBVw9KoHvS"
        self.blocked_token = {
            "1": {"status": "unlocked", "time": 0},
            "2": {"status": "unlocked", "time": 0}
        }

    def locker(self, number, status_token):
        if self.blocked_token[number]["status"] == status_token:
            return
        self.blocked_token[number]["status"] = status_token
        if number == "1" and status_token == "blocked":
            self.blocked_token[number]["time"] = time()
        elif number == "2" and status_token == "blocked":
            self.blocked_token[number]["time"] = time()
        elif number == "1" and status_token == "unlocked":
            self.bearer_token = self.bearer_token1
        elif number == "2" and status_token == "unlocked":
            self.bearer_token = self.bearer_token1

    def bloked_time_checker(self, number):
        if int((time() - self.blocked_token[number]["time"])) > 15*60:
            self.blocked_token[number]["status"] = "unlocked"
            return False
        else:
            return True

    def changer(self):
        if self.bearer_token == self.bearer_token1:
            if self.blocked_token["2"]["status"] == "blocked":
                if self.bloked_time_checker("2"):
                    print("Token can't be change because another token are blocked")
                    return
            self.bearer_token = self.bearer_token2
        elif self.bearer_token == self.bearer_token2:
            if self.blocked_token["1"]["status"] == "blocked":
                if self.bloked_time_checker("1"):
                    print("Token can't be change because anoter token are blocked")
                    return
            self.bearer_token = self.bearer_token1
        print("Token change")

    def followings_counter(self):
        self.counter += 1


tokenBear = TokenBearer()

BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAALI%2FNAEAAAAAV%2BtcsYGeiAWoklZzSMsZWBOQ9eg%3D1eagO1TuTlmdhaLj49kE1C6c1YJgtqqwzG9DYNJVL2Nngq823M'

def drop_temp_G_followings(name_document):
    db = client.test.twitter_followings
    db.delete_one({'_id': name_document})

#def save_mongo_token(data_dict):
#    db = client.test.test_followings

def save_mongo_followings(data_dict, name_document):
    dict_for_save = {}
    dict_for_save['_id'] = name_document
    dict_for_save['data'] = data_dict
    db = client.test.twitter_followings
    pars_data = db
    try:
        pars_data.insert_one(dict_for_save)
    except:
        pars_data.delete_one({'_id': name_document}) # Delete documemt from mongoDB
        pars_data.insert_one(dict_for_save) # Save new data_dic to mongoDB

def load_Mongo_followings(data_name):
    db = client.test.twitter_followings
    data_ = db.find_one({'_id': data_name})
    data_dict = data_.get('data')
    return data_dict

def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        return response.text
    return response.json()

def token_checker():
    print("Token checker in")
    if tokenBear.bearer_token == tokenBear.bearer_token1:
        tokenBear.locker("1", "blocked")
        print(tokenBear.blocked_token["1"]["status"])
        print(tokenBear.blocked_token["1"]["time"])
    elif tokenBear.bearer_token == tokenBear.bearer_token2:
        tokenBear.locker("2", "blocked")
        print(tokenBear.blocked_token["2"]["status"])
        print(tokenBear.blocked_token["2"]["time"])
    if tokenBear.blocked_token["1"]["status"] == "blocked" and tokenBear.blocked_token["2"]["status"] == "blocked":
        if tokenBear.blocked_token["2"]["time"] > tokenBear.blocked_token["1"]["time"]:
            sleep_time = int(15*60 - (time() - tokenBear.blocked_token["1"]["time"])) / 3
            if sleep_time > 0:
                print("sleep ", sleep_time)
                sleep(sleep_time)
            tokenBear.locker("1", "unlocked")

        elif tokenBear.blocked_token["1"]["time"] > tokenBear.blocked_token["2"]["time"]:
            sleep_time = int(15*60 - (time() - tokenBear.blocked_token["2"]["time"])) / 3
            if sleep_time > 0:
                print("sleep ", sleep_time)
                sleep(sleep_time)
            tokenBear.locker("2", "unlocked")

    return tokenBear.bearer_token

def get_twitter_followings_list(twitter_id, pagination_token=None):
    i = True
    while i:
        headers = {"Authorization": "Bearer {}".format(tokenBear.bearer_token)}
        if pagination_token == None:
            json_response = connect_to_endpoint(f'https://api.twitter.com/2/users/{twitter_id}/following?max_results=1000', headers)
        else:
            json_response = connect_to_endpoint(f'https://api.twitter.com/2/users/{twitter_id}/following?max_results=1000&pagination_token={pagination_token}', headers)

        if isinstance(json_response, str):
            print(f'Bearer token was blocked {tokenBear.bearer_token}')
            token_checker()
            tokenBear.changer()
        else:
            print('Good qeury')
            tokenBear.changer()
            print("sleep 30 seconds")
            sleep(30)
            i = False
    return json_response

def get_twitter_ids_coins_list(communities_dict):
    list_twitter_ids_coins = []
    for coin in communities_dict:
        try:
            if isinstance(communities_dict[coin]['twitter_id'], int) and communities_dict[coin]['twitter_id']:
                list_twitter_ids_coins.append(communities_dict[coin]['twitter_id'])
        except Exception as e:
            print(e, 'no data', coin)
    print(len(list_twitter_ids_coins), "Ids twitter coins amount")
    return list_twitter_ids_coins

def create_list_ids(data):
    followings_list = []
    for i in data:
        if i['id'] == "1426592427377258497":
            print("FURURKURU")
        try:
            followings_list.append(int(i["id"]))
        except:
            'no data'
    return followings_list

def update_G_followings(followings, new_followings):
    """ Get 2 followings dict (old and new) and add or delete followings """
    try:
        old_id_list = create_list_ids(followings)
        new_id_list = create_list_ids(new_followings)
        ids_to_add = list(set(new_id_list) - set(old_id_list))
        ids_to_del = list(set(old_id_list) - set(new_id_list))
        print('id to add - ', len(ids_to_add), 'id to del - ', len(ids_to_del))
        if len(ids_to_add) > 0:
            for elem in new_followings:
                try:
                    if int(elem['id']) in ids_to_add:
                        print(elem, ' to add')
                        followings.insert(0, elem)
                except Exception as e:
                    print(e, "In loop 1 update G", elem)
        added_followings = []
        if len(ids_to_del) > 0:
            for elem in followings:
                try:
                    if int(elem['id']) in new_id_list:
                        added_followings.insert(0, elem)
                except Exception as e:
                    print(e, "In loop added update G", elem)
            followings = added_followings
        check_id_list = create_list_ids(followings)
        if len(set(check_id_list) - set(new_id_list)) == 0:
            print('Update following complite')
        else:
            print("Something wrong with update followings list")
            print(len(set(check_id_list) - set(new_id_list)))
    except Exception as e:
        print(e, "In update G")
    return followings

def get_new_followings(AccountId):
    followings_list = []
    result = get_twitter_followings_list(AccountId)
    while True:
        try:
            followings_list += result['data']
            print(AccountId, result['meta']['result_count'], len(followings_list))
            if isinstance(result['meta']['result_count'], int) and result['meta']['result_count'] == 1000:
                pagination_token = result['meta']['next_token']
                result = get_twitter_followings_list(AccountId, pagination_token)
            else:
                break
        except Exception as e:
            print(e, " in get_new_followings")
            break
    print(f"New followings list amount for id {AccountId} is ", len(followings_list))
    return followings_list

def checker_id(followings):
    print("checker_id")
    for unit in followings:
        if str(unit['id']) == "1426592427377258497":
            print(unit)
        try:
            if 1426592427377258497 in unit["followings_list"]:
                print(unit)
        except Exception as e:
            print(e, checker_id)

    return

def time_checker(start_time):
    workTimeAmount = (time() - start_time)/60
    answer = True
    if workTimeAmount > 1310: #1350
        answer = False
        print("Overtime in time_checker")
    return answer

def sort_by_date(work_list):
    """TO DO SORT FUNCTION"""
    result_list = []
    today = datetime.today().strftime('%Y-%m-%d')
    yersterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    for i in work_list:
        if i["update_followings"] != today and i["update_followings"] != yersterday:
            result_list.insert(0, i)
        else:
            result_list.append(i)
    return result_list

def create_steps_lists(followings):
    first_step, second_step, third_step = [], [], []
    for unit in followings:
        try:
            if len(unit["followings_list"]) > 0:
                second_step.append(unit)

            else:
                third_step.append(unit)

        except:
            first_step.append(unit)
            print(unit)
    second_step = sort_by_date(second_step) # TO DO sort list by date update
    third_step = sort_by_date(third_step) # TO DO sort list by date update
    return first_step, second_step, third_step

def get_followings_ids_clear_list(all_followings_list, list_twitter_ids_coins):
    clear_ids_list = []
    all_followings_list = create_list_ids(all_followings_list)
    clear_ids_list = list(set(all_followings_list) & set(list_twitter_ids_coins))
    return clear_ids_list

def update_step(step, followings, list_twitter_ids_coins, start_time):
    today = datetime.today().strftime('%Y-%m-%d')
    all_in_step = len(step)
    counter_now = 0
    counter_check = 0
    i_today = 0
    for i in followings:
        try:
            if i["update_followings"] == today:
                i_today+=1
                print(i_today, "today" )
                continue
        except Exception as e:
            print("Error in update", e)
        for account in step:
            if i["id"] == account["id"]:
                all_followings_list = get_new_followings(account["id"])
                i["followings_list"] = get_followings_ids_clear_list(all_followings_list, list_twitter_ids_coins)
                clear_count = len(i["followings_list"])
                i["update_followings"] = datetime.today().strftime('%Y-%m-%d')
                print(f"Coins followings is {clear_count}")
                counter_now+=1
                tokenBear.followings_counter()
                print(i_today, " today ", counter_now, " now.", " from ", all_in_step, "Amount today counter - ", tokenBear.counter)
                try:
                    if (tokenBear.counter % 5) == 0:
                        save_mongo_followings(followings, 'temp_G_followings')
                        save_mongo_followings(followings, 'G_followings')
                        print(f"Save every 5 follwoings. Updating {tokenBear.counter}")
                        if (tokenBear.counter % 30) == 0:
                            communities_dict = add_count_follower(followings, load_Mongo_communities('communities_data'))
                            save_mongo_communities(communities_dict)
                            print("Refresh comunities data")
                except Exception as e:
                    print("dont save because ", e)

        if not time_checker(tokenBear.start_time):
            print("Overtime")
            return followings, False
            # TO DO save point for next day
    save_mongo_followings(followings, 'temp_G_followings')
    save_mongo_followings(followings, 'G_followings')
    communities_dict = add_count_follower(followings, load_Mongo_communities('communities_data'))
    save_mongo_communities(communities_dict)
    return followings, True




#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    t0 = time()

    GarryId = '44813348'
    communities_dict = load_Mongo_communities('communities_data')
    list_twitter_ids_coins = get_twitter_ids_coins_list(communities_dict)

    try:
        followings = load_Mongo_followings('G_followings')
        new_followings = get_new_followings(GarryId)
        followings = update_G_followings(followings, new_followings)
    except:
        followings = get_new_followings(GarryId)
        save_mongo_followings(followings, 'G_followings')

    first_step, second_step, third_step = create_steps_lists(followings)
    print(len(first_step), len(second_step), len(third_step))
    if len(first_step) > 0:
        followings, check_time = update_step(first_step, followings, list_twitter_ids_coins, t0)
    print("End 1 step")
    check_time = time_checker(t0)
    print(check_time, "Check Time")
    if check_time and len(second_step) > 0:
        print("Start step 2")
        followings, check_time = update_step(second_step, followings, list_twitter_ids_coins, t0)
    check_time = time_checker(t0)
    print(check_time, "Check Time")
    if check_time and len(third_step) > 0:
        followings, check_time = update_step(third_step, followings, list_twitter_ids_coins, t0)
        print(check_time) # TO DO logic time checker 2


    t1 = (time() - t0)/3600
    print("END WORK time - ", t1)
