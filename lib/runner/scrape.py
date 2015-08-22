__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

from threading import Thread as threading_Thread
from time import sleep
from lib.runner.abstract import AbstractCommand
from lib.scrapers.pastebin import PastebinScraper


class DumpScraperScrape(AbstractCommand):
    def run(self):
        # Ok, let's start a daemon that will search for new dumps
        pastebin_thread = threading_Thread(target=PastebinScraper(self.settings).monitor)

        print("Started monitoring paste sites")

        for thread in (pastebin_thread, ):
            thread.daemon = True
            thread.start()

        # Let threads run
        try:
            while 1:
                sleep(5)
        except KeyboardInterrupt:
            print 'Stopped.'
