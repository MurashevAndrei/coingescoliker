import get_links_with_API
from pymongo import MongoClient
import requests
import asyncio
import aiohttp
from datetime import datetime
#from selenium import webdriver
from time import sleep
#from selenium.webdriver.common.keys import Keys
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
import multiprocessing
from time import time

from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector



import random

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")

COINS = {}
ERR_5 = []
ERR_4 = []

def run_parser():
        data = get_links_with_API.get_links_for_parse()
        list = {'urls':data}
        print(list)
        return list

def save_mongo(data):
    db = client.test
    pars_data = db['coins_list']
    pars_data.insert_one(data)

def load_mongo():
    db = client.test
    pars_data = db['coins_list']
    data = pars_data.find_one()
    return data.get('urls')

def load_url(data):
    for url in data:
        print(url)
        r = requests.get(url)
        print(r.status_code)

def load(data):
    #PROXY = '/127.0.0.1:9150'

    #chrome_options = Options()
    chrome_options= webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    #chrome_options.add_argument('--proxy=%s' % PROXY)
    #d = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)
    d = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)
    for url in data:
        #proxy_auth = str(random.randint(10000, 2147483647)) + ':' + 'passwrd'
        #p = {'https': 'socks5//{}@localhost:9050'.format(proxy_auth)}
        proxies = {'https': 'socks5//{}@localhost:9050'.format(proxy_auth)}
        #chrome_options.add_argument('--proxy-server=%s' % p)
        #d = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)
        d.get(url)
        #r = requests.get(url, proxies=proxies)
        #print(r.status_code)
        print(d.title)

async def get_json(client, url):
    coin = {}
    plt = ''
    #url = 'https://api.ipify.org'
    async with client.get(url) as response:
        print('YAAAAH!')
        stat = response.status
        print(stat, ' for url ', url)
        if stat == 200:
            if url in ERR_5:
                ERR_5.remove(url)
        if stat != 200:
            if stat == 500 or stat == 503 or stat == 504:
                ERR_5.append(url)
            else:
                ERR_4.append((url, stat))
        data = await response.text()
        plt = 'Error'
        try:
            plt = data.split('<i data-target="favorites.emptyStar"')[1].split('</i>')[1].split('</span>')[0]
            plt = plt.split('people')[0]
            plt = ''.join(plt.split(','))
            plt = int(plt)
        except:
            print('Error ', url)
        coin_name = url.split('/')[-1]
        coin[coin_name] = plt
        COINS[coin_name] = plt

async def run_p(data):
    print(datetime.now().strftime("%A, %B %d, %I:%M %p"))
    print('---------------------------')
    loop = asyncio.get_running_loop()
    print('---------')
    headers = { 'User-Agent': UserAgent().random }


    with Controller.from_port(port = 9051) as c:
        c.authenticate()
        c.signal(Signal.NEWNYM)
        proxy = 'socks5://andrei:12wsaq@127.0.0.1:9050'
        print(proxy)
        connector = ProxyConnector.from_url(proxy)

        async with aiohttp.ClientSession(loop=loop, connector=connector, headers=headers) as client:

            links = data
            links = links[:5]
            await asyncio.wait([get_json(client, url) for url in links])
#return web.Response(text='Done')

def heandler(url):
    headers = { 'User-Agent': UserAgent().random }
    with Controller.from_port(port = 9051) as c:
        c.authenticate()
        c.signal(Signal.NEWNYM)
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    try:
        r = requests.get(url, proxies=proxies, headers=headers, timeout=4)
    except:
        ERR_4.append(url)

data = load_mongo()
links = data
t0 = time()
print(multiprocessing.cpu_count())
#b = asyncio.run(run_p(data))
#load_url(data)
#load(data)
with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
    process.map(heandler, links)
print(ERR_4)
print((time() - t0))
