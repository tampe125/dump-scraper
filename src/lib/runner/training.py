__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import random
import os
import shutil

from lib.runner.abstract import AbstractCommand
from lib.exceptions.exceptions import RunningError


class DumpScraperTraining(AbstractCommand):
    def check(self):
        if not os.path.exists('data/raw'):
            raise RunningError("There aren't any dump files to process. Scrape them before continuing.")

        if not os.path.exists('data/training'):
            os.makedirs('data/training')
        if not os.path.exists('data/training/hash'):
            os.makedirs('data/training/hash')
        if not os.path.exists('data/training/plain'):
            os.makedirs('data/training/plain')
        if not os.path.exists('data/training/trash'):
            os.makedirs('data/training/trash')

    def run(self):
        if self.parentArgs.getdata:
            self._gettrainingdata()
            return

    def _gettrainingdata(self):
        files = [os.path.join(path, filename)
                 for path, dirs, files in os.walk('data/raw')
                 for filename in files
                 if not filename.endswith(".csv")]
        while 1:
            rfile = random.choice(files)

            with open(rfile) as tfile:
                i = 0
                for line in tfile:
                    i += 1
                    if i >= 20:
                        break

                    if len(line) <= 80:
                        print line.strip('\n\r')
                    else:
                        print line[0:80].strip('\n\r')

            print("")
            print rfile
            answer = raw_input("[t]rash [p]lain [h]ash [s]kip [q]uit=> ")

            if answer == 't':
                shutil.copyfile(rfile, 'data/training/trash/' + os.path.basename(rfile))
            elif answer == 'p':
                shutil.copyfile(rfile, 'data/training/plain/' + os.path.basename(rfile))
            elif answer == 'h':
                shutil.copyfile(rfile, 'data/training/hash/' + os.path.basename(rfile))
            elif answer == 's':
                print("")
                continue
            elif answer == 'q':
                print("")
                print("Training complete")
                break
            else:
                print("")
                continue