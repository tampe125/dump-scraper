__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import logging
import datetime
from os import path, makedirs, walk
from sys import stdout as sys_stdout
from shutil import rmtree as shutil_rmtree
from lib.exceptions.exceptions import RunningError
from lib.extractor.hash import HashExtractor
from lib.extractor.plain import PlainExtractor
from lib.runner.abstract import AbstractCommand


class DumpScraperExtract(AbstractCommand):
    def check(self):
        if not path.exists(self.settings['data_dir'] + "/" + 'organized'):
            raise RunningError("There aren't any organized dump files to process. Organize them before continuing.")

        if not path.exists(self.settings['data_dir'] + "/" + 'processed'):
            makedirs(self.settings['data_dir'] + "/" + 'processed')
        if not path.exists(self.settings['data_dir'] + "/" + 'processed/hash'):
            makedirs(self.settings['data_dir'] + "/" + 'processed/hash')
        if not path.exists(self.settings['data_dir'] + "/" + 'processed/plain'):
            makedirs(self.settings['data_dir'] + "/" + 'processed/plain')

    def run(self):
        folders = []
        dates = [self.parentArgs.since]

        if self.parentArgs.until:
            date  = datetime.datetime.strptime(self.parentArgs.since, "%Y-%m-%d").date()
            end   = datetime.datetime.strptime(self.parentArgs.until, "%Y-%m-%d").date()

            date += datetime.timedelta(days=1)

            while end >= date:
                dates.append(date.strftime('%Y-%m-%d'))
                date += datetime.timedelta(days=1)

        for date in dates:
            folders.append('hash/' + date)
            folders.append('plain/' + date)

        extractors = {'hash': HashExtractor(), 'plain': PlainExtractor()}

        for folder in folders:
            source = self.settings['data_dir'] + "/" + 'organized/' + folder

            if not path.exists(source):
                print("Directory " + source + " does not exist!")
                print("")
                continue

            logging.getLogger('dumpscraper').info("Directory   : " + folder)

            cleared = []

            for root, dirs, files in walk(source):
                for dump in files:
                    # If the force param is set, skip all the files that do not match
                    if self.parentArgs.force and self.parentArgs.force not in dump:
                        sys_stdout.write('@')
                        sys_stdout.flush()
                        continue

                    sys_stdout.write('.')
                    sys_stdout.flush()

                    with open(root + "/" + dump, 'r+') as handle:
                        data = handle.read()

                    # Remove /r since they could mess up regex
                    data = data.replace("\r", "")

                    info = {'data': data}

                    parts = source.split('/')
                    label = parts[-2]

                    try:
                        extractor = extractors[label]
                    except KeyError:
                        continue

                    extractor.reset().setinfo(info).analyze()

                    extracted = extractor.extracted.strip(' \n\t\r')

                    if extracted:
                        destination = self.settings['data_dir'] + "/" + 'processed/' + label + '/' + path.basename(root)

                        # If asked for a clean run, let's delete the entire folder before copying any file
                        if self.parentArgs.clean and destination not in cleared and path.exists(destination):
                            cleared.append(destination)
                            shutil_rmtree(destination)

                        if not path.exists(destination):
                            makedirs(destination)

                        with open(destination + '/' + path.basename(dump), 'w') as dump_file:
                            dump_file.write(extracted)