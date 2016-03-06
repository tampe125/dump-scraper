# encoding=utf8

__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import requests
from logging import getLogger
from time import sleep
from abc import ABCMeta, abstractmethod
from datetime import datetime
from os import path, makedirs


class AbstractScrape:
    __metaclass__ = ABCMeta

    def __init__(self, settings):
        self.ref_id = None
        self.sleep  = 3
        self.queue = []
        self.settings = settings

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
                try:
                    paste.text = requests.get(paste.url).content
                except:
                    # Mhm... something wrong happened, let's wait some time and try again later
                    sleep(5)
                    continue

                self.build_tweet(paste)

            while self.empty():
                # logging.debug('[*] No results... sleeping')
                sleep(self.sleep)
                self.update()

    def build_tweet(self, paste):
        """
        build_tweet(url, paste) - Determines if the paste is interesting and, if so, builds and returns the tweet accordingly

        """
        tweet = None

        if paste.match():
            filename = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "_" + paste.id

            dObject = datetime.now()
            folder  = dObject.strftime('%Y') + '/' + dObject.strftime('%m') + '/' + dObject.strftime('%d')

            if not path.exists(path.realpath(self.settings['data_dir'] + "/raw/" + folder)):
                    makedirs(path.realpath(self.settings['data_dir'] + "/raw/" + folder))

            with open(path.realpath(self.settings['data_dir'] + "/raw/" + folder + "/" + filename + ".txt"), 'w+') as dump_file:
                    dump_file.write(paste.text)

            url = paste.url
            tweet = url

            if paste.type == 'db_dump':
                if paste.num_emails > 0:
                    tweet += 'Emails: ' + str(paste.num_emails)
                if paste.num_hashes > 0:
                    tweet += 'Hashes: ' + str(paste.num_hashes)
                if paste.num_hashes > 0 and paste.num_emails > 0:
                    tweet += 'E/H: ' + str(round(
                        paste.num_emails / float(paste.num_hashes), 2))
                tweet += 'Keywords: ' + str(paste.db_keywords)
            elif paste.type == 'google_api':
                tweet += 'Found possible Google API key(s)'
            elif paste.type in ['cisco', 'juniper']:
                tweet += 'Possible ' + paste.type + ' configuration'
            elif paste.type == 'ssh_private':
                tweet += 'Possible SSH private key'
            elif paste.type == 'honeypot':
                tweet += 'Dionaea Honeypot Log'
            elif paste.type == 'pgp_private':
                tweet += 'Found possible PGP Private Key'

            getLogger('dumpscraper').info("\tDump found: " + filename + ' (' + tweet + ')')

        return tweet

    @abstractmethod
    def update(self):
        pass
