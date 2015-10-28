from datetime import datetime
import json
import os.path
import unicodedata
import asyncio

from bs4 import BeautifulSoup
import aiofiles

WP_ARTICLE_BASE = 'https://en.wikipedia.org/wiki/'

def wikiurl(title):
    return WP_ARTICLE_BASE + title


def normalize(string):#Remove diacritics and whatevs
    return "".join(ch.lower() for ch in unicodedata.normalize('NFD', string) if not unicodedata.combining(ch))

def is_wikilink(url):
    return url.startswith('/wiki/') or url.startswith(WP_ARTICLE_BASE)

def is_article(title):
    """\
    Checks if the title is for an article or a special page. The title is
    part of the absolute url:

    http://www.wikipedia.org/wiki/TITLE

    Special pages have titles like this: NAMESPACE:SUBTITLE. For example, 
    'Help:Abbreviations' or 'Template_talk:Nobel_prizes'. When a colon appears 
    in an article title, it is followed by an underscore (which represents 
    a space), e.g. 'Terminator_2:_Judgment_Day'. Also, initial colons in a 
    title are ignored.
    """
    res = True
    parts = title.split(":")
    if len(parts) > 1 and parts[0] and not parts[1].startswith("_"):
        res = False
    return res

# Filters list of link Tags to the urls for WP articles 
def article_urls(links):
    for link in links:
        url = link['href']
        if is_wikilink(url) and is_article(url):
            yield url

class WikiScraper(object):
    def __init__(self, loop, save_dir='.'):
        self.save_dir = save_dir
        self.loop = loop

    def parse(self,html):
        doc = {}
        page = BeautifulSoup(html)
        doc['title'] = page.find(id='firstHeading').get_text()
        content = page.find(id='mw-content-text')
        links = content.find_all('a')
        
        doc['wikilinks'] = [url.split("/wiki/")[1] for url in article_urls(links)]
        doc['content'] = content.get_text()
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
            self.loop.create_task(self.save_doc(doc['content'],doc['title']))
            wikilink_urls = [WP_ARTICLE_BASE + topic for topic in doc['wikilinks']]
            success = True
        except Exception:
            print("Failure parsing: " + url)
        return (success, wikilink_urls)

