import asyncio

import aiohttp
from aiohttp import web

class Crawler(object): 
    def __init__(self, loop, scraper, max_conn=30):
        self.loop = loop
        self.scraper = scraper
        self.sem = asyncio.Semaphore(max_conn)#For preventing accidental DOS
        self.queued = set()
        self.processing = set()
        self.done = set()
        self.failed = set()

    def seen(self, url):
        return (url in self.queued or url in self.processing or url in self.done)  
        
    def queue(self, url):
        if not self.seen(url):
            self.queued.add(url)
            task = asyncio.Task(self.process_page(url))
        
        
    @asyncio.coroutine
    def get_html(self,url):
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
    def process_page(self, url):
        res = {}
        self.queued.remove(url)
        self.processing.add(url)
        try:
            with (yield from self.sem):#Limits number of concurrent requests
                html = yield from self.get_html(url)
        except web.HTTPNotFound as e:
            print('Resource not found: ' + url)
            self.failed.add(url)
        else:
             res = self.scraper.process(html)
             self.done.add(url)
             #TODO: Update queue based on scraping results (i.e. add outgoing links) 
        finally:
            self.processing.remove(url)

        return res

    @asyncio.coroutine
    def crawl(self):
        while self.queued or self.processing:
            yield from asyncio.sleep(1)
        print(self.failed)
        
    def launch(self, urls):
        for url in urls:
            self.queue(url)
        task = asyncio.Task(self.crawl())
        self.loop.run_until_complete(task)
