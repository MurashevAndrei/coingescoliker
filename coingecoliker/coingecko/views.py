from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import Coin
from .settings import BASE_DIR, MONGO_DB
import json
from datetime import datetime
import os
from pymongo import MongoClient
import coingecko.comparison_by_date as compare
import coingecko.parse_coins_detail as coin_detail
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect

client = MongoClient(MONGO_DB)

@csrf_protect
def index(request):
    """ Load all coins by custome date and by all exchanges or custom exchanges(coin_wm)"""
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        list_twitter_accounts = load_twitters_MongoDB()
        list_cat = load_cat_list_MongoDB()
        list_markets = load_MongoDB()
        dfrom, dto = get_date(request)
        if 'multi' in request.POST:
            coin_wm, answer = get_custom_exchanges(request)
            coin_tw, answer_twitter = get_custom_twitters(request)
            coin_cat, answer_cat = get_custom_cats(request)
        #    print(coin_cat)
        else:
            coin_wm = False
            coin_tw = False
            coin_cat = False
        data = compare.start_compare(dfrom, dto)
        try:
            dfrom, dto = date_formating(data)
        except Exception as e:
            print(e)
            dfrom, dto = "00", "00"

        if coin_wm:
            #print(coin_wm, "PRINT COIN WM")
            coins = load_coins_by_custom_date(data, coin_wm)
        elif isinstance(coin_wm, list):
            if len(coin_wm) == 0:
                coins = []
        else:
            coins = load_all_coins(data)
        if coin_tw != False:
            coins = twitter_ids_filter(coins, coin_tw)
        if coin_cat != False:
            coins = cat_ids_filter(coins, coin_cat)

        return render(request, 'sort.html', locals())


