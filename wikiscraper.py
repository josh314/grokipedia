from datetime import datetime
import json
import os.path
import unicodedata
import asyncio

from bs4 import BeautifulSoup
import aiofiles

WP_ARTICLE_BASE = 'http://www.wikipedia.org/wiki/'

def normalize(string):#Remove diacritics and whatevs
    return "".join(ch.lower() for ch in unicodedata.normalize('NFD', string) if not unicodedata.combining(ch))

class WikiScraper(object):
    def __init__(self, loop, save_dir='.'):
        self.save_dir = save_dir
        self.loop = loop

    def parse(self,html):
        doc = {}
        page = BeautifulSoup(html)
        doc['title'] = page.find(id='firstHeading').get_text()
        doc['categories'] = [ li.a['href'].split('/')[2] for li in page.find(id='mw-normal-catlinks').find_all('li') ]
        doc['content'] = page.find(id='mw-content-text').get_text()
        links = page.find(id='mw-content-text').find_all('a')
        def filter_links(links):
            for link in links:
                if link['href'].startswith('/wiki/') and 'class' not in link.attrs:
                    yield link['href'].split('/')[-1]
        doc['wikilinks'] = [link for link in filter_links(links)]
        page.decompose()
        return doc

    def build_filepath(self,title):
        now = datetime.now()
        filename = "{}.{}-{}-{}-{}:{}.json".format(title,now.year,now.month,now.day,now.hour,now.minute) 
        return os.path.join(self.save_dir, filename)
        
    # Saves html to file
    @asyncio.coroutine
    def save_doc(self,doc,title):
        filepath = self.build_filepath(title)
        f = yield from aiofiles.open(filepath, 'wt')
        try:
            yield from f.write(json.dumps(doc))
        finally:
            yield from f.close()
            
    def process(self,url,html):
        success = False
        wikilink_urls = []
        try:
            doc = self.parse(html)
            doc['url'] = url
            print("Parsed: " + doc['title'])
            asyncio.Task(self.save_doc(doc['wikilinks'],doc['title']))
            wikilink_urls = [WP_ARTICLE_BASE + topic for topic in doc['wikilinks']]
            success = True
        except Exception:
            print("Failure parsing: " + url)
        return (success, wikilink_urls)

