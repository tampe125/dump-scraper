__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import colorama
from os import path, makedirs, walk, listdir, system, name
from platform import system as platform_system
from random import choice as random_choice
from shutil import copyfile as shutil_copyfile
from subprocess import call as subprocess_call
from sys import stdout as sys_stdout
from lib.runner.abstract import AbstractCommand
from lib.exceptions.exceptions import RunningError
from lib.runner import getscore
from lib.utils.terminalsize import get_terminal_size
from lib.utils.getch import getch


class DumpScraperTraining(AbstractCommand):
    def check(self):
        if not path.exists(self.settings['data_dir'] + "/" + 'raw'):
            raise RunningError("There aren't any dump files to process. Scrape them before continuing.")

        if not path.exists(self.settings['data_dir'] + "/" + 'training'):
            makedirs(self.settings['data_dir'] + "/" + 'training')
        if not path.exists(self.settings['data_dir'] + "/" + 'training/hash'):
            makedirs(self.settings['data_dir'] + "/" + 'training/hash')
        if not path.exists(self.settings['data_dir'] + "/" + 'training/plain'):
            makedirs(self.settings['data_dir'] + "/" + 'training/plain')
        if not path.exists(self.settings['data_dir'] + "/" + 'training/trash'):
            makedirs(self.settings['data_dir'] + "/" + 'training/trash')

    def run(self):
        if self.parentArgs.getdata:
            self._gettrainingdata()
        else:
            self._getscore()

    def _gettrainingdata(self):
        files = [path.join(w_path, filename)
                 for w_path, dirs, files in walk(self.settings['data_dir'] + "/" + 'raw')
                 for filename in files
                 if not filename.endswith(".csv")]
        while 1:
            rfile = random_choice(files)

            trash  = len(listdir(self.settings['data_dir'] + "/" + 'training/trash'))
            plain  = len(listdir(self.settings['data_dir'] + "/" + 'training/plain'))
            hashes = len(listdir(self.settings['data_dir'] + "/" + 'training/hash'))

            # Clear the screen before displaying the text
            system('cls' if name == 'nt' else 'clear')

            # Let's the terminal size, so I can fill it with the file text
            cols, rows = get_terminal_size()

            print colorama.Fore.YELLOW + rfile
            print("")

            with open(rfile) as tfile:
                i = 0
                for line in tfile:
                    i += 1
                    if i >= (rows - 6):
                        break

                    if len(line) <= cols:
                        print line.strip('\n\r')
                    else:
                        print line[0:cols].strip('\n\r')

            print("")
            print colorama.Fore.YELLOW + "Trash: " + str(trash) + " Plain: " + str(plain) + " Hash: " + str(hashes)

            input_descr = colorama.Fore.MAGENTA + "[o]"
            input_descr += colorama.Fore.CYAN + "open "
            input_descr += colorama.Fore.MAGENTA + "[t]"
            input_descr += colorama.Fore.CYAN + "rash "
            input_descr += colorama.Fore.MAGENTA + "[p]"
            input_descr += colorama.Fore.CYAN + "lain "
            input_descr += colorama.Fore.MAGENTA + "[h]"
            input_descr += colorama.Fore.CYAN + "ash "
            input_descr += colorama.Fore.MAGENTA + "[s]"
            input_descr += colorama.Fore.CYAN + "kip "
            input_descr += colorama.Fore.MAGENTA + "[q]"
            input_descr += colorama.Fore.CYAN + "uit=> "

            sys_stdout.write(input_descr)
            sys_stdout.flush()

            answer = getch()

            while answer == '':
                pass

            # Opening a file with the default application AND being cross platform is a PITA...
            if answer == 'o':
                current_os = platform_system()
                if current_os == 'Windows':
                    from os import startfile as os_startfile
                    os_startfile(rfile)
                elif current_os == 'Linux':
                    subprocess_call(["xdg-open", rfile])
                elif current_os == 'Darwin':
                    system("open " + rfile)

                # Let's start the loop again to read the new key
                answer = getch()

                while answer == '':
                    pass

            if answer == 't':
                shutil_copyfile(rfile, self.settings['data_dir'] + "/" + 'training/trash/' + path.basename(rfile))
            elif answer == 'p':
                shutil_copyfile(rfile, self.settings['data_dir'] + "/" + 'training/plain/' + path.basename(rfile))
            elif answer == 'h':
                shutil_copyfile(rfile, self.settings['data_dir'] + "/" + 'training/hash/' + path.basename(rfile))
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
        self.parentArgs.level = 1
        running = getscore.DumpScraperGetscore(self.settings, self.parentArgs)
        running.run(training=True)
