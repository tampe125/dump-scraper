__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import argparse
import json
import os

from lib.exceptions import exceptions
from lib.runner import scrape, organize


class DumpScraper():
    def __init__(self):
        parser = argparse.ArgumentParser()
        # parser.add_argument('command', metavar='[command]')
        subparsers = parser.add_subparsers(dest='command')

        parser_scrape = subparsers.add_parser('scrape')

        parser_organize = subparsers.add_parser('organize')
        parser_organize.add_argument('-s', '--since',
                                     help='Starting date for the analysis, format YYYY-MM-DD',
                                     required=True)
        parser_organize.add_argument('-u', '--until',
                                     help='Stopping date for the analysis, format YYYY-MM-DD. If not supplied only the SINCE date will be processed')

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
        if not os.path.exists(os.path.realpath("settings.json")):
            raise exceptions.InvalidSettings("Please rename the file settings-dist.json to settings.json "
                                                  "and fill the required info")

        json_data = open(os.path.realpath("settings.json"))
        settings = json.load(json_data)
        json_data.close()

        required_keys = ['app_key', 'app_secret', 'token', 'token_secret']

        for required in required_keys:
            try:
                value = settings[required]

                if value == '':
                    raise exceptions.InvalidSettings("Please fill the required info before continuing")

            except KeyError:
                raise exceptions.InvalidSettings("Please fill the required info before continuing")

        self.settings = settings

    def run(self):
        self.banner()

        # Peform some sanity checks
        try:
            self.checkenv()
        except exceptions.InvalidSettings as error:
            print("")
            print(error)

            return

        # Let's load the correct object
        if self.args.command == 'scrape':
            runner = scrape.DumpScraperScrape(self.settings, self.args)
        elif self.args.command == 'organize':
            runner = organize.DumpScraperOrganize(self.settings, self.args)
        else:
            print("Unrecognized command")
            return

        # And away we go!
        try:
            runner.check()
            runner.run()
        # Ehm.. something wrong happened?
        except exceptions.RunningError as error:
            print("")
            print(error)
        # Always save the updated settings
        finally:
            with open(os.path.realpath("settings.json"), 'w+') as update_settings:
                json.dump(self.settings, update_settings, indent=4)


try:
    scraper = DumpScraper()
    scraper.run()
except KeyboardInterrupt:
    print("")
    print("Operation aborted")
    exit()