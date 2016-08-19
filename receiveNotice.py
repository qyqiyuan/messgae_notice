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


class Message(object):
    def __init__(self):
        self.__TRY_TIME = settings.TRY_TIME
        self.__notice_interval = settings.notice_interval
        self.message_storge_key = settings.redis_message_storge
        self.tmp_message_storge_key = settings.redis_tmp_message_storge
        self.__notice_success = False
        self.__request_data = None
        self.__response_data = None
        self.__message = None
        self.__enforce_repeate_notice = settings.enforce_repeate_notice

    def get_message_info(self):
        """获取一个任务，同时备份
        """
        get_task = task.get_task_handle("get_task")
        message = get_task(self.message_storge_key)
        self.__message = message
        push_task = task.get_task_handle("push_task")
        push_task(self.tmp_message_storge_key, message)

    def package_callbak(self):
        """"将需要回调的信息封装好塞到redis的头部
        """
        callbak_data = {
            'url': self.__message.get("callbak_url"),
            'http_method': "get",
            'content_type': "form",
            'data': None,
        }
        push_task = task.get_task_handle("push_task")
        push_task(self.message_storge_key, callbak_data, reverse=True)
        logger.debug("%s在第%s次时通知成功, 不再重复通知,准备回调%s" % (self.__message.get("url"),
                     self.__message.get("notice_count", 1), self.__message.get("callbak_url")))

    def check_callbak(self):
        """需要回调则回调，不用回调则返回1;需要回调则不再多次通知，改为多次回调了
        """
        if not self.__message.get("callbak_url", None) and self.__notice_success:
            self.package_callbak()
            if self.__enforce_repeate_notice:
                return 2
            return 0
        return 1

    def repeate_notice(self):
        """通过检查notice_count参数判断是第几次通知，以及对应的处理方式
        """
        notice_count = self.__message.get("notice_count", 1)
        if notice_count == 1:
            # 第一次通知需要封装消息进去
            self.__message["notice_interval"] = deepcopy(self.__notice_interval)
            self.__message["notice_time"] = time.time() + self.__message["notice_interval"].pop(0)
            self.__message["notice_data"] = self.__request_data
        elif notice_count == 5:
            logger.debug("%s通知完毕,是否通知成功过:%s" % (self.__message.get("url"),
                         self.__message.get("success_id", 0)))
            return
        else:
            # 正常通知，做好次数递减和下次通知时间的记录
            self.__message["notice_time"] = time.time() +\
                self.__message["notice_interval"].pop(0)
        push_task = task.get_task_handle("push_task")
        push_task(self.message_storge_key, self.__message)

    def success_record(self):
        """通知成功，记录通知的id号
        """
        success_flag = self.__message.get("success_flag", "success")
        if success_flag in self.__response_data:
            self.__notice_success = True
            if "success_id" not in self.__message:
                self.__message["success_id"] = self.__message["notice_count"]

    def notice(self):
        # 取一个任务
        self.get_message_info()
        # 设置通知号
        self.__message["notice_count"] = self.__message.get("notice_count", 0) + 1
        # 按通知号分别处理
        if self.__message.get("notice_count", 1) == 1:
            # 第一次通知，通知数据格式封装好
            self.__request_data = get_request_data(self.__message.get("content_type", "form"),
                                                   self.__message.get("data", None))
        else:
            # 不是第一次通知
            # 检查时间到没到，没到就扔回队列尾部去
            if self.__message.get("notice_data") > time.time():
                push_task = task.get_task_handle("push_task")
                push_task(self.message_storge_key, self.__message)
                # 打个时间未到的日志
                logger.debug("消息：%s时间未到，扔回队列尾部" % self.__message.get("url"))
                return
            self.__request_data = self.__message.get("request_data")
        # 正式通知
        try:
            self.__response_data = request_data(self.__message.get("http_method", "get"),
                                                self.__message.get("url"), request_data)
        except Exception as e:
            logger.debug("第%d次通知%s失败，原因%s：" % (self.__message.get("notice_count", 1),
                         self.__message.get("url"), e))
            return
        # 记录是否成功过，有记录将不再登记
        self.success_record()
        # 做回调
        repeate_flag = self.check_callbak()
        # 删除备份
        delete_task = task.get_task_handle("delete_task")
        delete_task(self.tmp_message_storge_key, self.__message, reverse=True)
        # repeate_flag = 1代表 需要多次通知
        if repeate_flag:
            self.repeate_notice()

    def message_restore(self):
        logger.debug("准备进行通知任务恢复.......")
        get_task = task.get_task_hand_way("get_task")
        push_task = task.get_task_hand_way("push_task")
        message = get_task(self.tmp_message_storge_key)
        while message:
            message = get_task(self.tmp_message_storge_key)
            logger.debug("恢复%s:" % message.get("url"))
            push_task(self.message_storge_key, message, reverse=True)
        logger.debug("任务恢复完成........")


class MessageNotice(object):
    """
    消息通知主程序
    """
    def __init__(self):
        self.__is_run = True
        self.__sleep_time = settings.no_task_sleep_time

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
            Message().notice()


if __name__ == "__main__":
    mnotice = MessageNotice()
    signal.signal(signal.SIGUSR2, mnotice.setQuit)
    mnotice.message_restore()
    mnotice.gevent_join()
