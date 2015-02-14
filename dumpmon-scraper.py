__author__ = 'tampe125'

import os
import datetime
from subprocess import call

__DIR__ = os.path.dirname(os.path.realpath(__file__))

date = datetime.date.today().strftime('%Y-%m-%d')

call(["php", __DIR__ + "/scrape.php"])
call(["php", __DIR__ + "/organize.php", "-s " + date])
call(["python", __DIR__ + "/organize.py"])
call(["php", __DIR__ + "/extract.php", "-s " + date])