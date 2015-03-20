__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

from abc import ABCMeta, abstractmethod


class AbstractCommand():
    __metaclass__ = ABCMeta

    def __init__(self, settings):
        self.settings = settings

    @abstractmethod
    def run(self):
        pass