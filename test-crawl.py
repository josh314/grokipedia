import asyncio
import logging
import aiohttp

from crawler import Crawler
from dummy import Scraper
#logging.basicConfig(level=logging.DEBUG)

WP_DOMAIN = "http://en.wikipedia.org/wiki/"

topics = [
    'Mathematics',
    'Barack_Obama',
    'Daredevil',
    'Monsieur_Farty_Pants',
    'fhgjfds',
]
urls = [WP_DOMAIN + t for t in topics]

loop = asyncio.get_event_loop()
#loop.set_debug(True)

ananzi = Scraper(loop, Scraper())
ananzi.crawl(urls)
loop.close()
