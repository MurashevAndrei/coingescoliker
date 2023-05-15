from get_links_with_API import get_dict_coins_id as get_ids
from get_coins_detail_save_mongo import get_coins
from compare_alert import main_notification
import asyncio
import aiohttp
import sys
from pymongo import MongoClient
import requests
from datetime import datetime
from time import sleep
from fake_useragent import UserAgent
import multiprocessing
from time import time, sleep
import json


import random


client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

def load_all_each_hour():
    db = client.test.each_hour
    data = db.find()
    return data

def find_all_date_MongoDB():
    db = client.test
    data_db = db['list_ids']
    data_names = data_db.find_one()
    return sorted(data_names['ids'], reverse=True)

def save_mongo_ids_list(data_ids):
    db = client.test.list_ids
    db.insert_one(data_ids)


#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    collection = load_all_each_hour()
    ids_list = []
    for unit in collection:
        ids_list.append(unit["_id"])
    data_ids = {"ids": sorted(ids_list, reverse=True)}
    save_mongo_ids_list(data_ids)
    print(ids_list)
    print(len(ids_list))

    #work_list = find_all_date_MongoDB()
    #for i in work_list:
    #    print(i)
