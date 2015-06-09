# coding=utf-8
__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import re
from lib.detector.abstract import AbstractDetector


class PlainDetector(AbstractDetector):
    def __init__(self):
        super(PlainDetector, self).__init__()

        self.regex['emailPwd'] = re.compile(r'^[\s"]?[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}\s?[\-|/|;|:|\||,|\t].*?[:\n]', re.I | re.M)
        self.regex['txtEmail:pwd'] = re.compile(r'login:\s+[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}:.*?\n', re.I)
        self.regex['pwd'] = re.compile(r'pass(?:word)?\s*?[:|=].*?$', re.I | re.M)
        self.regex['pwdES'] = re.compile(r'Contraseña\s*?[:|=].*?$', re.I | re.M)
        self.regex['usrPwd'] = re.compile(r'[a-z0-9]{5,15}:.{1,10}$', re.I | re.M)
        self.regex['pwdEmail'] = re.compile(r'.{4,15}[\s|/|;|:|\||,|\t][a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}\s*?$', re.I | re.M)

    def analyze(self, results):
        # If the Trash Detector has an high value, don't process the file, otherwise we could end up with a false positive
        # Sadly some list of emails only could be very hard to separate from email - pwd files
        if results['trash'] >= 0.95:
            self.score = 0
            return

        score  = self.detectEmailPwd()
        score += self.detectPwdStandalone()
        score += self.detectUsernamePwd() * 0.75
        score += self.detectPwdEmails()

        self.score = score

    def returnkey(self):
        return 'plain'

    def detectEmailPwd(self):
        """
        Detects lists of email:password(:username)
        :return:
        """
        results = len(re.findall(self.regex['emailPwd'], self.data))

        return results / self.lines

    def detectPwdStandalone(self):
        """
        Detects password written as standalone
        Password      : foobar
        pass=foobar
        :return:
        """
        results  = len(re.findall(self.regex['pwd'], self.data))
        results += len(re.findall(self.regex['pwdES'], self.data))
        results += len(re.findall(self.regex['txtEmail:pwd'], self.data))

        return results / self.lines

    def detectUsernamePwd(self):
        """
        Detects lists of username:password
        :return:
        """
        results = len(re.findall(self.regex['usrPwd'], self.data))

        return results / self.lines

    def detectPwdEmails(self):
        results = len(re.findall(self.regex['pwdEmail'], self.data))

        return results / self.lines