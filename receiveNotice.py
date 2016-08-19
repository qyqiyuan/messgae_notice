#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-
from gevent import monkey
monkey.patch_all()
import signal
import sys
import time
import os
from copy import deepcopy
import gevent
from __future__ import print_function
import settings
import task
import logConfig
from getRequestData import get_request_data
from request_type import request_data
import logging.config
logging.config.dictConfig(logConfig.LOGGING)
logger = logging.getLogger('notice')
gevent.monkey..patch_all()


class Message(object):
    def __init__(self):
        self.__TRY_TIME = settings.TRY_TIME
        self.__notice_interval = settings.notice_interval

    def get_message_info(self):
        """获取一个任务，同时备份
        """
        get_task = task.get_task_handle("get_task")
        message = get_task(settings.redis_message_storge)
        push_task = task.get_task_handle("push_task")
        push_task(settings.redis_message_tmp_storge, message)
        return message

    def package_callbak(self, message, response_data):
        callbak_data = {
            'url': message.get("callbak_url"),
            'http_method': "get",
            'content_type': "form",
            'data'：None,
        }
        push_task = task.get_task_handle("push_task")
        push_task(settings.redis_message_storge, callbak_data, reverse=True)

    def check_callbak(self, message, response_data):
        """需要回调则回调，不用回调则跳过
        """
        if not message.get("callbak_url", None):
            success_flag = message.get("success_flag", "success")
            if success_flag in response_data:
                self.package_callbak()
                return 0
        return 1

    def repeate_notice(self, message):
        # 第一次通知需要封装消息进去
        message["notice_count"] = self.__TRY_TIME - 1
        message["notice_interval"] = deepcopy(self.__notice_interval)
        message["notice_time"] = time.time() + message["notice_interval"].pop(0)

    def notice(self):
        while True:
            if not self.__is_run:
                sys.exit(0)
            message = self.get_message_info()
            # notice_url = self.get_notice_url(message)
            # 看是否有 request_data,确认是否是第一次通知
            if "request_data" in message:
                # 不是第一次通知,执行不是第一次通知的流程
                request_data = message.get("request_data")
            else:
                # 第一次通知，执行第一次通知该做的事
                request_data = get_request_data(message.get("content_type"), message.get("data"))
            response_data = request_data(message.get("http_method"), message.get("url"), request_data)
            # 做回调
            repeate_flag = self.check_callbak(message, response_data)
            # 删除备份
            delete_task = task.get_task_handle("delete_task")
            delete_task(settings.redis_message_tmp_storge, message, reverse=True)
            # repeate_flag = 1代表 需要多次通知 0代表
            if repeate_flag:
                self.repeate_notice(message)


class MessageNotice(object):
    """
    消息通知主程序
    """
    def __init__(self):
        self.__is_run = True
        self.__sleep_time = settings.SLEEP_TIME

    def setQuit(self, pid, signal_num):
        logger.warning("kill by USR2")
        self.__is_run = False

    def gevent_join(self):
        gevent_task = []
        for each in range(self.NOTICE_THREADS_NUM):
            gevent_task.append(gevent.spawn(self.message_notice))
        gevent.joinall(gevent_task)

    def message_notice(self):
        while True:
            if not self.__is_run:
                sys.exit(0)
            message = Message().notice()


if __name__ == "__main__":
    pass
