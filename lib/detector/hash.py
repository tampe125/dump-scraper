__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import re
from lib.detector.abstract import AbstractDetector


class HashDetector(AbstractDetector):
    def __init__(self, level):
        super(HashDetector, self).__init__(level)

        from collections import OrderedDict

        # Order MATTERS! Functions to detect false positives MUST BE executed first
        self.functions = OrderedDict()

        if self.level >= 1:
            self.functions['fewLines']      = 1
            self.functions['longLines']     = 1
            self.functions['hashPlain']     = 1
            self.functions['detectMd5']     = 1
            self.functions['detectMd5Crypt'] = 1
            self.functions['detectMd5Apache'] = 1
            self.functions['detectSha512Crypt'] = 1
            self.functions['phpassMd5']     = 1
            self.functions['phpassGen']     = 1
            self.functions['detectSha1']    = 1
            self.functions['detectMySQL']   = 1
            self.functions['detectMySQLOrig'] = 1
            self.functions['detectDrupal']  = 1
            self.functions['detectBlowfish'] = 1

        if self.level >= 2:
            pass

        if self.level >= 3:
            self.functions['detectCrypt']   = 1

        # Let's compile some regexes to speed up the execution
        self.regex['md5'] = re.compile(r'[a-f0-9]{32}')
        # Example $apr1$bHcedXBW$rdg78bAXeX0ndndEPgMY/.
        self.regex['md5Apache'] = re.compile(r'\$apr1\$.{8}\$.{22}')
        # Example (unsalted) $1$sCGfZOwq$K9M3ULuacSQln/e3/KnPN.
        self.regex['md5Crypt'] = re.compile(r'\$1\$.{8}\$.{22}', re.I | re.M)
        self.regex['sha512Crypt'] = re.compile(r'\$6\$[a-z0-9./]{8}\$[a-z0-9./]+', re.I | re.M)
        # Example $H$9V1cX/WqUhsSWM0ipyB7HwFQqTQKxP1
        self.regex['phpassMd5'] = re.compile(r'\$H\$9.{30}', re.M)
        # Example $P$B52zg0z/Y5e96IpD4KJ7a9ByqcrKb01
        self.regex['phpassGen'] = re.compile(r'\$P\$.{31}', re.M)
        self.regex['sha1'] = re.compile(r'\b[0-9a-f]{40}\b', re.I | re.M)
        self.regex['mysql'] = re.compile(r'\*[a-f0-9]{40}', re.I | re.M)
        self.regex['mysqlOrig'] = re.compile(r'[a-f0-9]{16}')
        self.regex['crypt'] = re.compile(r'[\s\t:][a-zA-Z0-9/\.]{13}[,\s\n]?$', re.M)
        # Drupal $S$DugG4yZmhfIGhNJJZMzKzh4MzOCkpsPBR9HtDIvqQeIyqLM6wyuM
        self.regex['drupal'] = re.compile(r'\$S\$[a-zA-Z0-9/\.]{52}', re.M)
        self.regex['blowfish'] = re.compile(r'\$2[axy]?\$[a-zA-Z0-9./]{8}\$[a-zA-Z0-9./]+', re.M)

    def analyze(self, results):
        # If the Trash Detector has an high value, don't process the file, otherwise we could end up with a false positive
        # Sadly debug files LOVE to use hashes...
        if results['trash'] >= 0.95:
            self.score = 0
            return
        
        for function, coefficient in self.functions.iteritems():
            score = getattr(self, function)() * coefficient
            
            # Did I get a negative score? This means that this file is NOT an hash one!
            # Set the global score to 0 and stop here
            if score < 0:
                self.score = 0
                break
                
            self.score += score
            
            # I already reached the maximum value, there's no point in continuing
            if self.score >= 3:
                break

    def returnkey(self):
        return 'hash'

    def fewLines(self):
        # If I just have few lines, most likely it's trash. I have to do this since sometimes some debug output are
        # crammed into a single line, screwing up all the stats
        if self.lines < 3:
            return -1
        
        return 0
    
    def longLines(self):
        lines = self.data.split("\n")

        for line in lines:
            if len(line) > 1000:
                return -1

        return 0

    def hashPlain(self):
        """
        Do I have a hash:plain pair? If so this is a plain file, not an hash one!
        """
        # Let's check for some VERY common password
        fakeHash = len(re.findall(r'[a-f0-9]{32}:password', self.data, re.I | re.M))
        fakeHash += len(re.findall(r'[a-f0-9]{32}:123456', self.data, re.I | re.M))

        if fakeHash:
            return -1

        return 0

    def detectMd5(self):
        hashes = len(re.findall(self.regex['md5'], self.data))

        return hashes / self.lines

    def detectMd5Crypt(self):
        hashes = len(re.findall(self.regex['md5Crypt'], self.data))

        return hashes / self.lines

    def detectMd5Apache(self):
        hashes = len(re.findall(self.regex['md5Apache'], self.data))

        return hashes / self.lines

    def detectSha512Crypt(self):
        hashes = len(re.findall(self.regex['sha512Crypt'], self.data))

        return hashes / self.lines

    def phpassMd5(self):
        hashes = len(re.findall(self.regex['phpassMd5'], self.data))

        return hashes / self.lines

    def phpassGen(self):
        hashes = len(re.findall(self.regex['phpassGen'], self.data))

        return hashes / self.lines

    def detectSha1(self):
        hashes = len(re.findall(self.regex['sha1'], self.data))

        return hashes / self.lines

    def detectMySQL(self):
        hashes = len(re.findall(self.regex['mysql'], self.data))

        return hashes / self.lines

    def detectMySQLOrig(self):
        hashes = len(re.findall(self.regex['mysqlOrig'], self.data))

        return hashes / self.lines

    def detectCrypt(self):
        # Sadly the crypt hash is very used and has a very common signature, this means that I can't simply search for it
        # in the whole document, or I'll have TONS of false positive. I have to shrink the range using more strict regex
        hashes = len(re.findall(self.regex['crypt'], self.data))

        return hashes / self.lines

    def detectDrupal(self):
        hashes = len(re.findall(self.regex['drupal'], self.data))

        return hashes / self.lines

    def detectBlowfish(self):
        hashes = len(re.findall(self.regex['blowfish'], self.data))

        return hashes / self.lines