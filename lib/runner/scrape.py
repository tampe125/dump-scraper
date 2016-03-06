__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import colorama
import datetime
import twitter
import os
import requests
from logging import getLogger
from time import sleep
from lib.runner.abstract import AbstractCommand
from lib.exceptions.exceptions import RunningError


class DumpScraperScrape(AbstractCommand):
    def run(self):
        prev_day = '1970-05-01'
        since_id = None if not self.settings['last_id'] else self.settings['last_id']
        max_id = None if not self.settings['max_id'] else self.settings['max_id']
        processed = 0

        connection = twitter.Api(consumer_key=self.settings['app_key'],
                                 consumer_secret=self.settings['app_secret'],
                                 access_token_key=self.settings['token'],
                                 access_token_secret=self.settings['token_secret'])

        # Let's check if we really have some valid credentials
        try:
            connection.VerifyCredentials()
        except twitter.error.TwitterError as error:
            raise RunningError(colorama.Fore.RED + 'Twitter error: ' + error.message[0]['message'])

        dump_logger = getLogger('dumpscraper')

        while processed <= self.settings['processing_limit']:

            tweets = connection.GetUserTimeline(screen_name='dumpmon', max_id=max_id,
                                                exclude_replies=True, include_rts=False, count=self.settings['limit'],
                                                since_id=since_id)

            if not len(tweets):
                break

            removed = 0
            processed += len(tweets)

            for tweet in tweets:
                max_id = tweet.id if not max_id else min(max_id, tweet.id)
                max_id -= 1

                self.settings['last_id'] = max(since_id, tweet.id)

                try:
                    link = tweet.urls[0].expanded_url
                except KeyError:
                    continue

                dObject = datetime.datetime.fromtimestamp(tweet.created_at_in_seconds)
                day = dObject.strftime('%Y-%m-%d')

                if day != prev_day:
                    prev_day = day
                    dump_logger.info("Processing day: " + day)

                # Let's create the folder name using year/month/(full-date) structure
                folder  = dObject.strftime('%Y') + '/' + dObject.strftime('%m') + '/' + dObject.strftime('%d')

                target_dir = os.path.realpath(self.settings['data_dir'] + "/raw/" + folder)

                # If I already have the file, let's skip it
                if os.path.isfile(target_dir + '/' + str(tweet.id) + '.txt'):
                    continue

                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                sleep(self.settings['delay'])

                data = requests.get(link)

                if not data.text:
                    continue

                if "Pastebin.com has blocked your IP" in data.text:
                    self.settings['last_id'] = since_id
                    raise RunningError(
                        colorama.Fore.RED + "Pastebin blocked your IP. Wait a couple of hours and try again, raising the delay between tweets"
                    )

                if "has been removed" in data.text:
                    removed += 1
                    continue

                with open(target_dir + "/" + str(tweet.id) + ".txt", 'w+') as dump_file:
                    dump_file.write(data.text.encode('utf-8'))

            dump_logger.info("Processed " + str(processed) + " tweets")
            dump_logger.info("Found " + str(removed) + " removed tweets in this batch")

        dump_logger.info("Total processed tweets: " + str(processed))
