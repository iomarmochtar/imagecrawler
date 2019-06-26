__author__ = ('Imam Omar Mochtar', 'iomarmochtar@gmail.com')

"""
Simple image crawler by follow the links recursively (within domain only)
using builtin python library (without any dependency)
works for python 2.7+
"""

import urllib
import json
import re
from pprint import pprint
try:
    from urllib.request import Request, urlopen, HTTPError, urlparse  # Python 3
except ImportError:
    from urllib2 import Request, urlopen, HTTPError  # Python 2
    from urlparse import urlparse

class StopCrawlingException(Exception):
    pass

class ImageCrawler(object):

    max_recur = 5
    curr_recur = 0

    images = set()
    links = []
    target = None
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    img_re = re.compile(r'<img.*?src=["|\'](.*?)["|\']')
    a_re = None
    is_debug = False
    
    def __init__(self, target, max_recur=None, is_debug=False):
        self.target = target
        # maximum page fetch
        self.max_recur = max_recur
        self.a_re = re.compile(
            r'<a.*?href=["|\']({}.*?)["|\']'.format(target)
        )
        self.is_debug = is_debug

    def fetch_html(self, url):
        pisah = urlparse(url)
        headers = {
            'Host': pisah.netloc,
            #'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        req = Request(url, headers=headers)
        return urlopen(req).read().decode('utf-8')

    def log(self, txt):
        if not self.is_debug:
            return
        print(txt)

    def fetch_images(self, url):
        if self.max_recur and self.max_recur == self.curr_recur:
            raise StopCrawlingException()
        self.links.append(url)
        self.curr_recur += 1
        self.log('[{}] Crawling => {}'.format(self.curr_recur, url))

        content = self.fetch_html(url)
        images = self.img_re.findall(content)
        links = self.a_re.findall(content)
        self.images.update(images)
        self.log('[{}] Found {} image(s) and {} link(s)'.format(
            self.curr_recur,
            len(images),
            len(links)
        ))
        for link in links:
            # make sure the links is never visited
            if link in self.links:
                continue 
            self.fetch_images(link)

    def get_images(self):
        try:
            self.fetch_images(self.target)
        except StopCrawlingException:
            pass
        self.log('DONE')
        self.log('Total image => {}'.format( len(self.images) ))
        self.log('Total links => {}'.format( len(self.links) ))
        return {
            'images': self.images,
            'links': self.links
        }

if __name__ == '__main__':
    obj = ImageCrawler('https://blog.mochtar.net/', max_recur=2, is_debug=True)
    pprint(obj.get_images())
