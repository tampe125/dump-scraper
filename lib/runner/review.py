__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import colorama
from os import path as os_path, walk as os_walk, system, name
from platform import system as platform_system
from subprocess import call as subprocess_call
from sys import stdout as sys_stdout
from lib.runner.abstract import AbstractCommand
from lib.exceptions.exceptions import RunningError
from lib.utils.terminalsize import get_terminal_size
from lib.utils.getch import getch


class DumpScraperReview(AbstractCommand):
    def check(self):
        if not os_path.exists(self.settings['data_dir'] + '/organized'):
            raise RunningError("There aren't any organized dump files to process. Organize them before continuing.")

    def run(self):
        stop = False

        for folder in ['trash', 'plain', 'hash']:
            if stop:
                break

            review_folder = self.settings['data_dir'] + '/organized/' + folder + "/" + self.parentArgs.dir

            if not os_path.exists(review_folder):
                print 'Folder "' + folder + '" not found, skipping...'
                continue

            files = [os_path.join(w_path, filename)
                     for w_path, dirs, files in os_walk(review_folder)
                     for filename in files
                     if not filename.endswith(".csv")]

            idx = 0

            while idx < len(files):
                rfile = files[idx]

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

                files_left = len(files) - idx
                print("")
                print colorama.Fore.YELLOW + "Folder: " + folder + " " + colorama.Fore.CYAN + str(files_left) + colorama.Fore.YELLOW + " files left"

                input_descr = colorama.Fore.MAGENTA + "[o]"
                input_descr += colorama.Fore.CYAN + "open "
                input_descr += colorama.Fore.MAGENTA + "[s]"
                input_descr += colorama.Fore.CYAN + "kip folder "
                input_descr += colorama.Fore.MAGENTA + "[n]"
                input_descr += colorama.Fore.CYAN + "ext "
                input_descr += colorama.Fore.MAGENTA + "[p]"
                input_descr += colorama.Fore.CYAN + "revious "
                input_descr += colorama.Fore.MAGENTA + "[q]"
                input_descr += colorama.Fore.CYAN + "uit=> "

                sys_stdout.write(input_descr)
                sys_stdout.flush()

                answer = getch()

                while answer == '':
                    pass

                idx += 1

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

                if answer == 'n':
                    print("")
                elif answer == 'p':
                    if idx >= 2:
                        idx -= 2
                    continue
                elif answer == 's':
                    break
                elif answer == 'q':
                    print("")
                    stop = True
                    break
                else:
                    print("")

        print(colorama.Fore.GREEN + "Review completed")
