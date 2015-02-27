__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'

import argparse
import textwrap
import os
import re
from subprocess import call

__DIR__ = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent('''
Dumpmon Scraper - Shorthand entry point

 This script will automatically fetch all the new dumps, calculates the score for them, organize
 and finally extract the interesting data from them (hashes and passwords).
'''))
parser.add_argument('-s', '--since', help='Starting date for the analysis, format YYYY-MM-DD', required=True)
parser.add_argument('-u', '--until', help='Stopping date for the analysis, format YYYY-MM-DD. If not supplied only the SINCE date will be processed')

args = parser.parse_args()

if None == re.match('(?:19|20)\d{2}-(?:0[1-9]|1[012])-(?:0[1-9]|[12][0-9]|3[01])', args.since):
    print("SINCE argument should be a date in YYYY-MM-DD format")
    exit(0)

parameters = ["-s " + args.since]

if args.until:
    if None == re.match('(?:19|20)\d{2}-(?:0[1-9]|1[012])-(?:0[1-9]|[12][0-9]|3[01])', args.until):
        print("UNTIL argument should be a date in YYYY-MM-DD format")
        exit(0)

    parameters.extend([" -u " + args.until])

call(["php", __DIR__ + "/scrape.php"])
call(["php", __DIR__ + "/organize.php"] + parameters)
call(["python", __DIR__ + "/classify.py"])
call(["php", __DIR__ + "/extract.php"] + parameters)
