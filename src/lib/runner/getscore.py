__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import os
import datetime
import csv
import sys
import re
from lib.detector.trash import TrashDetector
from lib.detector.hash import HashDetector
from lib.runner.abstract import AbstractCommand
from lib.detector.plain import PlainDetector
from lib.exceptions.exceptions import RunningError


class DumpScraperGetscore(AbstractCommand):
    def check(self):
        if not os.path.exists('data/raw'):
            raise RunningError("There aren't any dump files to process. Scrape them before continuing.")

    def run(self, **keyargs):
        if 'training' in keyargs and keyargs['training']:
            targetfolder = 'training'
            folders = ['trash', 'hash', 'plain']
        else:
            targetfolder = 'raw'
            folders = [self.parentArgs.since]

            if self.parentArgs.until:
                date  = datetime.datetime.strptime(self.parentArgs.since, "%Y-%m-%d").date()
                end   = datetime.datetime.strptime(self.parentArgs.until, "%Y-%m-%d").date()

                date += datetime.timedelta(days=1)

                while end >= date:
                    folders.append(date.strftime('%Y-%m-%d'))
                    date += datetime.timedelta(days=1)

        regex_empty_lines = re.compile(r'^\n', re.M)
        organizers = [TrashDetector(), PlainDetector(), HashDetector()]

        features_handle = open('data/' + targetfolder + '/features.csv', 'w')
        features_writer = csv.DictWriter(features_handle, fieldnames=['trash', 'plain', 'hash', 'label', 'file'])
        features_writer.writerow({'trash': 'Trash score', 'plain': 'Plain score', 'hash': 'Hash score', 'label': 'Label', 'file': 'Filename'})

        for folder in folders:
            source = 'data/' + targetfolder + '/' + folder

            if not os.path.exists(source):
                print("Directory " + source + " does not exist!")
                print("")
                continue

            print("Directory   : " + folder)

            for root, dirs, files in os.walk(source):
                for dump in files:
                    sys.stdout.write('.')
                    sys.stdout.flush()

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

                    label = os.path.basename(root)

                    if label == 'hash':
                        csvline['label'] = 1
                    elif label == 'plain':
                        csvline['label'] = 2
                    elif label == 'trash':
                        csvline['label'] = 0
                    else:
                        csvline['label'] = ''

                    csvline['file'] = os.path.basename(root) + "/" + dump

                    features_writer.writerow(csvline)

            print("")

        features_handle.close()
        print("")


