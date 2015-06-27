__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import requests
import time
from abc import ABCMeta, abstractmethod


class AbstractScrape:
    __metaclass__ = ABCMeta

    def __init__(self, queue=None):
        self.ref_id = None
        self.sleep  = 3

        if queue is None:
            self.queue = []

    def empty(self):
        return len(self.queue) == 0

    def get(self):
        if not self.empty():
            result = self.queue[0]
            del self.queue[0]
        else:
            result = None
        return result

    def put(self, item):
        self.queue.append(item)

    def peek(self):
        return self.queue[0] if not self.empty() else None

    def tail(self):
        return self.queue[-1] if not self.empty() else None

    def length(self):
        return len(self.queue)

    def clear(self):
        self.queue = []

    def list(self):
        print('\n'.join(url for url in self.queue))

    def monitor(self):
        self.update()

        while 1:
            while not self.empty():
                paste = self.get()
                self.ref_id = paste.id
                # logging.info('[*] Checking ' + paste.url)
                paste.text = self.get_paste_text(paste)
                # helper.build_tweet(paste)

            self.update()

            while self.empty():
                # logging.debug('[*] No results... sleeping')
                time.sleep(self.sleep)
                self.update()

    def get_paste_text(self, paste):
        r = requests.get(paste.url)

        return r.content

    @abstractmethod
    def update(self):
        pass