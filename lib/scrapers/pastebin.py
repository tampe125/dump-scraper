__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import BeautifulSoup
import requests
from time import sleep
from lib.scrapers.abstract import AbstractScrape
from lib.pastes.pastebin import PastebinPaste


class PastebinScraper(AbstractScrape):
    def __init__(self, last_id=None):
        super(PastebinScraper, self).__init__()

        if not last_id:
            last_id = None

        self.ref_id = last_id

    def update(self):
        """update(self) - Fill Queue with new Pastebin IDs"""
        # logging.info('Retrieving Pastebin ID\'s')
        new_pastes = []
        raw = None

        while not raw:
            try:
                raw = requests.get('http://pastebin.com/archive').content
            except:
                # logging.info('Error with pastebin')
                raw = None
                sleep(5)
        results = BeautifulSoup.BeautifulSoup(raw).findAll(
            lambda tag: tag.name == 'td' and tag.a and '/archive/' not in tag.a['href'] and tag.a['href'][1:])

        if not self.ref_id:
            results = results[:60]

        for entry in results:
            paste = PastebinPaste(entry.a['href'][1:])
            # Check to see if we found our last checked URL
            if paste.id == self.ref_id:
                break
            new_pastes.append(paste)

        for entry in new_pastes[::-1]:
            # logging.info('Adding URL: ' + entry.url)
            self.put(entry)
