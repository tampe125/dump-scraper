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
Dump Scraper - Shorthand entry point

 This script will automatically fetch all the new dumps, calculates the score for them, organize
 and finally extract the interesting data from them (hashes and passwords).
'''))
parser.add_argument('-s', '--since', help='Starting date for the analysis, format YYYY-MM-DD', required=True)
parser.add_argument('-u', '--until', help='Stopping date for the analysis, format YYYY-MM-DD. If not supplied only the SINCE date will be processed')

args = parser.parse_args()

# Print banner
print("")
print("Dump Scraper")
print("Copyright (C) 2015 FabbricaBinaria - Davide Tampellini")
print("===============================================================================")
print("Dump Scraper is Free Software, distributed under the terms of the GNU General")
print("Public License version 3 or, at your option, any later version.")
print("This program comes with ABSOLUTELY NO WARRANTY as per sections 15 & 16 of the")
print("license. See http://www.gnu.org/licenses/gpl-3.0.html for details.")
print("===============================================================================")
print("")

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
