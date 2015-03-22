import datetime

__author__ = 'tampe125'

import abs_command
import os


class DumpScraperOrganize(abs_command.AbstractCommand):
    def run(self):
        folders = [self.parentArgs.since]

        if self.parentArgs.until:
            date  = datetime.datetime.strptime(self.parentArgs.since, "%Y-%m-%d").date()
            end   = datetime.datetime.strptime(self.parentArgs.until, "%Y-%m-%d").date()

            date += datetime.timedelta(days=1)

            while end >= date:
                folders.append(date.strftime('%Y-%m-%d'))
                date += datetime.timedelta(days=1)

        organizers = []

        for folder in folders:
            source = 'data/raw/' + folder

            print("")

            if not os.path.exists(source):
                print("Directory " + source + " does not exist!")
                continue

            print("Directory   : " + folder)

            for root, dirs, files in os.walk(source):
                for dump in files:
                    print(".")

                    with open(root + "/" + dump, 'r+') as handle:
                        data = handle.read()

                    data = data.replace("\r", "")

                    info = {'data': data, 'lines': max(data.count("\n"), 1)}

                    for organizer in organizers:
                        pass

