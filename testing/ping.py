
import os

def ping(hostname,count):

    response = os.system("ping -c " + count + " " + hostname)
    if response == 0:
        return 0
    else:
        return 1

if __name__ == '__main__':
    host = str(input())
    count = input()
    ping(host, count)