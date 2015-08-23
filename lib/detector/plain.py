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
        self.regex['insertPlain'] = re.compile(r'^INSERT INTO.*?\((.*?password.*?)\).*?$', re.M)
        self.regex['sqlmap'] = re.compile(r'\[INFO\] (cracked|resuming) password', re.I)
        self.regex['keylogger_1'] = re.compile(r'program:.*?\nurl/host:.*?\nlogin:.*?\npassword:.*?\ncomputer:.*?\n', re.I)
        self.regex['keylogger_2'] = re.compile(r'software:.*?\nsitename:.*?\nlogin:.*?\npc name:.*?\n', re.I)

        # Bulgarian keylogger, I have to add the ??? form since sometimes the encoding is screwed up
        bg_regex  = r'(/Аккаунт/|Дата Рождения|Дата создания|Дата редактирования|Страна)'
        bg_regex += r'|(/\?\?\?\?\?\?\?/|\?\?\?\? \?\?\?\?\?\?\?\?|\?\?\?\? \?\?\?\?\?\?\?\?|\?\?\?\? \?\?\?\?\?\?\?\?\?\?\?\?\?\?|\?\?\?\?\?\?)'

        self.regex['keylogger_bg'] = re.compile(bg_regex, re.I)

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
        score += self.mysqlInsertPlain()
        score += self.detectBulgarianKeylogger()
        score += self.detectKeylogger1()
        score += self.detectKeylogger2()
        score += self.detectSqlMap()

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

    def mysqlInsertPlain(self):
        """
        Detects a MySQL dump where the passwords are plain ones
        :return: ratio between lines and occurrences
        """

        # Ok, this is a thought  one, since we have to actually read and parse the whole file
        # Is this a dump file that I can handle?
        columns = re.findall(self.regex['insertPlain'], self.data)
        if not len(columns):
            return 0

        try:
            columns = str(columns[0]).split(',')
            pwd_idx = [i for i, s in enumerate(columns) if 'password' in s][0]
        except IndexError:
            # The "password" field is not in the list
            return 0

        # Flag to know if I'm currently reading part of a query or simply reading garbage
        in_query = False
        pwd_counter = 0
        counter = 0

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

            counter += 1

            # Most likey plain password have "123" inside them
            if '123' in password:
                pwd_counter += 1

            if ');' in line:
                in_query = False

        # Did I hit enough possible passwords?
        if pwd_counter > 10:
            return counter / self.lines

        return 0

    def detectKeylogger1(self):
        """
        Detects keylogger output in the form

        Program: Google Chrome
        Url/Host: xxx
        Login: xxx
        Password: xxx
        Computer: xxx

        :return: ratio between occurrences and lines
        """
        # I have to multiply the result by 5, since every occurrence spans on 5 lines
        results = len(re.findall(self.regex['keylogger_1'], self.data)) * 5

        return results / self.lines

    def detectKeylogger2(self):
        """
        Detects keylogger output in the form

        Software:	Chrome
        Sitename:	xxx
        Login:		xxx:xxx
        PC Name:	xxx

        :return: ratio between occurrences and lines
        """
        # I have to multiply the result by 4, since every occurrence spans on 4 lines
        results = len(re.findall(self.regex['keylogger_2'], self.data)) * 4

        return results / self.lines

    def detectBulgarianKeylogger(self):
        """
        Detects keylogger output in the form

        ========/Аккаунт/========
        email:password
        ========/Аккаунт/========
        Дата Рождения: xxx
        Дата создания: xxx
        Дата редактирования: xxx
        Страна: XX

        :return: ratio between occurrences and lines
        """
        results = len(re.findall(self.regex['keylogger_bg'], self.data))

        return results / self.lines

    def detectSqlMap(self):
        """
        Detects SQLmap output of cracked passwords:

        [INFO] cracked password '050582' for hash '70a03af219d66bad60a764d0f1e25520'

        :return: ratio between occurrences and lines
        """
        results = len(re.findall(self.regex['sqlmap'], self.data))

        return results / self.lines
