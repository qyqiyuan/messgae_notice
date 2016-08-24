#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-
from __future__ import print_function
import signal
import sys
import time
import os


def setQuit(a, b):
    print("exit by myself")


def main():
    while True:
        signal.signal(signal.SIGUSR2, setQuit)
        print("11", "22", "33", "...", os.getpid())
        time.sleep(5)


if __name__ == "__main__":
    main()