@csrf_protect
def markets(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        data = load_Mongo('markets_data')
        data = data
        #print(len(data))
        data = data
        return render(request, 'markets.html', locals())

@csrf_protect
def coins(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        #data = load_Mongo('coins_detail')
        data = []
        data = coin_detail.get_coins()
        print(len(data))
        return render(request, 'coins.html', locals())

@csrf_protect
def setup(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    alert_sittings = load_mongo_alert_settings()
    if 'setup' in request.POST:
        alert_sittings = create_alert_setup(request.POST)
    return render(request, 'setup.html', locals())


@csrf_protect
def grafiks(request, coin_name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        db = client.markets
        coll= db['grafiks']
        data_coll = coll.find_one()
        #print(data_coll.keys())


        for coin in data_coll['data']:
            if coin == coin_name:
                data = data_coll['data'][coin]
                coin_name = coin_name
                #print(data)
        date_now = '01.12.2020'


    return render(request, 'grafiks.html', locals())


@csrf_protect
def gr(request, coin_name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        coin = {}
        data = load_graf(coin_name)
        coin['coin'] = coin_name
        dates = json.dumps(['16 aug'])

        return render(request, 'gr.html', locals())


@csrf_protect
def login_page(request):
    if request.POST:
        username= request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                print("User is valid, active and authenticated")
                login(request, user)
                return HttpResponseRedirect('/main')
            else:
                print("The password is valid, but the account has been disabled!")
        else:
            text = ("The username and password were incorrect.")
            return render(request, 'login.html', locals())
    return render(request, 'login.html', locals())


@csrf_protect
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def load_graf(coin_name):
    db = client.markets
    coll= db['grafiks']
    data_coll = coll.find_one()
    for c in data_coll['data']:
        if c == coin_name:
            data = data_coll['data'][c]
            data = data[:20]
            return data


def load_MongoDB():
    list_markets = []
    db = client.markets
    data_ = db['list_exchanges']
    data_dict = data_.find()
    for a in data_dict:
        for key in a.keys():
            if key != '_id':
                list_markets.append(key)
    return list_markets

def load_twitters_MongoDB(task=False):
    list_twitter_accounts = []
    db = client.test.twitter_followings
    data_ = db.find_one({'_id': 'G_followings'})
    data_dict = data_.get('data')
    if task:
        return data_dict
    for i in data_dict:
        try:
            list_twitter_accounts.append((i['name'], i['username']))
        except:
            'no data'
    return list_twitter_accounts

def load_cat_list_MongoDB(task=False):
    list_twitter_accounts = []
    db = client.test.categories
    data_ = db.find_one()
    list_cat = []
    if task:
        return data_['data']
    for cat in data_['data']:
        list_cat.append(cat['name'])
    return list_cat

def get_date(request):
    if 'date' in request.POST:
        dfrom = request.POST['from']
        dto = request.POST['to']
    else:
        dfrom = 0
        dto = 0
    return (dfrom, dto)

def date_formating(data):
    #print(data.get('bitcoin-one'))
    for i in data:
        try:
            dfrom = data.get(i)['c_date'].split('_')[0]
            dto = data.get(i)['c_date'].split('_')[1]
            return (dfrom, dto)
        except:
            print("no data dfrom dto in date_formating")


def get_custom_exchanges(request):
    coin_wm = []
    exchanges = request.POST.getlist('exchange[]')
    if len(exchanges) == 0:
        print('Ecxhange False')
        return False, ''
    answer = 'Coins in'
    markets = load_Mongo('markets_data')
    for ex in exchanges:
        answer = answer + ' ' + ex
        #markets = load_Mongo('markets_data')
        if coin_wm:
            coins_in_market = []
            for market in markets:
                if ex == market['exchange']:
                    coins_in_market.append(market['coin_name'])
            coin_wm = list(set(coin_wm) & set(coins_in_market))
            if len(coin_wm) == 0:
                break
        else:
            for market in markets:
                if ex == market['exchange']:
                    if market['coin_name'] not in coin_wm:
                        coin_wm.append(market['coin_name'])
    return coin_wm, answer

def get_custom_twitters(request):
    twitters_custom = request.POST.getlist('twitter[]')
    if len(twitters_custom) == 0:
        return False, ''
    answer_twitter = 'Coins for twitter accounts:'
    twitter_dict = load_twitters_MongoDB(True)
    lists_followings_list = []
    for twitter_username in twitters_custom:
        try:
            answer_twitter = answer_twitter + f' {twitter_username}' # tuple
        except:
            'no data'
        for account in twitter_dict:
            try:
                if account['username'] == twitter_username: # tuple
                    lists_followings_list.append(account['followings_list'])
            except:
                'no data'
    coin_tw_ids = []
    try:
        for i, j in enumerate(lists_followings_list):
            if i == 0:
                coin_tw_ids = j
                continue
            coin_tw_ids = list(set(j) & set(coin_tw_ids))
        return coin_tw_ids, answer_twitter
    except:
        return [], answer_twitter

def get_custom_cats(request):
    cats_custom = request.POST.getlist('cat[]')
    if len(cats_custom) == 0:
        return False, ''
    answer_cat = 'Coins for categories:'
    cat_list = load_cat_list_MongoDB(True)
    coins_list = []
    for cat_name in cats_custom:
        try:
            answer_cat = answer_cat + f' {cat_name}' # tuple
        except:
            'no data'
        for categorie in cat_list:
            try:
                if categorie['name'] == cat_name: # tuple
                   if len(coins_list) == 0:
                       coins_list.extend(categorie['coins'])
                   else:
                       coins_list = list(set(coins_list) & set(categorie['coins']))
                       if len(coins_list) == 0:
                           return coins_list, answer_cat
            except:
                'no data'
    return coins_list, answer_cat

def twitter_ids_filter(coins, coin_tw):
    coins_result = []
    for coin in coins:
        if coin['twitter_id'] in coin_tw:
            coins_result.append(coin)
    return coins_result

def cat_ids_filter(coins, coin_cat):
    coins_result = {}
    for coin, value in coins.items():
        if coin in coin_cat: #TO DO
            coins_result.update({coin: value})
    return coins_result



def load_coins_by_custom_date(data, coin_wm):
    coins = {}
    for coin in coin_wm:
        coin = coin.lower()
        coin1 = coin.replace(' ', '-')
        if not data.get(coin1):
            coin1 = coin.replace(' ', '')
        if data.get(coin1):
            try:
                coin_dict = {'coin' : coin1}
                for key, value in data.get(coin1).items():
                    coin_dict.update({key : value})
                coins.update({coin1 : coin_dict})
            except:
                print('No data', coin1)
    return coins


def load_all_coins(data):
    return data
    #return coins


def create_alert_setup(request):
    alert_sittings = {}
    #print(request)
    diff_likes = request['likes_change24']
    status_likes = request['status_likes_change24']
    market_cap = request['market_cap']
    status_market = request['status_market_cap']
    tfollowers_amount = request['tfollowers_amount']
    status_twitter = request['status_tfollowers_amount']
    price_change_percentage_24h = request['price_change_percentage_24h']
    statu_price = request['status_price_change_percentage_24h']
    date_release = request['date_release']
    satus_date = request['status_date_release']
    volume_24 = request['24_hour_trading_volume']
    status_volume_24 = request['status_24_hour_trading_volume']
    if diff_likes != '':
        alert_sittings['diff_likes'] = [status_likes, int(diff_likes)]
    if market_cap != '':
        alert_sittings['market_cap'] = [status_market, int(market_cap)]
    if tfollowers_amount != '':
        alert_sittings['tfollowers_amount'] = [status_twitter, int(tfollowers_amount)]
    if price_change_percentage_24h != '':
        alert_sittings['price_change_percentage_24h'] = [statu_price, float(price_change_percentage_24h)]
    if date_release != '':
        alert_sittings['date_release'] = [satus_date, str(date_release)]
    if volume_24 != '':
        alert_sittings['24_hour_trading_volume'] = [status_volume_24, int(volume_24)]
    #print(alert_sittings)
    if len(alert_sittings) > 0:
        save_mongo_alert_settings(alert_sittings)
    return alert_sittings

def save_mongo_alert_settings(data):
    data = {"data": data}
    db = client.markets.alert_sittings
    try:
        db.delete_many({})
    except:
        print('No date data')
    db.insert_one(data)
    return

def load_mongo_alert_settings():
    db = client.markets.alert_sittings
    alert_sittings = db.find_one()['data']
    return alert_sittings



def load_Mongo(name):
    datas = []
    db = client.markets
    db = db[name]
    data = db.find()
    for d in data:
        d.pop('_id')
        datas.append(d)
    return datas
