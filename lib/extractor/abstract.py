__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import re
from abc import ABCMeta, abstractmethod


class AbstractExtractor():
    __metaclass__ = ABCMeta

    def __init__(self):
        from collections import OrderedDict

        self.data = ''
        self.extracted = ''
        self.matches = []
        self.regex = OrderedDict()

    def reset(self):
        self.data = ''
        self.extracted = ''

        return self

    def setinfo(self, features):
        for feature, value in features.iteritems():
            setattr(self, feature, value)

        return self

    @abstractmethod
    def analyze(self):
        pass

    def extractdata(self, regex):
        self.matches = []

        self.data = re.sub(regex, self.replacemateches, self.data)

        return '\n'.join(self.matches)

    @abstractmethod
    def replacemateches(self, match):
        pass
