from pymongo import MongoClient
import os
import json


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

def save_result(file_name):
    path = os.path.join(BASE_DIR, 'coingecko', 'static', 'result', file_name)
    db = client.results
    name = file_name.split('.')[0]
    table = db[name]
    data = load_json(path)
    #table.insert_one(data)
    print(table.find_one())


# load json data and return {name_coin: people like this}
def load_json(file_name):
    with open(file_name, 'r') as f:
        data_dict = json.load(f)
    return data_dict

def save_parsers(file_name):
    db = client.parsers
    name = file_name.split('.')[0]
    parser = db[name]
    path = os.path.join(BASE_DIR, 'coingecko', 'static', 'parsers', file_name)
    data = load_json(path)
    #parser.insert_one(data)
    print(parser.find_one())


def main(dir_name):

    path = os.path.join(BASE_DIR, 'coingecko', 'static', dir_name)
    file_names = os.listdir(path=path)
    file_names = sorted(file_names, reverse=True)
    for file_name in file_names:
        if dir_name == 'result':
            save_result(file_name)
        else:
            save_parsers(file_name)

main('result')
main('parsers')
