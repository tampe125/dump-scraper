__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import colorama
import datetime
import lxml.html as LH
import json
import requests
import urllib
import sys
import os
from logging import getLogger
from time import sleep
from lib.runner.abstract import AbstractCommand
from lib.exceptions.exceptions import RunningError


class DumpScraperScrapeold(AbstractCommand):
    def run(self):
        base_url = 'https://twitter.com/i/search/timeline?f=realtime&q='
        base_query = 'from:dumpmon since:%s until:%s'
        prev_day = '1970-05-01'
        processed = 0

        origurl = base_url + urllib.quote(base_query % (self.parentArgs.since, self.parentArgs.until))

        processing = True
        url = origurl
        # We have to pass an user agent, otherwise Twitter will display an empty content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'
        }

        dump_logger = getLogger('dumpscraper')

        while processing:
            r = requests.get(url, headers=headers)
            json_data = json.loads(r.content)
            raw_html = json_data['items_html'].strip()

            if not raw_html:
                processing = False
                continue

            html = LH.fromstring(raw_html)

            removed = 0
            tweets = html.cssselect('.original-tweet')

            if not tweets:
                processing = False

            for tweet in tweets:
                link = tweet.cssselect('.twitter-timeline-link')

                if not link:
                    continue

                link = link[0]
                processed += 1

                paste_link = link.get('data-expanded-url')
                timestamp = tweet.cssselect('.js-short-timestamp')[0].get('data-time')
                tweetid = tweet.get('data-tweet-id')

                if not paste_link:
                    continue

                day = datetime.datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d')

                if day != prev_day:
                    prev_day = day
                    dump_logger.info("Processing day: " + day)

                folder = day

                if not os.path.exists(os.path.realpath("data/raw/" + folder)):
                    os.makedirs(os.path.realpath("data/raw/" + folder))

                sleep(self.settings['delay'])

                # Sometimes we download virus and the AV drops the connection
                try:
                    data = requests.get(paste_link)
                except requests.exceptions.ConnectionError:
                    continue

                if not data.text:
                    continue

                if "Pastebin.com has blocked your IP" in data.text:
                    raise RunningError(
                        colorama.Fore.RED + "Pastebin blocked your IP. Wait a couple of hours and try again, raising the delay between tweets"
                    )

                if "has been removed" in data.text:
                    removed += 1
                    continue

                with open(os.path.realpath("data/raw/" + folder + "/" + str(tweetid) + ".txt"), 'w+') as dump_file:
                    dump_file.write(data.text.encode('utf-8'))

            # Let's setup the url for the next iteration
            url = origurl + '&scroll_cursor=' + json_data['scroll_cursor']

        dump_logger.info("Total processed tweets: " + str(processed))
