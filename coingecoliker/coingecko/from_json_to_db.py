from wsgi import *
from .models import Coin
import json

def load_json():
    with open('../result.json', 'r') as f:
        data_dict = json.load(f)
    return data_dict


def save_to_DB(data_dict):
    for coin in data_dict:
        Coin.coin_name = coin
        Coin.total_value = data_dict.get(coin)['total_val']
        Coin.difference = data_dict.get(coin)['different_val']
        Coin.pub_date = datetime.now()
        Coin.save()


print(load_json())

for q in Coin:
    print(q.coin_name)

