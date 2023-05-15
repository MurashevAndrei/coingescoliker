import asyncio
from aiocfscrape import CloudflareScraper

async def test_open_page(url):
    async with CloudflareScraper() as session:
        async with session.get(url) as resp:
            print(resp.status)
            print(await resp.text())

if __name__ == '__main__':
    asyncio.run(test_open_page('<https://www.coingecko.com/en/coins/bitcoin>'))
