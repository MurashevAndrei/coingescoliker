import requests
from fake_useragent import UserAgent
import random
import multiprocessing


session = requests.session()
session.proxies = {}

#r = session.get('http://httpbin.org/ip')
#print(r.text)

#or i in range(2):
#    session = requests.session()
#    session.proxies = {}
#    session.proxies['http'] = 'socks5h://localhost:9050'
#    session.proxies['https'] = 'socks5h://localhost:9050'

#    r = session.get('http://httpbin.org/ip')
#    print(r.text)
def heandler(links):
    print(links)
    headers = { 'User-Agent': UserAgent().random }
    url = 'http://httpbin.org/ip'
    proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050'
    }
    r = requests.get(url, proxies=proxies, headers=headers)
    print(r.text)
    return r.text

links = list(range(200))
print(type(links))
print(multiprocessing.cpu_count())
with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
    result_data = process.map(heandler, links)
print(result_data)
