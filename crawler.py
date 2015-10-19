import os.path
import json
from datetime import datetime
import asyncio

import aiohttp
from aiohttp import web



class Crawler(object): 
    def __init__(self, loop, scraper, max_conn=30):
        self.loop = loop
        self.semaphore = asyncio.Semaphore(max_conn)#For preventing accidental DOS
        self.scraper = scraper

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
    def download_page(self, url):
        try:
            with (yield from self.semaphore):#Limits number of concurrent requests
                html = yield from self.get_page(url)
                self.scraper.process(html)
        except web.HTTPNotFound as e:
            print('Resource not found: ' + url)
        except Exception as e:
            print('Error:')
            print(e)
        return url


    # asyncio driver 
    def crawl(self, urls):
        schedule = [self.download_page(url) for url in urls]
        garcon = asyncio.wait(schedule)
        res, _ = self.loop.run_until_complete(garcon)
        return len(res)



