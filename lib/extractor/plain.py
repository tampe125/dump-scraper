# coding=utf-8
__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import re
from lib.extractor.abstract import AbstractExtractor


class PlainExtractor(AbstractExtractor):
    def __init__(self):
        super(PlainExtractor, self).__init__()

        # Keylogger output
        self.regex['keylogger_1'] = re.compile(r'program:.*?\nurl/host:.*?\nlogin:.*?\npassword:\s(.*?)\ncomputer:.*?\n', re.I)
        self.regex['keylogger_2'] = re.compile(r'software:.*?\nsitename:.*?\nlogin:.*?:(.*?)\npc name:.*?\n', re.I)
        # URL with passwords
        self.regex['urlPwd'] = re.compile(r'[ht|f]tp[s]*://\w+:(.*)@\w*\.\w*/')
        # Extracts data displayed in columns: Davison 	Yvonne 	library
        self.regex['columns'] = re.compile(r'^[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}\s?\t.*?\t.*?\t(.*?)$', re.I | re.M)
        # Standalone passwords
        self.regex['standalone'] = re.compile(r'pass(?:word)?\s*?[:|=](.*?$)', re.I | re.M)
        self.regex['standaloneES'] = re.compile(r'Contraseña\s*?[:|=](.*?$)', re.I | re.M)
        # email - password
        self.regex['emailPwd'] = re.compile(r'^"?[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}\s?[\-|/|;|:|\||,|\t]\s?(.*?)[,:\n"]', re.I | re.M)
        # password email
        self.regex['pwdEmail'] = re.compile(r'^(?!email)(?:.*?:)?(.*?)[\s|/|;|:|\||,|\t][a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}\s*?$', re.I | re.M)
        # username - password
        self.regex['md5'] = re.compile(r'^(?!http)[a-z0-9\-]{5,15}:(.*?)$', re.I | re.M)

        # Skip regexes
        self.skip_regex = {'email': re.compile(r'[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}', re.I),
                           'digits': re.compile(r'^\d+$')}

    def analyze(self):
        data = ''

        for key, regex in self.regex.iteritems():
            data += self.extractdata(regex) + '\n'

        data += self.mysqlInsertPlain()

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

            # Is it the "Username" label?
            if not skip:
                if string.lower() in ['user', 'correo']:
                    skip = True

            # Is it an email address?
            if not skip:
                if re.match(self.skip_regex['email'], string):
                    skip = True

            # Is this a numbers only password?
            if not skip:
                if re.match(self.skip_regex['digits'], string):
                    skip = True

            # If the skip flag is not set, let's add the string to the matches
            if not skip:
                self.matches.append(string)

        except IndexError:
            # Do nothing, there is no match
            pass

        return ''

    def mysqlInsertPlain(self):
        """
        Extracts a MySQL dump where the passwords are plain ones
        :return: ratio between lines and occurrences
        """

        # Ok, this is a thought  one, since we have to actually read and parse the whole file
        # Is this a dump file that I can handle?
        columns = re.findall(r'^INSERT INTO.*?\((.*?password.*?)\).*?$', self.data, re.M)

        if not len(columns):
            return ''

        try:
            columns = str(columns[0]).split(',')
            pwd_idx = [i for i, s in enumerate(columns) if 'password' in s][0]
        except IndexError:
            # The "password" field is not in the list
            return ''

        # Flag to know if I'm currently reading part of a query or simply reading garbage
        in_query = False
        matches = []

        # Ok, now I have the index of the password field, let's double check if these really are plain passwords
        for line in self.data.split("\n"):
            if 'INSERT' in line:
                in_query = True
                continue

            if not in_query:
                continue

            try:
                password = line.split(',')[pwd_idx]
            except IndexError:
                continue

            matches.append(password.strip("\t `'"))

            if ');' in line:
                in_query = False

        return '\n'.join(matches)
