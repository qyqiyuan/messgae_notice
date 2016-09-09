#!/usr/bin/python
# coding:utf-8
from __future__ import print_function
import signal
import sys
import time
import os


def setQuit(a, b):
    print("exit by myself")
    sys.exit(0)


def main():
    while True:
        print("11", "22", "33", "...", os.getpid())
        time.sleep(5)


if __name__ == "__main__":
    signal.signal(signal.SIGUSR2, setQuit)
    main()
