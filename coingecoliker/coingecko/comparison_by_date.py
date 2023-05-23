import json
import os
from datetime import datetime, timedelta
import datetime as DT
from pymongo import MongoClient
import coingecko.parse_coins_detail as get_detail
from .settings import BASE_DIR, MONGO_DB


client = MongoClient(MONGO_DB)

def load_MongoDB(data_name):
    db = client.test.each_hour
    data_ = db.find_one({'_id': data_name})
    data_dict = data_.get('data')
    return data_dict

def load_pricies_MongoDB(data_name):
    db = client.test.pricies
    data_ = db.find_one({'_id': f'price_{data_name}'})
    data_dict = data_.get('data')
    return data_dict

def load_Mongo_communities(data_name):
    db = client.test.communities_data
    data_ = db.find_one({'_id': data_name})
    data_dict = data_.get('data')
    return data_dict

def load_date_mongo():
    db = client.markets.date_release
    return db.find_one()['date']

def load_api_dev_data_mongo():
    date_today = datetime.utcnow().strftime("%Y-%m-%d")
    db = client.test.coins_data
    try:
        data = db.find_one({'_id': date_today})
    except:
        date_yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        data = db.find_one({'_id': date_yesterday})
    return data['coins']

def count_price_change(new_price, old_price):
    if not new_price and not old_price:
        return 0
    elif new_price and not old_price:
        return 99999
    elif not new_price and old_price:
        return -100
    else:
        return (new_price / old_price - 1) * 100

def price_compair(compair_dict, c_date1, c_date2):
    c_date1 = datetime.strptime(c_date1, '%Y-%m-%d').strftime('%d-%m-%Y')
    old_pricies = load_pricies_MongoDB(c_date1)
    if datetime.today().strftime('%Y-%m-%d') == c_date2:
        for i in compair_dict.keys():
            try:
                new_price = compair_dict[i]['coin_price']
            except:
                new_price = False
            try:
                old_price = old_pricies[i]
            except:
                old_price = False
            compair_dict[i].update({'custom_price_change_percentage': round(count_price_change(new_price, old_price), 2)})
    else:
        c_date2 = datetime.strptime(c_date2, '%Y-%m-%d').strftime('%d-%m-%Y')
        new_pricies = load_pricies_MongoDB(c_date2)
        for i in compair_dict.keys():
            try:
                new_price = new_pricies[i]
            except:
                new_price = False
            try:
                old_price = old_pricies[i]
            except:
                old_price = False
            compair_dict[i].update({'custom_price_change_percentage': round(count_price_change(new_price, old_price), 2)})
    return compair_dict

def twitter_followers_amount(compair_dict):
    communities_data = load_Mongo_communities('communities_data')
    for coin in compair_dict:
        try:
            compair_dict[coin]['twitter_followers_amount'] = communities_data[coin]['followers_amount']
            compair_dict[coin]['twitter_id'] = communities_data[coin]['twitter_id']
        except:
            compair_dict[coin]['twitter_followers_amount'] = '-'
            compair_dict[coin]['twitter_id'] = 0
    return compair_dict

# compare data. Function return { coin_name: {total_val = var, different_val = var} }
def comparison_dict(last_data, new_data):
    compare_data = {}
    for key in new_data:
        if not key in last_data.keys():
            try:
                compare_data[key] = {'total_val': int(new_data.get(key)), 'different_val': 0}
            except:
                if new_data.get(key) !=  'Error':
                    compare_data[key] = {'total_val': 0, 'different_val': 0}
        else:
            try:
                if int(last_data.get(key)) != 0:
                    #print(new_data.get(key), last_data.get(key), key)
                    compare_data[key] = {'total_val': int(new_data.get(key)), 'different_val': (int(new_data.get(key)) - int(last_data.get(key)))}
                else:
                    #print('------------------------------------------')
                    #print(new_data.get(key), last_data.get(key), key)
                    compare_data[key] = {'total_val': int(new_data.get(key)), 'different_val': 0}
            except:
                if new_data.get(key) !=  'Error':
                    compare_data[key] = {'total_val': int(new_data.get(key)), 'different_val': 0}
                else:
                    print('Coin is not defind on coingecko.com: ', key)
    return sort_dict(compare_data)

def sort_dict(compare_data):
    sort = {}
    for key, value in compare_data.items():
        sort[key] = value['total_val']
    sorted_={k: v for k, v in sorted(sort.items(),reverse=True, key=lambda item: item[1])}
    sort_compare_data = {}
    for key in sorted_:
        sort_compare_data[key] = compare_data.get(key)
    return sort_compare_data

# find all parse date from MongoDB and return list of data sorted by date [nowe_d, hour_ago_d, ..... , old_d]
def find_all_date_MongoDB():
    db = client.test
    data_db = db['list_ids']
    data_names = data_db.find_one()
    return sorted(data_names['ids'], reverse=True)

def count_f(all_parse_files, counter):
    text = all_parse_files[0]
    date_t = datetime.strptime(text, '%Y-%m-%d_%H:%M')
    if counter == 0:
        var_d = date_t - timedelta(hours=1)
    else:
        var_d = date_t - timedelta(counter)
    var_s = var_d.strftime('%Y-%m-%d_%H')
    for name in all_parse_files:
        if var_s in name:
            return name
    if counter != 0:
        var_s =var_d.strftime('%Y-%m-%d')
        for name in all_parse_files:
            if var_s in name:
                return name
    return 0

