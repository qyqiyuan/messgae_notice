#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
from __future__ import print_function
from gevent import monkey
monkey.patch_all()
import signal
import sys
import time
import os
from copy import deepcopy
import gevent
import random



class MessageNotice(object):
    def __init__(self):
        self.__be_kill = False
        self.__sleep_time = 3
        self.NOTICE_THREADS_NUM = 4

    def message(self):
        time = random.randint(1, 10)
        print("sleep %s" % time)
        gevent.sleep(time)
        print("222222222222....")


class MessageControl(object):
    def __init__(self):
        self.__be_kill = False
        self.__sleep_time = 3
        self.NOTICE_THREADS_NUM = 4
        runable = 0

    def setQuit(self, pid, signal_num):
        print("kill by USR2")
        self.__be_kill = True

    def gevent_join(self):
        gevent_task = []
        for each in range(self.NOTICE_THREADS_NUM):
            gevent_task.append(gevent.spawn(self.message_notice))
        gevent.joinall(gevent_task)

    def message_notice(self):
        gevent.sleep(random.randint(1, 3))
        while True:
            if self.__be_kill:
                break
            MessageNotice().message()


if __name__ == "__main__":
    mnotice = MessageControl()
    signal.signal(signal.SIGUSR2, mnotice.setQuit)
    mnotice.gevent_join()
