import asyncio
import logging

from crawler import Crawler
from wikiscraper import WikiScraper
#logging.basicConfig(level=logging.DEBUG)

topics = [
    'Mathematics',
    'Barack_Obama',
    'Daredevil',
    'Monsieur_Farty_Pants',
    'fhgjfds',
    'fhqwhgads',
]

urls = ["http://www.wikipedia.org/wiki/" + t for t in topics]


loop = asyncio.get_event_loop()
#loop.set_debug(True)
ananzi = Crawler(loop, WikiScraper())
ananzi.crawl(urls)
loop.close()
