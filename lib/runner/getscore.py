__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import datetime
import re
from logging import getLogger
from csv import DictWriter as csv_DictWriter
from os import path, walk
from lib.detector.trash import TrashDetector
from lib.detector.hash import HashDetector
from lib.runner.abstract import AbstractCommand
from lib.detector.plain import PlainDetector
from lib.exceptions.exceptions import RunningError


class DumpScraperGetscore(AbstractCommand):
    def check(self):
        if not path.exists(self.settings['data_dir'] + "/" + 'raw'):
            raise RunningError("There aren't any dump files to process. Scrape them before continuing.")

    def run(self, **keyargs):
        if 'training' in keyargs and keyargs['training']:
            targetfolder = 'training'
            feature_path = self.settings['data_dir'] + "/training/features.csv"
            folders = ['trash', 'hash', 'plain']
        else:
            targetfolder = 'raw'
            feature_path = self.settings['data_dir'] + "/features.csv"
            # Let's convert the single date to a path
            folders = ['/'.join(self.parentArgs.since.split('-'))]

            if self.parentArgs.until:
                date  = datetime.datetime.strptime(self.parentArgs.since, "%Y-%m-%d").date()
                end   = datetime.datetime.strptime(self.parentArgs.until, "%Y-%m-%d").date()

                date += datetime.timedelta(days=1)

                while end >= date:
                    parts = date.strftime('%Y-%m-%d').split('-')
                    folders.append(parts[0] + '/' + parts[1] + '/' + parts[2])
                    date += datetime.timedelta(days=1)

        regex_empty_lines = re.compile(r'^\s*?\n', re.M)
        organizers = [TrashDetector(self.parentArgs.level), PlainDetector(self.parentArgs.level),
                      HashDetector(self.parentArgs.level)]

        features_handle = open(feature_path, 'w')
        features_writer = csv_DictWriter(features_handle, fieldnames=['trash', 'plain', 'hash', 'label', 'file'])
        features_writer.writerow({'trash': 'Trash score', 'plain': 'Plain score', 'hash': 'Hash score', 'label': 'Label', 'file': 'Filename'})

        dump_logger = getLogger('dumpscraper')

        for folder in folders:
            source = self.settings['data_dir'] + "/" + targetfolder + '/' + folder

            if not path.exists(source):
                dump_logger.info("Directory " + source + " does not exist!")
                continue

            dump_logger.info("Directory   : " + folder)

            for root, dirs, files in walk(source):
                for dump in files:
                    # If the force param is set, skip all the files that do not match
                    if self.parentArgs.force and self.parentArgs.force not in dump:
                        continue

                    with open(root + "/" + dump, 'r+') as handle:
                        data = handle.read()

                    # Remove /r since they could mess up regex
                    data = data.replace("\r", "")

                    # Let's count only the amount of non-empty lines
                    all_lines = data.count("\n")
                    empty_lines = len(re.findall(regex_empty_lines, data))

                    # Guess what? You need to pass a float during a division, otherwise Python will truncate the result
                    # For crying it loud!!!
                    lines = float(max(all_lines - empty_lines, 1))

                    info = {'data': data, 'lines': lines}
                    csvline = {}
                    results = {'trash': 0, 'plain': 0, 'hash': 0}

                    for organizer in organizers:
                        organizer.reset().setinfo(info).analyze(results)

                        score = min(organizer.score, 3)
                        csvline[organizer.returnkey()] = round(score, 4)
                        results[organizer.returnkey()] = round(score, 4)

                    label = path.basename(root)

                    if label == 'hash':
                        csvline['label'] = 1
                    elif label == 'plain':
                        csvline['label'] = 2
                    elif label == 'trash':
                        csvline['label'] = 0
                    else:
                        csvline['label'] = ''

                    # Let's remove the data dir from the path
                    file_path = root + '/' + dump

                    csvline['file'] = file_path.replace(self.settings['data_dir'] + '/' + targetfolder + '/', '')

                    features_writer.writerow(csvline)

        features_handle.close()
