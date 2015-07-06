__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

from threading import Thread as threading_Thread
from time import sleep
from lib.runner.abstract import AbstractCommand
from lib.scrapers.pastebin import PastebinScraper


class DumpScraperScrape(AbstractCommand):
    def run(self):
        bot = None
        bitly = None

        try:
            import bitly_api

            bitly = bitly_api.Connection(self.settings['bot']['raw']['bitly']['username'],
                                         self.settings['bot']['raw']['bitly']['key'])
        # Oh well, what the hell...
        except ImportError:
            pass
        except KeyError:
            pass
        except bitly_api.BitlyError:
            pass

        try:
            import twitter

            bot = twitter.Api(consumer_key=self.settings['bot']['raw']['consumer_key'],
                              consumer_secret=self.settings['bot']['raw']['consumer_secret'],
                              access_token_key=self.settings['bot']['raw']['access_token_key'],
                              access_token_secret=self.settings['bot']['raw']['access_token_secret'])
            bot.VerifyCredentials()
        # Oh well, what the hell...
        except ImportError:
            pass
        except KeyError:
            pass
        except twitter.error.TwitterError:
            pass

        # Ok, let's start a daemon that will search for new dumps
        pastebin_thread = threading_Thread(target=PastebinScraper(self.settings, bot, bitly).monitor)

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
