# coding:utf-8
import redis
import json
import os
data = {
    "url": "http://ajun.tunnel.qydev.com/test3.php",
    "http_method": "post",
    "content_type": "form",
    "data": "a=1&b=2",
    "callback_url": "http://ajun.tunnel.qydev.com/test4.php",
    "success_flag": "specified"
}
# , password="uid"
redis_pool = redis.ConnectionPool(host='121.199.34.235', port=6379, db=0, password="uid")
r = redis.Redis(connection_pool=redis_pool)
redis_key = "6y:message:notice:task"
print r.rpush(redis_key, json.dumps(data))
# print r.lpop(redis_key)
