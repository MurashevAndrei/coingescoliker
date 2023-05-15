import json
import os
import locale
from datetime import datetime, timedelta, time
import datetime as DT
from pymongo import MongoClient
from pushbullet import Pushbullet

api_key = 'o.we360y2PXMdPhBuO1gsptVY2ywSf3vuc'
pb = Pushbullet(api_key)


client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")


def load_MongoDB(data_name):
    db = client.test.each_hour
    data_ = db.find_one({'_id': data_name})
    data_dict = data_.get('data')
    return data_dict

def load_detail_MongoDB():
    db = client.markets.coins_detail
    data = db.find()
    list_data = []
    for i in data:
        list_data.append(i)
    return list_data

def load_date_mongo():
    db = client.markets.date_release
    return db.find_one()['date']

def load_mongo_alert_settings():
    db = client.markets.alert_sittings
    alert_sittings = db.find_one()['data']
    return alert_sittings

def find_all_date_MongoDB():
    db = client.test
    data_db = db['list_ids']
    data_names = data_db.find_one()
    return sorted(data_names['ids'], reverse=True)

def load_Mongo_communities(data_name):
    db = client.test.communities_data
    data_ = db.find_one({'_id': data_name})
    data_dict = data_.get('data')
    return data_dict

# compare data. Function return { coin_name: {total_val = var, different_val = var} }
def compare(last_data, new_data):
    compare_data = {}
    for key in new_data:
        if not key in last_data.keys():
            try:
                compare_data[key] = {'total_val': int(new_data.get(key)), 'diff_likes_24h': 0}
            except:
                if new_data.get(key) !=  'Error':
                    compare_data[key] = {'total_val': 0, 'diff_likes_24h': 0}
        else:
            try:
                if int(last_data.get(key)) != 0:
                    compare_data[key] = {'total_val': int(new_data.get(key)), 'diff_likes_24h': (int(new_data.get(key)) - int(last_data.get(key)))}
                else:
                    compare_data[key] = {'total_val': int(new_data.get(key)), 'diff_likes_24h': 0}
            except:
                if new_data.get(key) !=  'Error':
                    compare_data[key] = {'total_val': int(new_data.get(key)), 'diff_likes_24h': 0}
                else:
                    print('Coin is not defind on coingecko.com: ', key)
    return sort_dict(compare_data)

def get_two_namefiles():
    """Load ids list each hours. Return 2 name files last and day ago"""
    all_parse_files = find_all_date_MongoDB()
    first_name = all_parse_files[0]
    first_file = datetime.strptime(first_name, '%Y-%m-%d_%H:%M')
    second_name = (first_file - timedelta(days=1)).strftime('%Y-%m-%d_%H')
    for i in all_parse_files:
        if second_name in i:
            return first_name, i
    return False, False


def sort_dict(compare_data):
    sort = {}
    for key, value in compare_data.items():
        sort[key] = value['total_val']
    sorted_={k: v for k, v in sorted(sort.items(),reverse=True, key=lambda item: item[1])}
    sort_compare_data = {}
    for key in sorted_:
        sort_compare_data[key] = compare_data.get(key)
    return sort_compare_data

def get_market_cap():
    print('Start load')
    data_detail = load_detail_MongoDB()
    return data_detail


def get_coins_detail(compare_dict):
    detail_api = get_market_cap()
    for i in detail_api:
        if i['id'] in compare_dict.keys():
            compare_dict[i['id']].update({
                                        'market_cap': i['market_cap'],
                                        'price_change_percentage_24h': i['price_change_percentage_24h'],
                                        'fully_diluted_valuation': i['fully_diluted_valuation'],
                                        '24_hour_trading_volume': i['total_volume']})
    date_list = load_date_mongo()
    current_coins_list = list(compare_dict.keys())
    for coin in date_list:
        if coin in current_coins_list:
            compare_dict[coin]['date_release'] = date_list[coin]
    return compare_dict

def check_difference_like(diff_likes, compare_dict):
    if diff_likes == 0:
        return compare_dict
    result_dict = {}
    if diff_likes[0] == 'more':
        for coin in compare_dict:
            if compare_dict[coin]['diff_likes_24h'] > diff_likes[1]:
                result_dict[coin] = compare_dict[coin]
    elif diff_likes[0] == 'less':
        for coin in compare_dict:
            if compare_dict[coin]['diff_likes_24h'] < diff_likes[1]:
                result_dict[coin] = compare_dict[coin]
    print('Check dif likes after ', len(compare_dict), 'before', len(result_dict))
    return result_dict

def check_market_cap(market_cap, compare_dict):
    if market_cap == 0:
        return compare_dict
    result_dict = {}
    if market_cap[0] == 'more':
        for coin in compare_dict:
            try:
                if compare_dict[coin]['market_cap'] > market_cap[1]:
                    result_dict[coin] = compare_dict[coin]
            except:
                compare_dict[coin]['market_cap'] = 0
    elif market_cap[0] == 'less':
        for coin in compare_dict:
            try:
                if compare_dict[coin]['market_cap'] < market_cap[1]:
                    result_dict[coin] = compare_dict[coin]
            except:
                compare_dict[coin]['market_cap'] = 0
    print('Check market_cap after ', len(compare_dict), 'before', len(result_dict))
    return result_dict

