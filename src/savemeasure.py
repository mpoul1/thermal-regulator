import time
import datetime
import sys

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

f = open('/opt/z-way-server/automation/ThermalRegulator/src/measure.log', 'a')
f.write(st + "\t" + sys.argv[1] + "\t" + sys.argv[2] + "\n")
f.close()