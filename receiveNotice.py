#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-
from gevent import monkey
monkey.patch_all()
import signal
import sys
import time
import os
import gevent
from __future__ import print_function
import config
import task
import logConfig
import logging.config
logging.config.dictConfig(logConfig.LOGGING)
logger = logging.getLogger('notice')
gevent.monkey..patch_all()


class Message(object):
    def __init__(self):
        pass



class MessageNotice(object):
    """
    消息通知主程序
    """
    def __init__(self):
        self.__is_run = True
        self.__sleep_time = config.SLEEP_TIME

    def setQuit(self, pid, signal_num):
        logger.warning("kill by USR2")
        self.__is_run = False

    def get_message_info(self):
        get_task = task.get_task_hand_way("get_task")
        message = get_task(config.redis_message_storge)
        push_task = task.get_task_hand_way("push_task")
        push_task(config.redis_message_tmp_storge, message)
        return message

    def acquire_message(self):
        while True:
            if not self.__is_run:
                sys.exit(0)
            message = self.get_message_info()
            notice_url = self.get_notice_url(message)
            # TODO

    def gevent_join(self):
        gevent_task = []
        for each in range(self.packet_count):
            gevent_task.append(gevent.spawn(self.packet))
        for each in range(self.retry_packet_count):
            gevent_task.append(gevent.spawn(self.retry_packet))
        for each in range(self.message_count):
            message = self.initialize_message()
            gevent_task.append(gevent.spawn(message.message_queue()))
        for each in range(self.retry_upload_count):
            upload = self.initialize_upload()
            gevent_task.append(gevent.spawn(upload.get_upload_task))
        gevent.joinall(gevent_task)

if __name__ == "__main__":
    pass
