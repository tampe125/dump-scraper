__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import datetime
import twitter
import os
import requests
import sys
from time import sleep
from lib.runner.abstract import AbstractCommand
from lib.exceptions.exceptions import RunningError

# Sadly there is a problem with shipping the certificate in the single executable, so I have to skip HTTPS verification
# This is turn will raise an InsecureRequestWarning, so we hav e to suppress it
# It's an ugly workaround while we found a way to make HTTPS connection work...
try:
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    # Guess what? Under Linux I don't have the packages attribute
    pass


class DumpScraperScrape(AbstractCommand):
    def run(self):
        prev_day = '1970-05-01'
        since_id = self.settings['last_id']
        max_id = self.settings['max_id']
        processed = 0

        connection = twitter.Api(consumer_key=self.settings['app_key'],
                                 consumer_secret=self.settings['app_secret'],
                                 access_token_key=self.settings['token'],
                                 access_token_secret=self.settings['token_secret'])

        # Let's check if we really have some valid credentials
        try:
            connection.VerifyCredentials()
        except twitter.error.TwitterError as error:
            raise RunningError('Twitter error: ' + error.message[0]['message'])

        while processed <= self.settings['processing_limit']:

            tweets = connection.GetUserTimeline(screen_name='dumpmon', max_id=max_id,
                                                exclude_replies=True, include_rts=False, count=self.settings['limit'],
                                                since_id=since_id)

            if not len(tweets):
                break

            removed = 0
            processed += len(tweets)

            for tweet in tweets:
                max_id = 0 if not max_id else min(max_id, tweet.id)
                max_id -= 1

                since_id = max(since_id, tweet.id)

                try:
                    link = tweet.urls[0].expanded_url
                except KeyError:
                    continue

                day = datetime.datetime.fromtimestamp(tweet.created_at_in_seconds).strftime('%Y-%m-%d')

                if day != prev_day:
                    prev_day = day
                    print("")
                    print("Processing day: " + day)

                folder = day

                if not os.path.exists(os.path.realpath("data/raw/" + folder)):
                    os.makedirs(os.path.realpath("data/raw/" + folder))

                sleep(self.settings['delay'])

                data = requests.get(link)

                if not data.text:
                    continue

                if "Pastebin.com has blocked your IP" in data.text:
                    self.settings['last_id'] = since_id
                    raise RunningError(
                        "Pastebin blocked your IP. Wait a couple of hours and try again, raising the delay between tweets"
                    )

                if "has been removed" in data.text:
                    removed += 1
                    sys.stdout.write('x')
                    sys.stdout.flush()
                    continue

                sys.stdout.write('.')
                sys.stdout.flush()

                with open(os.path.realpath("data/raw/" + folder + "/" + str(tweet.id) + ".txt"), 'w+') as dump_file:
                    dump_file.write(data.text.encode('utf-8'))

            print("")
            print("\tprocessed " + str(processed) + " tweets")
            print("\tFound " + str(removed) + " removed tweets in this batch")

        print("")
        print("Total processed tweets: " + str(processed))

        self.settings['last_id'] = since_id