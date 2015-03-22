__author__ = 'tampe125'

from lib.detector.abstract import AbstractDetector


class PlainDetector(AbstractDetector):

    def analyze(self):
        pass

    def returnkey(self):
        return 'plain'