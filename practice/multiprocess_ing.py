import os
import sys
import time
import signal
from multiprocessing import Process

from pytest_cov.embed import cleanup


def sig(s, frame):
    print('Signal Received:', s)
    cleanup()
    sys.exit(s)


def p():
    signal.signal(signal.SIGTERM, sig)

    i = 0
    try:
        while True:
            i += 1
            print(i)
            time.sleep(.3)
    except KeyboardInterrupt:
        print('CTRL+C detected')
        sys.exit(1)


if __name__ == '__main__':
    p = Process(target=p)
    p.daemon = True
    p.start()
    time.sleep(2)
    p.terminate()
    p.join()
    print('exit status:', p.exitcode)

