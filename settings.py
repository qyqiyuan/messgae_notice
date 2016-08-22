#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  -*--*--*--*--*--*--*--*- global   -*--*--*--*--*--*--*--*-
# 调试模式开关
DEBUG = True

# 尝试次数
TRY_TIME = 5

# 尝试的时间间隔
notice_interval = [10 * 60, 10 * 60, 10 * 60, 10 * 60, ]

# 睡眠的时间
no_task_sleep_time = 10


# 强制多次通知, 会照成回调TRY_TIME * TRY_TIME 次的情况
enforce_repeate_notice = True

# 通知的进程数
NOTICE_THREADS_NUM = 3

# -*--*--*--*--*--*--*--*-  任务存储的配置  -*--*--*--*--*--*--*--*--*--*--*--*-
# 消息存储的类型
task_type = 'redis'

# redis的IP地址
redis_host = '121.199.34.235'

# redis的端口
redis_port = 6379

# redis的数据库
redis_db = 0

# redis的密码
redis_auth = 'uid'

redis_message_storge = "6y:message:notice:task"
redis_tmp_message_storge = "6y:message:notice:tmptask"


# -**********************- 日志的配置 -**********************-

# 日志文件夹的根目录
logging_directory_path = 'log'
