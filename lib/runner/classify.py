__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import sklearn.neighbors
import colorama
from csv import reader as csv_reader
from os import path, makedirs
from scipy import genfromtxt as scipy_genfromtxt
from shutil import copyfile as shutil_copyfile
from lib.runner.abstract import AbstractCommand
from lib.exceptions.exceptions import RunningError
from lib.runner import getscore


class DumpScraperClassify(AbstractCommand):
    def check(self):
        if not path.exists(self.settings['data_dir'] + "/" + 'training/features.csv'):
            raise RunningError(colorama.Fore.RED + "Training score was not calculated. Do it and then run this command again")

        if not path.exists(self.settings['data_dir'] + "/" + 'organized'):
            makedirs(self.settings['data_dir'] + "/" + 'organized')
        if not path.exists(self.settings['data_dir'] + "/" + 'organized/hash'):
            makedirs(self.settings['data_dir'] + "/" + 'organized/hash')
        if not path.exists(self.settings['data_dir'] + "/" + 'organized/plain'):
            makedirs(self.settings['data_dir'] + "/" + 'organized/plain')
        if not path.exists(self.settings['data_dir'] + "/" + 'organized/trash'):
            makedirs(self.settings['data_dir'] + "/" + 'organized/trash')

    def run(self):
        # Let's invoke the getscore runner and tell him to work on training data
        print("Calculating dump score...")
        running = getscore.DumpScraperGetscore(self.settings, self.parentArgs)
        running.run()

        # First of all let's feed the classifier with the training data
        training = scipy_genfromtxt(self.settings['data_dir'] + "/" + "training/features.csv", delimiter=",", skip_header=1, usecols=(0, 1, 2))
        target = scipy_genfromtxt(self.settings['data_dir'] + "/" + "training/features.csv", delimiter=",", skip_header=1, usecols=(-2))

        clf = sklearn.neighbors.KNeighborsClassifier(10, weights='uniform')
        clf.fit(training, target)

        trash_count = hash_count = plain_count = 0

        with open(self.settings['data_dir'] + "/" + 'raw/features.csv', 'rb') as csvfile:
            reader = csv_reader(csvfile)

            for line in reader:
                if line[0] == 'Trash score':
                    continue

                features = line[0:3]
                label = clf.predict(features)

                if label == 0:
                    folder = 'trash'
                    trash_count += 1
                elif label == 1:
                    folder = 'hash'
                    hash_count += 1
                elif label == 2:
                    folder = 'plain'
                    plain_count += 1

                target_dir = self.settings['data_dir'] + "/" + 'organized/' + folder + "/" + line[-1]

                if not path.exists(path.dirname(target_dir)):
                    makedirs(path.dirname(target_dir))

                shutil_copyfile(self.settings['data_dir'] + "/" + 'raw/' + line[-1], target_dir)

        print("Trash files: " + str(trash_count))
        print("Hash files: " + str(hash_count))
        print("Plain files: " + str(plain_count))
        print("Operation completed")
