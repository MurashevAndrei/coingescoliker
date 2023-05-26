import requests
from fake_useragent import UserAgent
import multiprocessing
import random
from stem import Signal
from stem.control import Controller

def heandler(var):
    headers = { 'User-Agent': UserAgent().random }
    url_p = 'https://api.ipify.org'
    url = 'https://www.coingecko.com/en'
    with Controller.from_port(port = 9051) as c:
            c.authenticate()
            c.signal(Signal.NEWNYM)
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    b = requests.get(url_p, proxies=proxies, headers=headers)
    r = requests.get(url, proxies=proxies, headers=headers, timeout=10)
    print(r.status_code, '  ', var, ' ip ', b.text)
    return r.status_code

links = list(range(200))
with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
    result_data = process.map(heandler, links)
print(result_data)

#webbrowser.open('https://vk.com', new=2)
#webbrowser.open_new_tab(url)


"""
i = 0
while i <5:
    headers = { 'User-Agent': UserAgent().random }
    url = 'https://api.ipify.org'
    proxy_auth = str(random.randint(10000, 2147483647)) + ':' + 'torProxy123'
    p = {'http': 'socks5//{}@127.0.0.1:9050'.format(proxy_auth), 'https': 'socks5//{}@127.0.0.1:9050'.format(proxy_auth)}
    r = requests.get(url, proxies=p, timeout=10)

    print(r)
    i += 1

proxy_auth = str(random.randint(10000, 2147483647)) + ':' + 'passwrd'
proxies = {'http': 'socks5://{}@localhost:9050'.format(proxy_auth), 'https': 'socks5://{}@localhost:9050'.format(proxy_auth)}
response = requests.get(url, proxies=proxies)
print(response.text())
"""
