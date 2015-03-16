__author__ = 'tampe125'

import os
import csv
import scipy as sp
import shutil
from sklearn import neighbors

# Print banner
print("")
print("Dump Scraper - Classify dump files")
print("Copyright (C) 2015 FabbricaBinaria - Davide Tampellini")
print("===============================================================================")
print("Dump Scraper is Free Software, distributed under the terms of the GNU General")
print("Public License version 3 or, at your option, any later version.")
print("This program comes with ABSOLUTELY NO WARRANTY as per sections 15 & 16 of the")
print("license. See http://www.gnu.org/licenses/gpl-3.0.html for details.")
print("===============================================================================")
print("")

__DIR__ = os.path.dirname(os.path.realpath(__file__))
dir_organized = __DIR__ + "/data/organized/"

if not os.path.exists(__DIR__ + "/training/features.csv"):
    print("Training data not found. Please collect some training data and calculate its score")
    print("then run again this script.")
    print("")
    exit()

if not os.path.exists(__DIR__ + "/data/raw/features.csv"):
    print("Score data not found. Please calculate the score of the collected data,")
    print("then run again this script.")
    print("")
    exit()

training = sp.genfromtxt(__DIR__ + "/training/features.csv", delimiter=",", skip_header=1, usecols=(0, 1, 2))
target = sp.genfromtxt(__DIR__ + "/training/features.csv", delimiter=",", skip_header=1, usecols=(-2))

n_neighbors = 10

# Let's load the training data into the classifier
clf = neighbors.KNeighborsClassifier(n_neighbors, weights='uniform')
clf.fit(training, target)

trash_count = hash_count = plain_count = 0

with open(__DIR__ + "/data/raw/features.csv", 'rb') as csvfile:
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

        target_dir = dir_organized + folder + "/" + line[-1]

        if not os.path.exists(os.path.dirname(target_dir)):
            os.makedirs(os.path.dirname(target_dir))

        shutil.copyfile(__DIR__ + "/data/raw/" + line[-1], target_dir)

print("Trash files: " + str(trash_count))
print("Hash files: " + str(hash_count))
print("Plain files: " + str(plain_count))
print("Operation completed")
