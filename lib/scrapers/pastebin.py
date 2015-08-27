__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

from logging import getLogger
from requests import get as requests_get
from time import sleep
from lib.scrapers.abstract import AbstractScrape
from lib.pastes.pastebin import PastebinPaste
from bs4 import BeautifulSoup
from lib.exceptions.exceptions import RunningError
from requests.exceptions import ConnectionError


class PastebinScraper(AbstractScrape):
    def __init__(self, settings):
        super(PastebinScraper, self).__init__(settings)

        self.ref_id = None

    def update(self):
        """update(self) - Fill Queue with new Pastebin IDs"""
        # logging.info('Retrieving Pastebin ID\'s')
        new_pastes = []
        raw = None

        while not raw:
            try:
                raw = requests_get('http://pastebin.com/archive').content
                if "Pastebin.com has blocked your IP" in raw:
                    getLogger('dumpscraper').critical("Pastebin blocked your IP. Wait a couple of hours and try again")
                    raise RunningError()
            except ConnectionError:
                # logging.info('Error with pastebin')
                raw = None
                sleep(5)

        results = BeautifulSoup(raw, "lxml").findAll(
            lambda tag: tag.name == 'td' and tag.a and '/archive/' not in tag.a['href'] and tag.a['href'][1:])

        for entry in results:
            paste = PastebinPaste(entry.a['href'][1:])
            # Check to see if we found our last checked URL
            if paste.id == self.ref_id:
                break
            new_pastes.append(paste)

        # Don't cry if we don't have any results
        try:
            # Let's save the starting id, so I can skip already processed pastes
            self.ref_id = results[0].a['href'][1:]
        except IndexError:
            getLogger('dumpscraper').info("Archive links not found")

        for entry in new_pastes[::-1]:
            # logging.info('Adding URL: ' + entry.url)
            self.put(entry)
