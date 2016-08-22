#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import settings


def mkdir_log_path(log_dir):
    if not os.path.isdir(log_dir):
        print("创建%s目录" % log_dir)
        os.makedirs(log_dir)


# 日志配置文件
def logging_file_path(log_type):
    date = time.strftime("%m%d", time.localtime())
    log_path = os.path.join(settings.logging_directory_path, date)
    mkdir_log_path(log_path)
    return os.path.join(log_path, "%s.log" % log_type)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'notes': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logging_file_path('all'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'default',
        },
        'success': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logging_file_path('success'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'default',
        },
        'warning': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logging_file_path('warning'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'default',
        },
    },
    'loggers': {
        # 定义了一个logger
        'notice': {
            'level': 'DEBUG',
            'handlers': ['console', 'notes', 'success', 'warning'],
            'propagate': True
        }
    }
}
