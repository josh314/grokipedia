from datetime import datetime
import json
import os.path
import urllib.parse

from bs4 import BeautifulSoup

WP_ARTICLE_BASE = 'http://www.wikipedia.org/wiki/'

class WikiScraper(object):
    def __init__(self, save_dir='.'):
        self.save_dir = save_dir
        
    def parse(self,html):
        doc = {}
        page = BeautifulSoup(html)
        doc['title'] = page.find(id='firstHeading').get_text()
        doc['categories'] = [ li.a['href'].split('/')[2] for li in page.find(id='mw-normal-catlinks').find_all('li') ]
        doc['content'] = page.find(id='mw-content-text').get_text()
        links = page.find(id='mw-content-text').find_all('a')
        def filter_links(links):
            #TODO: use urllib.parse for extracting topic. Also handle fragments somehow
            for link in links:
                if link['href'].startswith('/wiki/') and 'class' not in link.attrs:
                    yield link['href'].split('/')[-1]
        doc['wikilinks'] = [link for link in filter_links(links)]
        page.decompose()
        return doc

#TODO: remove links internal to a page (i.e. ugly # url fragments) 

    # Saves html to file
    def save_doc(self,doc,title):
        now = datetime.now()
        filename = "{}.{}-{}-{}-{}:{}.json".format(title,now.year,now.month,now.day,now.hour,now.minute) 
        path = os.path.join(self.save_dir, filename)
    #    print("Saving to "+path)
        with open(path, 'wt') as fp:
            json.dump(doc,fp)

    def process(self,url,html):
        doc = self.parse(html)
        doc['url'] = url
        print("Parsed: " + doc['title'])
        self.save_doc(doc,doc['title'])
        wikilink_urls = [urllib.parse.urljoin(WP_ARTICLE_BASE, topic) for topic in doc['wikilinks']]
        return (True, wikilink_urls)

