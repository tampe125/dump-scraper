__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import re
from lib.detector.abstract import AbstractDetector


class TrashDetector(AbstractDetector):
    def __init__(self):
        self.functions = {
            'fewLines'         : 1,
            'longLines'        : 1,
            'privateKeys'      : 1,
            'antivirusDump'    : 1,
            'detectRawEmail'   : 1,
            'detectEmailsOnly' : 1,
            'detectDebug'      : 1.2,
            'detectIP'         : 1.5,
            'detectTimeStamps' : 1,
            'detectHtml'       : 1,
            'detectVarious'    : 1
        }

        super(TrashDetector, self).__init__()

        # Let's compile some regexes to speed up the execution
        self.regex['emailsOnly'] = re.compile('^[\s"]?[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}[\s|\t]?$', re.I | re.M)
        self.regex['debugHex'] = re.compile('0x[a-f0-9]{8}', re.I)
        self.regex['winPath'] = re.compile('[A-Z]:\\\.*?\\\.*?\\\\', re.M)

        # Chat log 330e8f8887e4ea04b06a6cffc66cfce0 -1 Admin Ban G-SH
        self.regex['chat'] = re.compile('[a-f0-9]{32} -\d')

        self.regex['mysqlTable'] = re.compile('\+-{10,}?\+', re.M)
        self.regex['startingDigits'] = re.compile('^\d{1,4},', re.M)
        self.regex['mysqlDates'] = re.compile('(19|20)\d\d[\-/.](0[1-9]|1[012])[\-/.](0[1-9]|[12][0-9]|3[01])')
        self.regex['engDates'] = re.compile('(0[1-9]|1[012])[\-/.](0[1-9]|[12][0-9]|3[01])[\-/.](19|20)\d\d')
        self.regex['time'] = re.compile('(?:2[0-3]|[01][0-9]):[0-5][0-9](?::[0-5][0-9])?')
        self.regex['htmlTags'] = re.compile('</?(?:html|div|p|div|script|link|span|u|ul|li|ol|a)+\s*/?>', re.I)
        self.regex['htmlLinks'] = re.compile('\b(?:(?:https?|udp)://|www\.)[-A-Z0-9+&@#/%=~_|$?!:,.]*[A-Z0-9+&@#/%=~_|$]', re.I)
        self.regex['md5links'] = re.compile('(?:(?:https?|udp)://|www\.)[-A-Z0-9+&@#/%=~_|$?!:,.]*[A-Z0-9+&@#/%=~_|$]=[a-f0-9]{32}', re.I)

    def analyze(self, results):
        for function, coefficient in self.functions.iteritems():
            self.score += getattr(self, function)() * coefficient

            if self.score >= 3:
                break

    def returnkey(self):
        return 'trash'

    def fewLines(self):
        # If I just have few lines, most likely it's trash. I have to do this since sometimes some debug output are
        # crammed into a single line, screwing up all the stats
        if self.lines < 3:
            return 3

        return 0

    def longLines(self):
        """
        Files with huge lines are debug info
        :return:
        """
        # This is a special case: porn passwords usually have tons of keywords and long lines (4k+)
        # Let's manually add an exception for those files and hope for the best
        if self.data.count('XXX Porn Passwords') > 0:
            return 0

        lines = self.data.split("\n")

        for line in lines:
            if len(line) > 1000:
                return 3

        return 0

    def privateKeys(self):
        """
        RSA private keys
        :return:
        """
        if self.data.count('---BEGIN') > 0:
            return 3

        return 0

    def antivirusDump(self):
        signatures = ['Malwarebytes Anti-Malware', 'www.malwarebytes.org']

        for signature in signatures:
            if self.data.lower().count(signature.lower()) > 0:
                return 3

        return 0

    def detectRawEmail(self):
        """
        Detects emails in "raw mode"
        :return:
        """
        if self.data.count('Content-Type:') > 0:
            return 3

        return 0

    def detectEmailsOnly(self):
        """
        Detect full list of email addresses only, useless for us
        :return:
        """
        emails = re.findall(self.regex['emailsOnly'], self.data)

        return len(emails) / self.lines

    def detectDebug(self):
        """
        Files with debug info
        :return: float
        """
        data_lower = self.data.lower()

        # Windows paths
        score = len(re.findall(self.regex['winPath'], self.data))
        score += len(re.findall(self.regex['debugHex'], self.data))

        # Windows register keys
        score += data_lower.count('hklm\\')
        score += data_lower.count('debug')
        score += data_lower.count('[trace]')
        score += data_lower.count('session')
        score += data_lower.count('class=')
        score += data_lower.count('thread')
        score += data_lower.count('uuid')

        score += len(re.findall(self.regex['chat'], self.data))

        return score / self.lines

    def detectIP(self):
        """
        Files with IP most likely are access log files
        :return:
        """
        multiplier = 1

        # Do I have a table dump? If so I have to lower the score
        insert = self.data.count('INSERT INTO')
        mysql  = len(re.findall(self.regex['mysqlTable'], self.data))

        # Do I have lines starting with a number? Maybe it's a table dump without any MySQL markup
        digits = len(re.findall(self.regex['startingDigits'], self.data)) / self.lines

        if insert > 3 or mysql > 5 or digits > 0.25:
            multiplier = 0.01

        ip = len(re.findall(self.regex['ip'], self.data)) * multiplier

        return ip / self.lines

    def detectTimeStamps(self):
        """
        Files with a lot of timestamps most likely are log files
        :return:
        """
        multiplier = 1

        # Do I have a table dump? If so I have to lower the score of the timestamps, since most likely it's the creation time
        insert = self.data.count('INSERT INTO')
        mysql  = len(re.findall(self.regex['mysqlTable'], self.data))

        # Do I have lines starting with a number? Maybe it's a table dump without any MySQL markup
        digits = len(re.findall(self.regex['startingDigits'], self.data)) / self.lines

        if insert > 3 or mysql > 5 or digits > 0.25:
            multiplier = 0.01

        # MySQL dates - 2015-11-02
        dates = len(re.findall(self.regex['mysqlDates'], self.data)) * multiplier
        score = dates / self.lines

        # English dates - 11-25-2015
        dates = len(re.findall(self.regex['engDates'], self.data)) * multiplier
        score += dates / self.lines

        # Search for the time only if the previous regex didn't match anything.
        # Otherwise I'll count timestamps YYYY-mm-dd HH:ii:ss twice
        if score < 0.01:
            time = len(re.findall(self.regex['time'], self.data)) * multiplier
            score += time / self.lines

        return score

    def detectHtml(self):
        """
        HTML tags in the file, most likely garbage
        :return:
        """
        # HTML tags (only the most used ones are here)
        score = len(re.findall(self.regex['htmlTags'], self.data)) * 1.5

        # Links
        score += len(re.findall(self.regex['htmlLinks'], self.data)) * 0.5

        # Links containing md5 hash
        score += len(re.findall(self.regex['md5links'], self.data))

        return score / self.lines

    def detectVarious(self):
        score = self.data.lower().count('e-mail found')

        return score / self.lines