import os.path
import json
from datetime import datetime

from bs4 import BeautifulSoup
import asyncio, aiohttp
from aiohttp import web

import logging
#logging.basicConfig(level=logging.DEBUG)

WP_DOMAIN = "http://en.wikipedia.org/wiki/"

topics = [
    'Mathematics',
    'Barack_Obama',
    'Daredevil',
    'Monsieur_Farty_Pants',
    'fhgjfds',
]

SAVE_DIR = 'tmp/'

# Saves html to file
def save_doc(doc,title):
    now = datetime.now()
    filename = "{}-{}-{}-{}:{}:{}.{}.json".format(now.year,now.month,now.day,now.hour,now.minute,now.second,title) 
    path = os.path.join(SAVE_DIR, filename)
#    print("Saving to "+path)
    with open(path, 'wt') as fp:
        json.dump(doc,fp)

# parse html and build save document
def parse(html):
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
    return doc

@asyncio.coroutine
def get_page(url):
    html = None
    err = None
    resp = yield from aiohttp.get(url)
    if resp.status == 200:
        html = yield from resp.read()
    else:
        if resp.status == 404:
            err = web.HTTPNotFound
        else:
            err = aiohttp.HttpProcessingError(
                code=resp.status, message=resp.reason,
                headers=resp.headers)
    resp.close()
    if(err):
        raise err
    return html
    
@asyncio.coroutine
def download_page(semaphore, title):
    try:
        with (yield from semaphore):#Limits number of concurrent requests
            html = yield from get_page(WP_DOMAIN + title)
        print('Completed download of: ' + title)
        document = parse(html)
        save_doc(document, title)
    except web.HTTPNotFound as e:
        print('Topic not found at Wikipedia: ' + title)
    except Exception as e:
        print('Error:')
        print(e)
    return title


# asyncio driver 
def crawl(topics, max_concur):
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    semaphore = asyncio.Semaphore(max_concur)#For preventing accidental DOS
    schedule = [download_page(semaphore,t) for t in topics]
    garcon = asyncio.wait(schedule)
    res, _ = loop.run_until_complete(garcon)
    loop.close()
    return len(res)


if __name__ == '__main__':
    crawl(topics,max_concur=30)
