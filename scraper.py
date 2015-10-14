import os.path

import asyncio, aiohttp


WP_DOMAIN = "http://en.wikipedia.org/wiki/"

topics = ['Mathematics', 'Barack_Obama', 'Daredevil', 'Monsieur_Farty_Pants', 'fhgjfds']

SAVE_DIR = 'tmp/'

# Saves html to file
def save_html(html, filename):
    path = os.path.join(SAVE_DIR, filename)
    with open(path, 'wb') as f:
        f.write(html)
        
@asyncio.coroutine
def get_page(url):
    resp = yield from aiohttp.get(url)
    html = yield from resp.read_and_close()
    return html
        
@asyncio.coroutine
def download_page(title):
    html = yield from get_page(WP_DOMAIN + title)
    print('Completed download of: ' + title)
    save_html(html, title.lower() + '.html')
    return title

# asyncio driver 
def crawl(topics):
    loop = asyncio.get_event_loop()
    schedule = [download_page(t) for t in topics]
    garcon = asyncio.wait(schedule)
    res, _ = loop.run_until_complete(garcon)
    loop.close()
    return res


if __name__ == '__main__':
    crawl(topics)
