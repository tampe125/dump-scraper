__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import colorama
import random
import os
import shutil

from lib.runner.abstract import AbstractCommand
from lib.exceptions.exceptions import RunningError
from lib.runner import getscore
from lib.utils.terminalsize import get_terminal_size

class DumpScraperTraining(AbstractCommand):
    def check(self):
        if not os.path.exists('data/raw'):
            raise RunningError(colorama.Fore.RED + "There aren't any dump files to process. Scrape them before continuing.")

        if not os.path.exists('data/training'):
            os.makedirs('data/training')
        if not os.path.exists('data/training/hash'):
            os.makedirs('data/training/hash')
        if not os.path.exists('data/training/plain'):
            os.makedirs('data/training/plain')
        if not os.path.exists('data/training/trash'):
            os.makedirs('data/training/trash')

    def run(self):
        if self.parentArgs.getdata:
            self._gettrainingdata()
        else:
            self._getscore()

    def _gettrainingdata(self):
        files = [os.path.join(path, filename)
                 for path, dirs, files in os.walk('data/raw')
                 for filename in files
                 if not filename.endswith(".csv")]
        while 1:
            rfile = random.choice(files)

            trash  = len(os.listdir('data/training/trash'))
            plain  = len(os.listdir('data/training/plain'))
            hashes = len(os.listdir('data/training/hash'))

            # Clear the screen before displaying the text
            os.system('cls' if os.name == 'nt' else 'clear')

            # Let's the terminal size, so I can fill it with the file text
            cols, rows = get_terminal_size()

            print colorama.Fore.YELLOW + rfile
            print("")

            with open(rfile) as tfile:
                i = 0
                for line in tfile:
                    i += 1
                    if i >= (rows - 4):
                        break

                    if len(line) <= cols:
                        print line.strip('\n\r')
                    else:
                        print line[0:cols].strip('\n\r')

            print("")
            print colorama.Fore.YELLOW + "Trash: " + str(trash) + " Plain: " + str(plain) + " Hash: " + str(hashes)

            input_descr = colorama.Fore.MAGENTA + "[t]"
            input_descr += colorama.Fore.CYAN + "rash "
            input_descr += colorama.Fore.MAGENTA + "[p]"
            input_descr += colorama.Fore.CYAN + "lain "
            input_descr += colorama.Fore.MAGENTA + "[h]"
            input_descr += colorama.Fore.CYAN + "ash "
            input_descr += colorama.Fore.MAGENTA + "[s]"
            input_descr += colorama.Fore.CYAN + "kip "
            input_descr += colorama.Fore.MAGENTA + "[q]"
            input_descr += colorama.Fore.CYAN + "uit=> "

            answer = raw_input(input_descr)

            if answer == 't':
                shutil.copyfile(rfile, 'data/training/trash/' + os.path.basename(rfile))
            elif answer == 'p':
                shutil.copyfile(rfile, 'data/training/plain/' + os.path.basename(rfile))
            elif answer == 'h':
                shutil.copyfile(rfile, 'data/training/hash/' + os.path.basename(rfile))
            elif answer == 's':
                print("")
                continue
            elif answer == 'q':
                print("")
                print(colorama.Fore.GREEN + "Training complete")
                break
            else:
                print("")
                continue

    def _getscore(self):
        # Let's invoke the getscore runner and tell him to work on training data
        running = getscore.DumpScraperGetscore(self.settings, self.parentArgs)
        running.run(training=True)