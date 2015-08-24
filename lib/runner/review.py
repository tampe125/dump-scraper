__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import colorama
from os import path as os_path
from lib.exceptions.exceptions import RunningError
from lib.runner.abstract import AbstractCommand


class DumpScraperReview(AbstractCommand):
    def check(self):
        if not os_path.exists(self.settings['data_dir'] + "/" + 'organized'):
            raise RunningError(colorama.Fore.RED + "There aren't any organized dump files to process. Organize them before continuing.")

    def run(self):
        pass
