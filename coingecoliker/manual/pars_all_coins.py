import os
import requests
import json
import sys
import asyncio
import aiohttp
import datetime
from aiohttp import web
from bs4 import BeautifulSoup

COINS = {}

def load_coins_page(data):
    with open(data, 'r') as f:
        links_list = json.load(f)
    return links_list


async def get_json(client, url):
    print('Get url for parse', url)
    coin = {}
    async with client.get(url) as response:
        assert response.status == 200
        data = await response.text()
        plt = data.split('<i data-target="favorites.emptyStar"')[1].split('</i>')[1].split('</span>')[0]
        try:
            plt = plt.split('people')[0]
            plt = ''.join(plt.split(','))
            plt = int(plt)
        except:
            plt = data.split('<title>')[1].split('</title>')[0]
        coin_name = url.split('/')[-1]
        coin[coin_name] = plt
        COINS[coin_name] = plt
        print(coin)
    return coin

def save_json(coin):
    print('Star save result to json file')
    with open('coingecko_table.json', 'w') as f:
              json.dump(coin, f, indent=4)

async def main(data):
    print(datetime.datetime.now().strftime("%A, %B %d, %I:%M %p"))
    print('---------------------------')
    loop = asyncio.get_running_loop()
    links = load_coins_page(data)
    async with aiohttp.ClientSession(loop=loop) as client:
        links
        await asyncio.wait([get_json(client, url) for url in links])
        coin = COINS
        save_json(coin)
        print('Save coingecko_table.json complite')
    return web.Response(text='Done')


if __name__ == '__main__':
    data = 'coins_list.json'
    b = asyncio.run(main(data))
    print("End", b)
    #web.run_app(app)
