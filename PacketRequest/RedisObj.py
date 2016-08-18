# coding:utf-8
import time
import json
import redis
from BaseObj import BaseObj
import config
import logging.config
logging.config.dictConfig(config.LOGGING)
logger = logging.getLogger('mylogger')


class RedisObj(BaseObj):
    def __init__(self):
        self.__redis_host = config.redis_host
        self.__redis_port = config.redis_port
        self.__redis_db = config.redis_db
        self.__redis_auth = config.redis_auth
        self.redis_sleep_time = config.SLEEP_TIME

    def get_redis_pool(self):
        redis_handler = redis.ConnectionPool(host=self.__redis_host,
                           port=self.__redis_port, db=self.__redis_db, password=self.__redis_auth)

        return redis_handler

    def get_task(self, key):
        redis_con = redis.Redis(connection_pool=self.get_redis_pool())
        task_info = redis_con.lpop(key)
        while not task_info:
            time.sleep(self.redis_sleep_time)
            task_info = redis_con.lpop(key)
        logger.debug("取到一个数据......")
        task_info = json.loads(task_info)
        return task_info

    def push_task(self, key, data, reverse=False):
        redis_con = redis.Redis(connection_pool=self.get_redis_pool())
        data = json.dumps(data)
        if reverse:
            redis_con.rpush(key, data)
        else:
            redis_con.lpush(key, data)

    def delete_task(self, key, data):
        redis_con = redis.Redis(connection_pool=self.get_redis_pool())
        data = json.dumps(data)
        redis_con.lrem(key, data, 1)
