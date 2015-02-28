__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import argparse
import textwrap
import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn import neighbors

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent('''
Dump Scraper - Training data chart

 This script will print out a chart showing the how the features are distribuited
'''))
parser.add_argument('-c', '--columns', help='Comma separated list of training columns that will be displayed', required=True)

args = parser.parse_args()

# Print banner
print("")
print("Dump Scraper - Training chart")
print("Copyright (C) 2015 FabbricaBinaria - Davide Tampellini")
print("===============================================================================")
print("Dump Scraper is Free Software, distributed under the terms of the GNU General")
print("Public License version 3 or, at your option, any later version.")
print("This program comes with ABSOLUTELY NO WARRANTY as per sections 15 & 16 of the")
print("license. See http://www.gnu.org/licenses/gpl-3.0.html for details.")
print("===============================================================================")
print("")

columns = map(int, args.columns.split(','))

if len(columns) != 2:
    print("You should pass only two columns at time")
    exit()

labels = []

for column in columns:
    if column > 2 or column < 0:
        print("Column value should be between 0 and 2")
        exit()

    if column == 0:
        labels.append('Trash')
    elif column == 1:
        folder = 'hash'
        labels.append('Hash')
    elif column == 2:
        labels.append('Plain')

'''
    Columns:
    0 - Trash
    1 - Plain
    2 - Hash
    3 - Label
    4 - Filename
'''
data = sp.genfromtxt("training/features.csv", delimiter=",", skip_header=1, usecols=columns)
target = sp.genfromtxt("training/features.csv", delimiter=",", skip_header=1, usecols=(-2))

n_neighbors = 10
h = .02  # step size in the mesh

cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])

clf = neighbors.KNeighborsClassifier(n_neighbors, weights='uniform')

clf.fit(data, target)

# Plot the decision boundary. For that, we will assign a color to each
# point in the mesh [x_min, m_max]x[y_min, y_max].
x_min, x_max = data[:, 0].min() - 1, data[:, 0].max() + 1
y_min, y_max = data[:, 1].min() - 1, data[:, 1].max() + 1

xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

# Put the result into a color plot
Z = Z.reshape(xx.shape)
plt.figure()
plt.pcolormesh(xx, yy, Z, cmap=cmap_light)

# Plot also the training points
plt.scatter(data[:, 0], data[:, 1], c=target, cmap=cmap_bold)
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
plt.title(labels[0] + " vs " + labels[1] + " (k = %i, weights = '%s')" % (n_neighbors, 'uniform'))

print "Printing chart..."

plt.show()

print "Operation completed"