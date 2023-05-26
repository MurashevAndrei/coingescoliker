import json
import os
from datetime import datetime, timedelta
import datetime as DT
from pymongo import MongoClient
import json

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

def find_all_date_MongoDB():
    db = client.test
    data_db = db['list_ids']
    data_names = data_db.find_one()
    return sorted(data_names['ids'], reverse=True)

def load_MongoDB(data_name):
    db = client.test.each_hour
    data_ = db.find_one({'_id': data_name})
    data_dict = data_.get('data')
    return data_dict


def create_new_ids_list(x_date, all_list):
    result_list = []
    for i, unit in enumerate(all_list):
        if datetime.strptime(unit, '%Y-%m-%d_%H:%M') > x_date:
            result_list.append(unit)
            continue
        if datetime.strptime(unit, '%Y-%m-%d_%H:%M').day != datetime.strptime(all_list[i-1], '%Y-%m-%d_%H:%M').day:
            result_list.append(unit)
    return result_list

def get_all_each_hours(new_list):
    list_new_data = []
    for unit in new_list:
        list_new_data.append({unit: load_MongoDB(unit)})
    return list_new_data


def save_json(list_all_data):
    with open('each_days.json', 'w') as f:
        json.dump(list_all_data, f, indent=4)

def remove_each_hours(list_deleted):
    db = client.test.each_hour
    for unit in list_deleted:
        try:
            db.delete_one({"_id": unit})
        except:
            continue
    return

def rewrite_list_ids(new_ids):
    db = client.test.list_ids
    db.delete_many({})
    db.insert_one(new_ids)
    return

def get_new_list(all_list):
    thirty_days_ago = datetime.today() - timedelta(days=40)
    new_list = create_new_ids_list(thirty_days_ago, all_list)
    return new_list

def get_list_after_date(all_list, date_after):
    list_d = []
    x_date = datetime.strptime(date_after, '%Y-%m-%d_%H:%M')
    for unit in all_list:
        if datetime.strptime(unit, '%Y-%m-%d_%H:%M') > x_date:
            list_d.append(unit)
            continue
    return list_d





#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    all_list = find_all_date_MongoDB()
    new_list = get_new_list(all_list)
    list_deleted = list(set(all_list) - set(new_list))
    #list_deleted = get_list_after_date(all_list, "2021-07-13_01:07")
    print(sorted(list_deleted, reverse=True), len(list_deleted))

    remove_each_hours(list_deleted)
    rewrite_list_ids({"ids": new_list})
