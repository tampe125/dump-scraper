__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from logging import getLogger

class AbstractDetector:
    __metaclass__ = ABCMeta

    def __init__(self, level):

        # Order MATTERS! Functions to detect false positives MUST BE executed first
        self.functions = OrderedDict()
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

    def logfunctions(self):
        dump_logger = getLogger('dumpscraper')

        dump_logger.debug('\t' + self.returnkey().capitalize() + " detector setup")
        dump_logger.debug("\tThe following rules will be applied:")

        for name in self.functions:
            dump_logger.debug('\t\t' + name)
            descr = getattr(self, name).__doc__

            if descr is not None:
                descr = descr.strip(' \n\t')

                if descr:
                    descr = descr.split(':return:')
                    descr = descr[0].strip(' \n\t').split('\n')
                    for row in descr:
                        dump_logger.debug('\t\t\t' + row.strip(' \n\t'))

    @abstractmethod
    def analyze(self, results):
        pass

    @abstractmethod
    def returnkey(self):
        pass
