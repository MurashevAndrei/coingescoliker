from get_links_with_API import get_dict_coins_id as get_ids
from parser_aiohttp import get_proxies_list
from parser_twitter_aiohttp import load_Mongo_communities, save_mongo_communities, add_count_follower
import asyncio
import aiohttp
import sys
from pymongo import MongoClient
import requests
from datetime import datetime, timedelta
from time import sleep
from fake_useragent import UserAgent
import multiprocessing
from time import time, sleep
import json
import random

client = MongoClient("mongodb+srv://coingeckoDB:12wsaq@coingecko.16oet.mongodb.net/<dbname>?retryWrites=true&w=majority")



#-------------------------------------------------------------------------------
#-----------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    t0 = time()

    communities_dict = load_Mongo_communities('communities_data')
    print(time() - t0)
