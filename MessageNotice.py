#!/usr/bin/python
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
import settings
import task
import logConfig
from getRequestData import get_request_data
from request_type import request_data
import logging.config
logging.config.dictConfig(logConfig.LOGGING)
logger = logging.getLogger('notice')
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class MessageNotice(object):
    def __init__(self):
        self.__TRY_TIME = settings.TRY_TIME
        self.__notice_count = 0
        self.__notice_interval = settings.notice_interval
        self.__message_storge_key = settings.redis_message_storge
        self.__backup_message_storge_key = settings.redis_backup_message_storge
        self.__notice_success = False
        self.__request_data = None
        self.__response_data = None
        self.__message = None
        self.__enforce_repeate_notice = settings.enforce_repeate_notice
        self.sleep_time = settings.no_task_sleep_time

    def get_message(self, key):
        """获取一个任务
        """
        get_task = task.get_task_handle("get_task")
        message = get_task(key)
        return message

    def push_message(self, key, message, reverse=False):
        """塞消息
        """
        push_task = task.get_task_handle("push_task")
        push_task(key, message, reverse)

    def del_message(self, key, message):
        delete_task = task.get_task_handle("delete_task")
        delete_task(key, message)

    def package_callbak(self):
        """"将需要回调的信息封装好塞到redis的头部
        """
        callbak_data = {
            'url': self.__message.get("callback_url"),
            'http_method': "get",
            'content_type': "query_string",
            'data': None,
        }
        self.push_message(key=self.__message_storge_key, message=callbak_data, reverse=True)
        logger.info("%s在第%s次时通知成功, 不再重复通知,准备回调%s" % (self.__message.get("url"),
                    self.__notice_count, self.__message.get("callback_url")))

    def check_callbak(self):
        """检查是否满足条件:通知成功并且有回调,如满足则回调并且检查是否有强制多次通知，有返回2，没有返回0,
        如果没有满足条件则返回1,如果是0则不需要多次通知了,如果非0则还是需要继续通知
        """
        if (self.__message.get("callback_url", None)) and self.__notice_success:
            self.package_callbak()
            if self.__enforce_repeate_notice:
                return 2
            return 0
        return 1

    def repeate_notice(self):
        """通过检查notice_count参数判断是第几次通知，以及对应的处理方式
        """
        if self.__notice_count == 1:
            # 第一次通知需要封装消息进去
            self.__message["notice_interval"] = deepcopy(self.__notice_interval)
            self.__message["notice_time"] = time.time() + self.__message["notice_interval"].pop(0)
            self.__message["notice_data"] = self.__request_data
            self.__message["notice_count"] = self.__notice_count
        elif self.__notice_count == 5:
            logger.info("%s通知完毕,是否通知成功过:%s" % (self.__message.get("url"),
                        self.__message.get("success_id", 0)))
            return
        else:
            # 正常通知，做好通知次数更新和下次通知时间的记录
            self.__message["notice_count"] = self.__notice_count
            self.__message["notice_time"] = time.time() +\
                self.__message["notice_interval"].pop(0)
        self.push_message(key=self.__message_storge_key, message=self.__message)

    def success_record(self):
        """通知成功，记录通知的id号
        """
        success_flag = self.__message.get("success_flag", "success")
        if success_flag in self.__response_data:
            self.__notice_success = True
            if "success_id" not in self.__message:
                self.__message["success_id"] = self.__notice_count

    def message_restore(self):
        logger.debug("准备进行通知任务恢复.......")
        get_task_count = task.get_task_handle("get_task_count")
        upload_task_count = get_task_count(self.__backup_message_storge_key)
        if upload_task_count:
            get_task = task.get_task_handle("get_task")
            push_task = task.get_task_handle("push_task")
            for count in range(upload_task_count):
                message = get_task(self.__backup_message_storge_key)
                logger.debug("恢复%s:" % message.get("url"))
                push_task(self.__message_storge_key, message, reverse=True)
            logger.debug("任务恢复完成........")
        else:
            logger.debug("没有待恢复的任务.......")

    def message(self):
        """
        正式通知前的预处理:包括取任务,任务备份，设置是第几次通知,
        根据是第几次通知来生成将要发送的数据
        """
        # 取一个任务
        self.__message = self.get_message(key=self.__message_storge_key)
        # 无任务休息一会，return
        if not self.__message:
            logger.debug("无任务,sleep %s s" % self.sleep_time)
            time.sleep(self.sleep_time)
            return
        # 通知前先备份
        self.push_message(key=self.__backup_message_storge_key, message=self.__message)
        # logger.debug("取到一个任务:%s" % (self.__message))
        # 设置通知号
        self.__notice_count = self.__message.get("notice_count", 0) + 1
        # 按通知次数号分别处理
        if self.__notice_count == 1:
            # 第一次通知，通知数据格式封装好
            self.__request_data = get_request_data(self.__message.get("content_type", "query_string"),
                                                   self.__message.get("data", None))
        else:
            # 不是第一次通知
            # 检查时间到没到，没到就扔回队列尾部去
            # todo 扔到哪里
            if self.__message.get("notice_time") > time.time():
                self.push_message(key=self.__message_storge_key, message=self.__message)
                # 删除备份
                self.del_message(key=self.__backup_message_storge_key, message=self.__message)
                # 打个时间未到的日志
                # logger.debug("%s 通知时间未到" % self.__message.get("url"))
                return
            self.__request_data = self.__message.get("notice_data")
        # logger.debug("请求的数据为：%s" % self.__request_data)
        self.notice()

    def notice(self):
        """正式通知,检查是否成功处理,回调处理，是否多次通知处理
        """
        try:
            self.__response_data = request_data(self.__message.get("http_method", "get"),
                                                self.__message.get("url"), self.__request_data)
            logger.debug("第%s次通知%s成功,返回值:%s" % (self.__notice_count,
                         self.__message.get("url"), self.__response_data))
            # 删除备份
            self.del_message(key=self.__backup_message_storge_key, message=self.__message)
        except Exception as e:
            logger.warning("第%d次通知%s失败，原因%s：" % (self.__message.get
                           ("notice_count", 1), self.__message.get("url"), e))
            # 删除备份
            self.del_message(key=self.__backup_message_storge_key, message=self.__message)
            return
        else:
            # 记录是否成功过
            self.success_record()
            # 做回调
            repeate_flag = self.check_callbak()
            # repeate_flag != 0代表 需要多次通知
            if repeate_flag:
                self.repeate_notice()


class MessageControl(object):
    """
    消息通知主程序
    """
    def __init__(self):
        self.__be_kill = False
        self.__sleep_time = settings.no_task_sleep_time
        self.__message_storge_key = settings.redis_message_storge
        self.__backup_message_storge_key = settings.redis_backup_message_storge
        self.NOTICE_THREADS_NUM = settings.NOTICE_THREADS_NUM

    def setQuit(self, pid, signal_num):
        logger.warning("kill by USR2")
        self.__be_kill = True

    def gevent_join(self):
        MessageNotice().message_restore()
        gevent_task = []
        for each in range(self.NOTICE_THREADS_NUM):
            gevent_task.append(gevent.spawn(self.message_notice))
        gevent.joinall(gevent_task)

    def message_notice(self):
        while True:
            if self.__be_kill:
                break
            MessageNotice().message()


if __name__ == "__main__":
    mnotice = MessageControl()
    signal.signal(signal.SIGUSR2, mnotice.setQuit)
    mnotice.gevent_join()
