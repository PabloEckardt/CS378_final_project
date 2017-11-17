from ping import ping
from datetime import datetime
import time
import sys

plot = [] # array of tuples of (success to ms or failures to ms

CURR_TIME = datetime.now()
DIFF = datetime.now() - CURR_TIME
HOST = "8.8.8.8"
#HOST = "192.168.1.4"



def log_pings(TIME_LIMIT=5,HOST="8.8.8.8"):
    while  DIFF.total_seconds() < TIME_LIMIT:# 60 seconds

        ret = None

        try:
            ret = ping(HOST,"1")
        except Exception as e:
            print(e)

        DIFF = datetime.now() - CURR_TIME
        plot.append(DIFF.total_seconds(),ret)
        time.sleep(.05)



    with open ("net_report.csv", "w") as outfile:
        outfile.write("error,timings\n")
        for point in plot:
            outfile.write(str(point[0]) + "," + str(point[1]) + "\n")


if __name__ == "__main__":

    if len(sys.argv) == 3:
        _timeout = sys.argv[1]
        _host = sys.argv[2]
        log_pings(_timeout, _host)
    else:
        log_pings()
