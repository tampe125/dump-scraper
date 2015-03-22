__author__ = 'tampe125'
from lib.detector.abstract import AbstractDetector


class TrashDetector(AbstractDetector):

    def analyze(self):
        pass

    def returnkey(self):
        return 'trash'