# select from all parse files 4 name of files [now_file, hour_ago_file, day_ago_file, week_ago_file]
def select_four_files(all_parse_files):
    now_f = all_parse_files[0]
    hour_ago_f = count_f(all_parse_files, 0)
    day_ago_f = count_f(all_parse_files, 1)
    week_ago_f = count_f(all_parse_files, 7)
    return [now_f, hour_ago_f, day_ago_f, week_ago_f]

def custom_interval(all_parse_files, c_date1, c_date2):
    """ input all_parse_files, c_date1, c_date2
        return dict diff custom_interval and interval date
    """
    for name in all_parse_files:
        if c_date1 in name:
            last_data = load_MongoDB(name)
            for name in all_parse_files:
                if c_date2 in name:
                    new_data = load_MongoDB(name)
                    return ['{}_{}'.format(c_date1.split('_')[0], c_date2.split('_')[0]), comparison_dict(last_data, new_data)]
            c_date2 = all_parse_files[0]
            new_data = load_MongoDB(c_date2)
            return ['{}_{}'.format(c_date1.split('_')[0], c_date2.split('_')[0]), comparison_dict(last_data, new_data)]
    c_date1 = all_parse_files[len(all_parse_files)-1]
    last_data = load_MongoDB(c_date1)
    for name in all_parse_files:
        if c_date2 in name:
            new_data = load_MongoDB(name)
            return ['{}_{}'.format(c_date1.split('_')[0], c_date2.split('_')[0]), comparison_dict(last_data, new_data)]
    c_date2 = all_parse_files[0]
    new_data = load_MongoDB(c_date2)
    return ['{}_{}'.format(c_date1.split('_')[0], c_date2.split('_')[0]), comparison_dict(last_data, new_data)]

def coin_release_date(compare_data):
    date_list = load_date_mongo()
    current_coins_list = list(compare_data.keys())
    for coin in date_list:
        if coin in current_coins_list:
            compare_data[coin]['date_release'] = date_list[coin]
    return compare_data


def coin_api_dev_data(compare_data):
    coins_data = load_api_dev_data_mongo()
    current_coins_list = list(compare_data.keys())
    for unit in coins_data:
        if unit['id'] in current_coins_list:
            compare_data[unit['id']].update(unit)
    return compare_data

def start_compare(c_date1=0, c_date2=0):
    """
       input custome date 1-from 2-to from user or default
       compare 3 base date (1 hour, 1 day, 1 week, custom_interval or default
       return dict {'url': coin_url, 'total_val': int, 'diff-1': int, 'diff-2': int, 'diff-3': int, 'diff custom'; int}
    """
    all_parse_files = find_all_date_MongoDB()
    selected_list_parse = select_four_files(all_parse_files)
    if c_date2 == 0 and c_date1 == 0:
        c_date1 = (datetime.today() - timedelta(days=14)).strftime('%Y-%m-%d')
        c_date2 = datetime.today().strftime('%Y-%m-%d')

    custom_list = custom_interval(all_parse_files, c_date1, c_date2)
    custom_inter = custom_list[0]
    custom_dict = custom_list[1]
    new_data = load_MongoDB(selected_list_parse[0])
    print(new_data)
    compair_dict = {}
    for key in new_data:
        compair_dict[key] = {'url': 'https://www.coingecko.com/en/coins/{}'.format(key), 'total_val': 0}
        if key in custom_dict:
            compair_dict[key].update({'diff_c': custom_dict.get(key)['different_val'], 'c_date': custom_inter})
        else:
            compair_dict[key].update({'diff_c': 'not data fo this interval', 'c_date': custom_inter})
    i = 1
    while i < len(selected_list_parse):
        if selected_list_parse[i] == 0:
            last_data = new_data
        else:
            last_data = load_MongoDB(selected_list_parse[i])
        var_dict = comparison_dict(last_data, new_data)

        for key in var_dict:
            compair_dict[key].update({
                                    'total_val': int(var_dict.get(key)['total_val']),
                                    'diff_{}'.format(i): var_dict.get(key)['different_val'],
                                    'price_change_percentage_24h': '-', 'market_cap': '-',
                                    'fully_diluted_valuation': '-', '24_hour_trading_volume': '-',
                                    'date_release': '-',
                                    'tw_f': '-',            # all twitter followers
                                    'tel_users_count': '-', # telegram users count
                                    'stars': '-',           # developer stars
                                    'subscribers': '-',     # developer subscribers coingecko
                                    't_i': '-',             # total issues
                                    'c_i': '-',             # closed issues
                                    'p_r_m': '-',           # pull_requests_merged
                                    'p_r_c': '-'            # pull_requests_contributors
                                    })
        i = i + 1
    detail_api = get_detail.get_coins()
    for i in detail_api:
        if i['coin_id'] in compair_dict.keys():
            compair_dict[i['coin_id']].update({
                                            'price_change_percentage_24h': i['price_change_percentage_24h'],
                                            'coin_price': i['coin_price'],
                                            'market_cap': i['market_cap'],
                                            'fully_diluted_valuation': i['fully_diluted_valuation'],
                                            '24_hour_trading_volume': i['24_hour_trading_volume']
                                            })

    compair_dict = price_compair(compair_dict, c_date1, c_date2)

    try:
        compair_dict = twitter_followers_amount(compair_dict)
    except:
        print('No followers_amount data')

    compair_dict = coin_release_date(compair_dict)
    compair_dict = coin_api_dev_data(compair_dict)

    return sort_dict(compair_dict)

    #--------------------------------
    #              MAIN
    #-------------------------------
