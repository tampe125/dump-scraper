__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import os
import csv
import scipy
import shutil
import sklearn.neighbors
import colorama
from lib.runner.abstract import AbstractCommand
from lib.exceptions.exceptions import RunningError
from lib.runner import getscore


class DumpScraperClassify(AbstractCommand):
    def check(self):
        if not os.path.exists('data/training/features.csv'):
            raise RunningError(colorama.Fore.RED + "Training score was not calculated. Do it and then run this command again"
                               + colorama.Fore.RESET)

        if not os.path.exists('data/organized'):
            os.makedirs('data/organized')
        if not os.path.exists('data/organized/hash'):
            os.makedirs('data/organized/hash')
        if not os.path.exists('data/organized/plain'):
            os.makedirs('data/organized/plain')
        if not os.path.exists('data/organized/trash'):
            os.makedirs('data/organized/trash')

    def run(self):
        # Let's invoke the getscore runner and tell him to work on training data
        print("Calculating dump score...")
        running = getscore.DumpScraperGetscore(self.settings, self.parentArgs)
        running.run()

        # First of all let's feed the classifier with the training data
        training = scipy.genfromtxt("data/training/features.csv", delimiter=",", skip_header=1, usecols=(0, 1, 2))
        target = scipy.genfromtxt("data/training/features.csv", delimiter=",", skip_header=1, usecols=(-2))

        clf = sklearn.neighbors.KNeighborsClassifier(10, weights='uniform')
        clf.fit(training, target)

        trash_count = hash_count = plain_count = 0

        with open('data/raw/features.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)

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

                target_dir = 'data/organized/' + folder + "/" + line[-1]

                if not os.path.exists(os.path.dirname(target_dir)):
                    os.makedirs(os.path.dirname(target_dir))

                shutil.copyfile('data/raw/' + line[-1], target_dir)

        print("Trash files: " + str(trash_count))
        print("Hash files: " + str(hash_count))
        print("Plain files: " + str(plain_count))
        print("Operation completed")
