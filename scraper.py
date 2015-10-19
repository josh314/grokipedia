import os.path
import json
from datetime import datetime
import asyncio

import aiohttp
from aiohttp import web

WP_DOMAIN = "http://en.wikipedia.org/wiki/"
SAVE_DIR = 'tmp/'

class Scraper(object): 
    def __init__(self, loop, parser, max_conn=30):
        self.loop = loop
        self.semaphore = asyncio.Semaphore(max_conn)#For preventing accidental DOS
        self.parser = parser

    # Saves html to file
    def save_doc(self,doc,title):
        now = datetime.now()
        filename = "{}-{}-{}-{}:{}:{}.{}.json".format(now.year,now.month,now.day,now.hour,now.minute,now.second,title) 
        path = os.path.join(SAVE_DIR, filename)
    #    print("Saving to "+path)
        with open(path, 'wt') as fp:
            json.dump(doc,fp)
            
    # parse html and build save document
    def parse(self,html):
        return self.parser.parse(html)
                
    @asyncio.coroutine
    def get_page(self,url):
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
    def download_page(self, title):
        try:
            with (yield from self.semaphore):#Limits number of concurrent requests
                html = yield from self.get_page(WP_DOMAIN + title)
                print('Completed download of: ' + title)
                document = self.parse(html)
                self.save_doc(document, title)
        except web.HTTPNotFound as e:
            print('Topic not found at Wikipedia: ' + title)
        except Exception as e:
            print('Error:')
            print(e)
        return title


    # asyncio driver 
    def crawl(self, topics):
        schedule = [self.download_page(t) for t in topics]
        garcon = asyncio.wait(schedule)
        res, _ = self.loop.run_until_complete(garcon)
        return len(res)



