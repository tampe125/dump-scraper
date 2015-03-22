__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import argparse
import os
import dump_exceptions
import json
import scrape


class DumpScraper():
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('command', metavar='[command]')

        self.args = parser.parse_args()

    def banner(self):
        print("Dump Scraper - A better way of scraping")
        print("Copyright (C) 2015 FabbricaBinaria - Davide Tampellini")
        print("===============================================================================")
        print("Dump Scraper is Free Software, distributed under the terms of the GNU General")
        print("Public License version 3 or, at your option, any later version.")
        print("This program comes with ABSOLUTELY NO WARRANTY as per sections 15 & 16 of the")
        print("license. See http://www.gnu.org/licenses/gpl-3.0.html for details.")
        print("===============================================================================")

    def checkenv(self):
        if not os.path.exists(os.path.realpath("../settings.json")):
            raise dump_exceptions.InvalidSettings("Please rename the file settings-dist.json to settings.json "
                                                           "and fill the required info")

        json_data = open(os.path.realpath("../settings.json"))
        settings = json.load(json_data)

        required_keys = ['app_key', 'app_secret', 'token', 'token_secret']

        for required in required_keys:
            try:
                value = settings[required]

                if value == '':
                    raise dump_exceptions.InvalidSettings("Please fill the required info before continuing")

            except KeyError:
                raise dump_exceptions.InvalidSettings("Please fill the required info before continuing")

        self.settings = settings

    def run(self):
        self.banner()

        # Peform some sanity checks
        try:
            self.checkenv()
        except dump_exceptions.InvalidSettings as error:
            print("")
            print(error)

            return

        # Let's load the correct object
        if self.args.command == 'scrape':
            runner = scrape.DumpScraperScrape(self.settings)
        else:
            print("Unrecognized command")
            return

        # And away we go!
        try:
            runner.run()
        # Ehm.. something wrong happened?
        except dump_exceptions.RunningError as error:
            print("")
            print(error)
        # Always save the updated settings
        finally:
            with open(os.path.realpath("../settings.json"), 'w+') as update_settings:
                json.dump(self.settings, update_settings, indent=4)


try:
    scraper = DumpScraper()
    scraper.run()
except KeyboardInterrupt:
    print("")
    print("Operation aborted")
    exit()