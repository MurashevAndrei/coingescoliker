import os
import requests
import asyncio
import aiohttp
from aiohttp import web
from datetime import datetime
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient

MAIN_PAGE = 'https://www.coingecko.com/en/exchanges/'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")
PAIR_WX = {}
ALL_EX_PAIR = []
ERR = {}
ERR_L = []
ERR5 =[]
ERR_EXCH = []

def save_mongo(data, name):
    db = client.markets
    markets_db = db[name]
    markets_db.delete_many({})
    if name == 'list_exchanges':
        markets_db.insert_one(data)
    else:
        markets_db.insert_many(data)

def save_json(data):
    date_t = datetime.utcnow()
    date = date_t.strftime("%Y-%m-%d_%H:%M")
    file_name = ('%s.json' % date)
    path = os.path.join(BASE_DIR, 'coingecko', 'static', 'market_parsers', file_name)
    with open(path, 'w') as f:
              json.dump(data, f, indent=4)

def api_exchanges():
    headers = {
        'accept': 'application/json',
    }
    response = requests.get('https://api.coingecko.com/api/v3/exchanges/list', headers=headers)
    return response.json()

def add_links(data):
    data_dict = {}
    for i in data:
        i['url'] = MAIN_PAGE + i['id']
        data_dict[i['id']] = {'url': MAIN_PAGE + i['id']}
    return data_dict

async def get_html(client, url):
    async with client.get(url) as response:
        resp = response.status
        if resp == 200:
            if url in ERR5:
                ERR5.remove(url)
        if resp != 200:
            if resp == 404:
                ERR[url.split('/')[-1]] = response.status
            else:
                ERR5.append(url)
            return web.Response(text='Done')
        r = await response.text()
        try:
            soup = BeautifulSoup(r, 'lxml')
            el_div = soup.findAll("div", {"class": "px-4 text-center py-2 py-lg-0"})
            PAIR_WX[url.split('/')[-1]] = int(el_div[-1].div.next)
        except:
            print('Error')
    return web.Response(text='Done')

async def get_html2(client, url):
    async with client.get(url) as response:
        ex_name = url.split('/show_more')[0].split('/')[-1]
        resp = response.status
        if resp == 200:
            if url in ERR_L:
                ERR_L.remove(url)
        if resp != 200:
             ERR_L.append(url)
             return web.Response(text='Done')
        r = await response.text()
        try:
            soup = BeautifulSoup(r, 'lxml')
            el_div = soup.findAll("tr")
            for tr in el_div:
                var_dict = {}
                var_dict['exchange'] = ex_name
                td = tr.findAll('td')
                var_dict['coin_name'] = td[1].text.strip()
                var_dict['pair'] = td[3].text.strip()
                var_dict['price'] = td[4].text.strip().split('$')[1].split('\n\n')[0]
                if var_dict['price'] != '-' and var_dict['price'] != '':
                    var_dict['price'] = float(var_dict['price'].replace(',', ''))
                var_dict['spread'] = td[5].text.strip()
                if var_dict['spread'] != '-' and var_dict['spread'] != '':
                    var_dict['spread'] = float(var_dict['spread'].replace('%', ''))
                var_dict['depth+per2'] = td[6].text.strip()
                if var_dict['depth+per2'] != '-' and var_dict['depth+per2'] != '':
                    var_dict['depth+per2'] = float(var_dict['depth+per2'].replace('$', '').replace(',', ''))
                var_dict['depth-per2'] = td[7].text.strip()
                if var_dict['depth-per2'] != '-' and var_dict['depth-per2'] != '':
                    var_dict['depth-per2'] = float(var_dict['depth-per2'].replace('$', '').replace(',', ''))
                if ',' in td[8].text:
                    var_dict['volume_ex'] = float(td[8].text.strip().split('$')[1].split('\n')[0].replace(',',''))
                else:
                    var_dict['volume_ex'] = float(td[8].text.strip().split('$')[1].split('\n')[0])
                if td[2].text.strip() == '':
                    var_dict['total_volume'] = 0
                elif ',' in td[2].text:
                    var_dict['total_volume'] = round(float(td[2].text.strip().split('$')[1].replace(',','')), 2)
                else:
                    var_dict['total_volume'] = round(float(td[2].text.strip().split('$')[1]), 2)
                if var_dict['total_volume'] != 0:
                    var_dict['volume_per'] = round(var_dict['volume_ex']/var_dict['total_volume']*100, 2)
                else:
                    var_dict['volume_per'] = 0
                ALL_EX_PAIR.append(var_dict)
                if url in ERR_EXCH:
                    ERR_EXCH.remove(url)
        except:
            r_var = str(response.url)
            r_var = r_var + '/' + url.split('/')[-1]
            ERR_EXCH.append(r_var)
    return web.Response(text='Done')

def create_links(val, exch_name):
    i = 0
    if val != 0:
        pages = val // 100
        data_links = []
        while i != (pages+1):
            data_links.append('{}{}/show_more_tickers?page={}&per_page=100&verified_ticker=true'.format(MAIN_PAGE, exch_name, i))
            i = i + 1
        return data_links
    return []

def get_total_coins(exch):
    """Get dict of all exchanges and return all coins for each exchanges. Use iohttp"""
    urls = []
    for ex in exch:
        urls.append(exch[ex]['url'])
    page = asyncio.run(run_asy_parse(urls, 1))

async def run_asy_parse(urls, var):
    """Write to PAIR_WX how many pair on the exchange"""
    loop = asyncio.get_running_loop()
    if var == 1:
        async with aiohttp.ClientSession(loop=loop) as client:
            await asyncio.wait([get_html(client, url) for url in urls])
        return web.Response(text='Done')
    elif var ==2:
        async with aiohttp.ClientSession(loop=loop) as client:
            await asyncio.wait([get_html2(client, url) for url in urls])
        return web.Response(text='Done')


def exch_data(urls):
    data = asyncio.run(run_asy_parse(urls, 2))

def get_urls_list(pair):
    urls = []
    for key in pair:
        urls.extend(create_links(pair.get(key), key))
    return urls

def check_500(var):
    i = 0
    if var == 1:
        while len(ERR5) > 0 and i < 5:
            data = asyncio.run(run_asy_parse(ERR5, 1))
            i = i + 1
    if var == 2:
        while len(ERR_L) > 0 and i < 5:
            data = asyncio.run(run_asy_parse(ERR_L, 2))
            i = i + 1

def check_ERR_EXCH():
    if len(ERR_EXCH) > 0:
        data = asyncio.run(run_asy_parse(ERR_EXCH, 2))

def main():
    exch_dict = add_links(api_exchanges())
    get_total_coins(exch_dict)
    check_500(1)
    var = get_urls_list(PAIR_WX)
    exch_data(var)
    check_500(2)
    check_ERR_EXCH()
    check_500(2)
    save_mongo(ALL_EX_PAIR, 'markets_data')
    save_mongo(exch_dict, 'list_exchanges')
    print(ERR, ERR5, ERR_L, ERR_EXCH)
    print(len(ERR_EXCH))
"""
    exch_data(['https://www.coingecko.com/en/exchanges/bitso/show_more_tickers?page=0&per_page=100&verified_ticker=true'])
    print(ALL_EX_PAIR)
    """

if __name__ == '__main__':
    main()
