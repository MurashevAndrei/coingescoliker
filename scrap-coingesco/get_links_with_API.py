import requests
import json

def get_dict_coins_id():

    headers = {
        'accept': 'application/json',
    }
    
    coins_id = requests.get('https://api.coingecko.com/api/v3/coins/list', headers=headers)
    coins_id = coins_id.json()
    coins_id_lists = []
    for coin in coins_id:
        if '.' in coin.get('id'):
            continue
        coins_id_lists.append(coin.get('id'))
        if '.' in coin.get('id'):
            print(coin.get('id'))
    return coins_id_lists

def get_links_for_parse():
    coins_lists = get_dict_coins_id()
    links_list = []
    for coin in coins_lists:
        links_list.append('https://www.coingecko.com/en/coins/' + coin)
    print(len(links_list))
    return links_list
