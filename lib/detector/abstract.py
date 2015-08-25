__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

from abc import ABCMeta, abstractmethod


class AbstractDetector:
    __metaclass__ = ABCMeta

    def __init__(self, level):
        self.score = 0
        self.data = ''
        self.lines = 0
        self.regex = {}

        self.level = level

    def reset(self):
        self.score = 0
        self.data  = ''

        return self

    def setinfo(self, features):
        for feature, value in features.iteritems():
            setattr(self, feature, value)

        return self

    @abstractmethod
    def analyze(self, results):
        pass

    @abstractmethod
    def returnkey(self):
        pass