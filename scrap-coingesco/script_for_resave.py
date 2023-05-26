import os
import requests
import json
import sys
from datetime import datetime
from pymongo import MongoClient


client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

def load_mongo():
    db = client.consol_heroku.ch
    collection = db.find()
    for i in collection:
        data = i
        print(data)
    return data.get('data')

def save_mongo(coin):
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

save_mongo(load_mongo())
