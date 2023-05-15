import os
import requests
import json
import sys
import asyncio
import aiohttp
import datetime
from aiohttp import web
from bs4 import BeautifulSoup
import get_links_with_API

COINS = {}

def load_coins_page(data):
    with open(data, 'r') as f:
        links_list = json.load(f)
    return links_list


async def get_json(client, url):
    #print('get json first', url, client)
    coin = {}
    plt = ''
    async with client.get(url) as response:
        #print(response.status, ' for url - ', url)
        if response.status != 200:
            print('Status ', response.status, ' for ', url, 'is not 200')
        data = await response.text()
        plt = 'Error'
        try:
            plt = data.split('<i data-target="favorites.emptyStar"')[1].split('</i>')[1].split('</span>')[0]
            plt = plt.split('people')[0]
            plt = ''.join(plt.split(','))
            plt = int(plt)
        except:
            print('Error ', url)
            plt = 'Error'
        coin_name = url.split('/')[-1]
        coin[coin_name] = plt
        COINS[coin_name] = plt
    
def save_json(coin):
    print('Start geting data save to json')
    with open('coingecko_table_new.json', 'w') as f:
              json.dump(coin, f, indent=4)

async def main(data):
    print(datetime.datetime.now().strftime("%A, %B %d, %I:%M %p"))
    print('---------------------------')
    loop = asyncio.get_running_loop()
    #links = load_coins_page(data)
    async with aiohttp.ClientSession(loop=loop) as client:
        links = data
        print('downlod to parse ', len(links))
        await asyncio.wait([get_json(client, url) for url in links])
        print('Parse is done')
        coin = COINS
        save_json(coin)
        print('Was done ', len(COINS.keys()), ' coins from ', len(links), ' in coingecko')

    return web.Response(text='Done')

if __name__ == '__main__':
    data = get_links_with_API.get_links_for_parse()
    b = asyncio.run(main(data))
    print("End", b)
