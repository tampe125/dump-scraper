__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import re
from lib.extractor.abstract import AbstractExtractor


class PlainExtractor(AbstractExtractor):
    def __init__(self):
        super(PlainExtractor, self).__init__()

        # URL with passwords
        self.regex['urlPwd'] = re.compile(r'[ht|f]tp[s]*://\w+:(.*)@\w*\.\w*/')
        # Extracts data displayed in columns: Davison 	Yvonne 	library
        self.regex['columns'] = re.compile(r'^[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}\s?\t.*?\t.*?\t(.*?)$', re.I | re.M)
        # Standalone passwords
        self.regex['standalone'] = re.compile(r'pass(?:word)?\s*?[:|=](.*?$)', re.I | re.M)
        # email - password
        self.regex['emailPwd'] = re.compile(r'^"?[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}\s?[/|;|:|\||,|\t]\s?(.*?)[,:\n"]', re.I | re.M)
        # password email
        self.regex['pwdEmail'] = re.compile(r'^(?!email)(?:.*?:)?(.*?)[\s|/|;|:|\||,|\t][a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}\s*?$', re.I | re.M)
        # username - password
        self.regex['md5'] = re.compile(r'^(?!http)[a-z0-9\-]{5,15}:(.*?)$', re.I | re.M)

        # Skip regexes
        # Email address
        self.regex['email'] = re.compile(r'[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}', re.I)
        # Digits only
        self.regex['digits'] = re.compile(r'^\d+$')

    def analyze(self):
        data = ''

        for key, regex in self.regex.iteritems():
            data += self.extractdata(regex) + '\n'

        self.extracted = data

    def replacemateches(self, match):
        # Let's perform some sanity checks on the matched string
        try:
            skip = False
            string = match.group(1)
            string = string.strip(' \t\n\r')

            # Is it too long or too short?
            if len(string) > 20 or len(string) < 4:
                skip = True

            # Does it contain some wrong character?
            if not skip:
                chars = [' ', "\t", "\n"]

                for char in chars:
                    if char in string:
                        skip = True
                        break

            # Is it an email address?
            if not skip:
                if re.match(self.regex['email'], string):
                    skip = True

            # Is this a numbers only password?
            if not skip:
                if re.match(self.regex['digits'], string):
                    skip = True

            # If the skip flag is not set, let's add the string to the matches
            if not skip:
                self.matches.append(string)

        except IndexError:
            # Do nothing, there is no match
            pass

        return ''