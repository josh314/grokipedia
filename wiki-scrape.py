import asyncio
import logging
import aiohttp

from scraper import Scraper
from wikiparser import WikiParser
#logging.basicConfig(level=logging.DEBUG)

topics = [
    'Mathematics',
    'Barack_Obama',
    'Daredevil',
    'Monsieur_Farty_Pants',
    'fhgjfds',
]

loop = asyncio.get_event_loop()
#loop.set_debug(True)
ananzi = Scraper(loop, WikiParser())
ananzi.crawl(topics)
loop.close()
