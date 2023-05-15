import requests
import cfscrape
from fake_useragent import UserAgent
from time import time, sleep

#PROXIES_LIST = get_proxies_list('Webshare')
#pr = PROXIES_LIST[0]
proxy = {
    "http": 'http://vvyyimhm:vu4t6rhgy97x @138.128.69.9:8078',
    "https": 'https://vvyyimhm:vu4t6rhgy97x @138.128.69.9:8078'
    }
"""
headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0" ,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br"
    }
"""
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    }
url = 'https://www.coingecko.com/en/coins/bitcoin'
url2 ='https://httpbin.org/cookies'

c = {"__atuvc":"1|30","__cf_bm":"5LOaQ3NIPc.QTU02oonS7ssLz5elX_rJmq5jTBMS9pA-1640334110-0-AdczkQ0SmMovjnCe90Dv+03Pbz4hfJh/mq9XsY6vtCvYZ3JRYd7IBbgzhNOTAjvJuLfM2Z0cfG6cP39lcAwuZper7Bh7v/ZeJA+kn2jEK0ECHENn76YZ1KQF686RkRhkvIErQKP84hdAjQKOrnXDUzFcDK+1hlQzHhF/h0YJFnxv","__gads":"ID=64e4ddb9c2b8c5e6-220e9e8ad9ce001f:T=1614413752:S=ALNI_Mbx8jpOiNR5m7rISRT7AYpjumT93g","_ga":"GA1.2.359378639.1613921993","_ga_LJR3232ZPB":"GS1.1.1640334107.14.1.1640334108.0","_gaexp":"GAX1.2.SPxjkMasRayCjV6SpTBIMw.19031.2!iK3ermLkRXOQrPmLmmxe1w.19071.0!ziJPa17vSn-OMacw479Hzw.19020.0","_gid":"GA1.2.995925519.1640291589","_session_id":"b0ad56f521267847b808a7e0a7b7a354","cf_clearance":"GHhHjm0kq3VdZOyARV9Tc18Y7In5sIcIUflK17Jq45M-1640293881-0-150"}

"""
cookies_jar = requests.cookies.RequestsCookieJar()
cookies_jar.set('','', 'coingecko.com', '')
Cookie(_ga_LJR3232ZPB=GS1.1.1640334107.14.1.1640334108.0; _ga=GA1.2.359378639.1613921993; __gads=ID=64e4ddb9c2b8c5e6-220e9e8ad9ce001f:T=1614413752:S=ALNI_Mbx8jpOiNR5m7rISRT7AYpjumT93g; __atuvc=1%7C30; _gaexp=GAX1.2.SPxjkMasRayCjV6SpTBIMw.19031.2!iK3ermLkRXOQrPmLmmxe1w.19071.0!ziJPa17vSn-OMacw479Hzw.19020.0; _session_id=b0ad56f521267847b808a7e0a7b7a354; _gid=GA1.2.995925519.1640291589; cf_clearance=GHhHjm0kq3VdZOyARV9Tc18Y7In5sIcIUflK17Jq45M-1640293881-0-150; __cf_bm=5LOaQ3NIPc.QTU02oonS7ssLz5elX_rJmq5jTBMS9pA-1640334110-0-AdczkQ0SmMovjnCe90Dv+03Pbz4hfJh/mq9XsY6vtCvYZ3JRYd7IBbgzhNOTAjvJuLfM2Z0cfG6cP39lcAwuZper7Bh7v/ZeJA+kn2jEK0ECHENn76YZ1KQF686RkRhkvIErQKP84hdAjQKOrnXDUzFcDK+1hlQzHhF/h0YJFnxv))
response = requests.get(url, cookies=cookies_jar)
print(response.status_code)
print(response.headers)
"""
c ={"_session_id": "b0ad56f521267847b808a7e0a7b7a354"}

with requests.Session() as sess:

    #cookies = c
    resp = sess.get(url, headers=headers, stream=True, cookies=c)
    if resp.status_code == 503:
        print("STATUS 1", resp.status_code, resp.headers)
        """
        for cookie in resp.cookies:
            domain = cookie.domain
            name = cookie.name
            value = cookie.value
        sleep(45)
        cookies = {'name': name, 'value': value, 'domain': domain}
        r = sess.get(url, headers=headers, stream=True, cookies=cookies)
        print("STATUS 2", resp.status_code, resp.headers)
        """
    else:

        print(resp.status_code)
        print(resp.headers)




#session.headers = headers
#session.proxies = proxy
#scraper = cfscrape.create_scraper(sess=session)
#print(scraper.get(url).content)

#r = requests.get(url, headers=headers, proxies=proxy)
#print(r)
#print(r.text)
