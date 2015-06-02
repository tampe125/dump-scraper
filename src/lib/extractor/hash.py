__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import re
from lib.extractor.abstract import AbstractExtractor


class HashExtractor(AbstractExtractor):
    def __init__(self):
        super(HashExtractor, self).__init__()

        self.regex['phpass'] = re.compile(r'(\$P\$.{31})', re.M)
        self.regex['md5crypt'] = re.compile(r'(\$1\$.{8}\$.{22})', re.I | re.M)
        self.regex['phpassMd5'] = re.compile(r'(\$H\$9.{30})', re.M)
        self.regex['drupal'] = re.compile(r'(\$S\$.{52})', re.M)
        self.regex['mysql'] = re.compile(r'(\*[a-f0-9]{40})', re.I | re.M)
        self.regex['md5'] = re.compile(r'([a-f0-9]{32})', re.I | re.M)
        self.regex['crypt'] = re.compile(r'([a-z0-9/\.]{13})[,\s\n]?$', re.I | re.M)
        self.regex['sha1'] = re.compile(r'(\b[0-9a-f]{40}\b)', re.I | re.M)

    def analyze(self):
        data = ''

        for key, regex in self.regex.iteritems():
            data += self.extractdata(regex) + '\n'

        self.extracted = data

    def replacemateches(self, match):
        try:
            skip = False
            string = match.group(1)
            string = string.strip(' \t\n\r')

            # Is this a debug string?
            if string.count('000'):
                skip = True

            if not skip:
                self.matches.append(string)

        except IndexError:
            # Do nothing, there is no match
            pass

        return ''
