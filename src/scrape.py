import datetime

__author__ = 'tampe125'

import json
import os
import requests
import sys
import twitter
from time import sleep

print("Dump Scraper - Twitter scraper")
print("Copyright (C) 2015 FabbricaBinaria - Davide Tampellini")
print("===============================================================================")
print("Dump Scraper is Free Software, distributed under the terms of the GNU General")
print("Public License version 3 or, at your option, any later version.")
print("This program comes with ABSOLUTELY NO WARRANTY as per sections 15 & 16 of the")
print("license. See http://www.gnu.org/licenses/gpl-3.0.html for details.")
print("===============================================================================")

if not os.path.exists(os.path.realpath("../settings.json")):
    print("Please rename the file settings-dist.json to settings.json and fill the required info")
    exit()

json_data = open(os.path.realpath("../settings.json"))
settings = json.load(json_data)

required_keys = ['app_key', 'app_secret', 'token', 'token_secret']

for required in required_keys:
    try:
        value = settings[required]

        if value == '':
            print("Please fill the required info before continuing")
            exit()

    except KeyError:
        print("Please fill the required info before continuing")
        exit()


prev_day = '1970-05-01'
since_id = settings['last_id']
max_id = settings['max_id']
processed = 0

connection = twitter.Api(consumer_key=settings['app_key'],
                         consumer_secret=settings['app_secret'],
                         access_token_key=settings['token'],
                         access_token_secret=settings['token_secret'])

while processed <= settings['processing_limit']:

    tweets = connection.GetUserTimeline(screen_name='dumpmon', max_id=max_id,
                                        exclude_replies=True, include_rts=False, count=settings['limit'],
                                        since_id=since_id)

    if not len(tweets):
        break

    nestedBreak = False
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

        if not os.path.exists(os.path.realpath("../data/raw/" + folder)):
            os.makedirs(os.path.realpath("../data/raw/" + folder))

        sleep(settings['delay'])

        data = requests.get(link)

        if not data.text:
            continue

        if "Pastebin.com has blocked your IP" in data.text:
            print("Pastebin blocked your IP. Wait a couple of hours and try again, raising the delay between tweets")
            nestedBreak = True
            break

        if "has been removed" in data.text:
            removed += 1
            sys.stdout.write('x')
            continue

        sys.stdout.write('.')

        with open(os.path.realpath("../data/raw/" + folder + "/" + str(tweet.id) + ".txt"), 'w+') as dump_file:
            dump_file.write(data.text.encode('utf-8'))

    # Ugly workaround for missing inner loop breaking
    if nestedBreak:
        break

    print("")
    print("\tprocessed " + str(processed) + " tweets")
    print("\tFound " + str(removed) + " removed tweets in this batch")

print("")
print("Total processed tweets: " + str(processed))

settings['last_id'] = since_id

with open(os.path.realpath("../settings.json"), 'w+') as update_settings:
    json.dump(settings, update_settings, indent=4)