def check_twitters_followers(twitter_followers, compare_dict):
    if twitter_followers == 0:
        return compare_dict
    result_dict = {}
    communities_data = load_Mongo_communities('communities_data')
    if twitter_followers[0] == 'more':
        for coin in compare_dict:
            try:
                if communities_data[coin]['followers_amount'] > twitter_followers[1]:
                    compare_dict[coin]['tfollowers_amount'] = communities_data[coin]['followers_amount']
                    result_dict[coin] = compare_dict[coin]
            except:
                'no data'
    elif twitter_followers[0] == 'less':
        for coin in compare_dict:
            try:
                if communities_data[coin]['followers_amount'] < twitter_followers[1]:
                    compare_dict[coin]['tfollowers_amount'] = communities_data[coin]['followers_amount']
                    result_dict[coin] = compare_dict[coin]
            except:
                'no data'
    print('Check tfollowers_amount after ', len(compare_dict), 'before', len(result_dict))
    return result_dict

def check_24_price_change(price_change, compare_dict):
    if price_change == 0:
        return compare_dict
    result_dict = {}
    if price_change[0] == 'more':
            for coin in compare_dict:
                try:
                    if compare_dict[coin]['price_change_percentage_24h'] > price_change[1]:
                        result_dict[coin] = compare_dict[coin]
                except:
                    compare_dict[coin]['price_change_percentage_24h'] = 0
    elif price_change[0] == 'less':
        for coin in compare_dict:
            try:
                if compare_dict[coin]['price_change_percentage_24h'] < price_change[1]:
                    result_dict[coin] = compare_dict[coin]
            except:
                compare_dict[coin]['price_change_percentage_24h'] = 0
    print('Check price_change ', len(compare_dict), 'before', len(result_dict))
    return result_dict

def format_date(date):
    try:
        if issubclass(type(date), datetime):
            date = date.strftime("%Y-%m-%d")
        else:
            date = datetime.strptime(date, "%Y-%m-%d")
    except:
        date = False
    return date

def check_release_date(date_release, compare_dict):
    if date_release == 0:
        return compare_dict
    date_release[1] = format_date(date_release[1])
    result_dict = {}
    if date_release[0] == 'more':
            for coin in compare_dict:
                try:
                    if compare_dict[coin]['date_release'] > format_date(date_release[1]):
                        result_dict[coin] = compare_dict[coin]
                except:
                    compare_dict[coin]['date_release'] = 0
    elif date_release[0] == 'less':
        for coin in compare_dict:
            try:
                if compare_dict[coin]['date_release'] < format_date(date_release[1]):
                    result_dict[coin] = compare_dict[coin]
            except:
                compare_dict[coin]['date_release'] = 0
    print('Check date_release ', len(compare_dict), 'before', len(result_dict))
    return result_dict

def check_24_trading_volume(volume24, compare_dict):
    if volume24 == 0:
        return compare_dict
    result_dict = {}
    if volume24[0] == 'more':
        for coin in compare_dict:
            try:
                if compare_dict[coin]['24_hour_trading_volume'] > volume24[1]:
                    result_dict[coin] = compare_dict[coin]
            except:
                compare_dict[coin]['24_hour_trading_volume'] = 0
    elif volume24[0] == 'less':
        for coin in compare_dict:
            try:
                if compare_dict[coin]['24_hour_trading_volume'] < volume24[1]:
                    result_dict[coin] = compare_dict[coin]
            except:
                compare_dict[coin]['24_hour_trading_volume'] = 0
    print('Check 24_hour_trading_volume', len(compare_dict), 'before', len(result_dict))
    return result_dict

def create_answer(coin_name, values, answer_list):
    answer = f"{coin_name} https://www.coingecko.com/en/coins/{coin_name} "
    for val in answer_list:
        answer += f", {val} {values[val]}"
    return answer

def push_alert(compare_dict, answer_list):
    msg = []
    for i in compare_dict:
        am = create_answer(i, compare_dict[i], answer_list)
        msg.append(am)
        print(am)
        send_push(am)
    return

def send_push(msg):
    print(pb.chats)
    nastya = pb.chats[1]
    garry = pb.chats[0]
    push = nastya.push_note('Coin alert', msg)
    push = garry.push_note('Coin alert', msg)

def checker(compare_dict):
    #TODO LOAD ALERT_SETINGS FROM MONGO
    alert_settings = load_mongo_alert_settings()

    answer_list = []
    for set in alert_settings:
        if set == 'diff_likes':
            compare_dict = check_difference_like(alert_settings[set], compare_dict)
            answer_list.append('diff_likes_24h')
        if set == 'market_cap':
            compare_dict = check_market_cap(alert_settings[set], compare_dict)
            answer_list.append('market_cap')
        if set == 'tfollowers_amount':
            compare_dict = check_twitters_followers(alert_settings[set], compare_dict)
            answer_list.append('tfollowers_amount')
        if set == 'price_change_percentage_24h':
            compare_dict = check_24_price_change(alert_settings[set], compare_dict)
            answer_list.append('price_change_percentage_24h')
        if set == 'date_release':
            compare_dict = check_release_date(alert_settings[set], compare_dict)
            answer_list.append('date_release')
        if set == '24_hour_trading_volume':
            compare_dict = check_24_trading_volume(alert_settings[set], compare_dict)
            answer_list.append('24_hour_trading_volume')
    return compare_dict, answer_list



def main_notification():
    current_filename, day_ago_filename = get_two_namefiles()
    current_data = load_MongoDB(current_filename)
    day_ago_data = load_MongoDB(day_ago_filename)
    compare_dict = compare(day_ago_data, current_data)
    compare_dict = get_coins_detail(compare_dict)
    #TODO IF NOT DATA LAST HOUR SEND ALERT ERROR

    alert_dict, answer_list = checker(compare_dict)
    push_alert(alert_dict, answer_list)


#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main_notification()
