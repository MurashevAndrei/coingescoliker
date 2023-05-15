from bs4 import BeautifulSoup
import requests
import json


FIRST_PART_OF_LINK = 'https://www.coingecko.com/en/coins/'
FIRST_PART_OF_PAGE = 'https://www.coingecko.com/'
ALL_COINGECKO_TABLE = {}


def load_main_page(link):
    r = requests.get(link)
    return r


def config_list_of_links(r):
    soup = BeautifulSoup(r.content, 'lxml')
    value = soup.findAll('a', class_="d-lg-none font-bold")
    full_links = []
    for val in value:
        var = val["href"]
        second_part_of_link = var.split('/')[-1]
        full_links.append(FIRST_PART_OF_LINK + second_part_of_link)
    return full_links


def page_link(link):
    next_page_list = [link]
    while link:
        r = load_main_page(link)
        soup = BeautifulSoup(r.content, 'lxml')
        page = soup.find('li', class_="page-item next")
        if page:
            next_page = page.find('a', class_="page-link")
            next_page = next_page['href']
            link = FIRST_PART_OF_PAGE + next_page
            next_page_list.append(link)
            print(next_page)
        else:
            link = False
    return next_page_list

def save_json(coins_list):
    with open('coins_list.json', 'w') as write_file:
        json.dump(coins_list, write_file, indent=4)

def run_coins_list(mainpage):
    pages = page_link(mainpage)
    coins_list = []
    for link in pages:
        coins_list.extend(config_list_of_links(load_main_page(link)))
    save_json(coins_list)
    return True

if run_coins_list(FIRST_PART_OF_PAGE):
    print('All links write in coins_list.json')
else:
    print('Error')

