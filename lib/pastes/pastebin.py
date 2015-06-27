__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

from lib.pastes.abstract import AbstractPaste


class PastebinPaste(AbstractPaste):
    def __init__(self, paste_id):
        self.id = paste_id
        self.headers = None
        self.url = 'http://pastebin.com/raw.php?i=' + self.id
        super(PastebinPaste, self).__init__()