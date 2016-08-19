## 任务获取
在`redis redis_message_storge` 里`lpop`出一个新任务，同时`rpush`进`redis_message_tmp_storge`里做任务备份

消息的基本格式：
```
{
    url: http://X/x.php,
    http_method: post(默认)|get
    content_type: form(默认)|json|xml
    data：a=1&b=2|{"a":1, "b":2}|..
    callbak_url: http://X/xx.php  (可选参数，如果有此参数那么回调通知也需要重复通知，即最多5*5次通知)
    success_flag:xxxxx (默认 success)

    # 下面几个参数是程序添加的
    notice_count : 剩余的通知次数 settings里最大通知次数-1
    notice_interval : （10*60，10*60......） 列表， 里面的项应该比notice_count少1  //通知的时间间隔
    notice_time : time.time()+notice_interval.pop(0)  //下次的通知时间
    notice_data : 第一次通知后把数据解析好 非第一次通知就不需要查看content_type项和data项了

}
```
## 通知前的处理
根据`http_method`确定使用   `requests`的`get`方法还是`post`方法
根据 `content_type` 生成数据格式（使用`requests`无论是`post`还是`get`数据都是字典形的，不同的只有参数是`data`还是`params`）
- form : urlparse.parse_qs(data)
- json : 直接json.loads(data)
- xml : 待写

## 通过检查是否有 notice_count 项 来判断是否是第一次通知，如果是第一次通知执行 1，如果不是执行2

### 1. `message_data = get_message_data()`发送通知(并从`redis_message_tmp_storge`里删除任务备份) 检查`success_flag`：如果成功执行1.1，否则执行1.2   
 - 1.1. 检查是否有 `callbak_url`,如果有则执行1.1.1，没有则执行1.2
  - 1.1.1 封装回调通知,`lpush`进`redis_message_storge` ,回调通知的格式是：
```
{
    callbak : True,
    url : xx.php,
}
```
 - 1.2. 添加参数  
 ```
notice_count = 4    
notice_interval = copy.deepcopy(settings.notice_interval)   
notice_time = time.time()+notice_interval.pop(0)   
request_data =  message_data
```
`rpush`进 `redis redis_message_storge`
