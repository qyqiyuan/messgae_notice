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
}
```
## get_message_data()的定义
根据`http_method`确定使用   `requests`的`get`方法还是`post`方法
根据 `content_type` 生成数据格式（使用`requests`无论是`post`还是`get`数据都是字典形的，不同的只有参数是`data`还是`params`）
- form : urlparse.parse_qs(data)
- json : 直接json.loads(data)
- xml : 待写


### 1.做任务恢复, 将`tmp_message_storge_key`里的数据转移到`message_storge_key`的头部

### 2.获取消息，并备份至`tmp_message_storge_key`

### 3.. 确定是第几次通知,添加参数`notice_count`记录这是第几次消息通知
 - ######  第一次 : `request_data = get_message_data()`
 - ###### 非第一次 : 先检查通知时间是否到了
  - ###### 没到 塞回队列尾部，日志记录，返回
  - ###### 时间到了 `request_data = request_data`

### 4. 通知,记录返回值，出错则打日志，return

### 5. 从 `tmp_message_storge_key`删除备份信息

### 6. 记录是否成功，第一成功则记录成功的id

### 7. 通过检查是否有回调url和是否成功，判断是否要进行回调，
 - ###### 如果`enforce_repeate_notice = True`则回调后继续多次通知,会照成回调TRY_TIME * TRY_TIME 次的情况，一般不建议设置为 `True`，除非是严苛场景
 - ###### 回调的数据格式为：
 {
     'url': xxx.php(原callbak_url),
     'http_method': "get",
     'content_type': "form",
     'data': None,
 }

 ### 8. 后续通知的封装，检查是第几次通知
  - ###### 第5次：打日志，谁的通知完成，是否有成功的记录，return

  - ###### 第一次：
```
   message["notice_interval"] = deepcopy(notice_interval)
   message["notice_time"] = time.time() + message["notice_interval"].pop(0)
   message["notice_data"] = request_data
```
- ###### 中间：
```
message["notice_time"] = time.time() +\
    message["notice_interval"].pop(0)
```
塞回 `message_storge_key`的尾部

{
    url: http://X/x.php,
    http_method: post(默认)|get
    content_type: form(默认)|json|xml
    data：a=1&b=2|{"a":1, "b":2}|..
    callbak_url: http://X/xx.php  (可选参数，如果有此参数那么回调通知也需要重复通知，即最多5*5次通知)
    success_flag:xxxxx (默认 success)

    # 下面几个参数是程序添加的
    notice_count : 第几次通知
    notice_interval : （10*60，10*60......） 列表， 里面的项应该比notice_count少1  //通知的时间间隔
    notice_time : time.time()+notice_interval.pop(0)  //下次的通知时间
    notice_data : 第一次通知后把数据解析好 非第一次通知就不需要查看content_type项和data项了
    success_id 首次通知成功的编号， 0为还未成功过

}
