#!/usr/bin/env python
#coding:utf-8

import sys
import os
import subprocess
#childutils这个模块是supervisor的一个模型，可以方便我们处理event消息。。。当然我们也可以自己按照协议，用任何语言来写listener，只不过用childutils更加简便罢了
from supervisor import childutils
from optparse import OptionParser
import socket
import fcntl
import struct

__doc__ = "\033[32m%s,捕获PROCESS_STATE_EXITED事件类型,当异常退出时触发报警\033[0m" % sys.argv[0]


def write_stdout(s):
    sys.stdout.write(s)
    sys.stdout.flush()



class CallError(Exception):
    """定义异常，没啥大用其实"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
# 定义处理event的类
class ProcessesMonitor():
    def __init__(self):
        self.stdin = sys.stdin
        self.stdout = sys.stdout

    def runforever(self):
        '''定义一个无限循环，可以循环处理event，当然也可以不用循环，把listener的autorestart#配置为true，
        处理完一次event就让该listener退出，然后supervisord重启该listener，这样listen#er就可以处理新的event了
        '''
        while 1:
            # 下面这个东西，是向stdout发送"READY"，然后就阻塞在这里，一直等到有event发过来
            # headers,payload分别是接收到的header和body的内容
            headers, payload = childutils.listener.wait(self.stdin, self.stdout)
            # 判断event是否是咱们需要的，不是的话，向stdout写入"RESULT\NOK"，并跳过当前
            # 循环的剩余部分
            if not headers['eventname'] == 'PROCESS_STATE_EXITED':
                childutils.listener.ok(self.stdout)
                continue

            pheaders, pdata = childutils.eventdata(payload + '\n')
            # 判读event是否是expected是否是expected的，expected的话为1，否则为0
            # 这里的判断是过滤掉expected的event
            if int(pheaders['expected']):
                childutils.listener.ok(self.stdout)
                continue

            ip = self.get_ip('eth0')
            # 构造报警信息结构
            msg = "[Host:%s][Process:%s][pid:%s][exited unexpectedly fromstate:%s]" % (
                ip, pheaders['processname'], pheaders['pid'], pheaders['from_state'])
            # 调用报警接口，这个接口是我们公司自己开发的，大伙不能用的，要换成自己的接口
            subprocess.call("/usr/local/bin/alert.py -m '%s'" % msg, shell=True)
            # stdout写入"RESULT\nOK"，并进入下一次循环
            childutils.listener.ok(self.stdout)

    '''def check_user(self):
        userName = os.environ['USER']
        if userName != 'root':
            try:
                raise MyError('must be run by root!')
            except MyError as e:
                write_stderr( "Error occurred,value:%s\n" % e.value)
                sys.exit(255)'''

    def get_ip(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
        ret = socket.inet_ntoa(inet[20:24])
        return ret


def main():
    parser = OptionParser()
    if len(sys.argv) == 2:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print __doc__
            sys.exit(0)
    # (options, args) = parser.parse_args()
    # 下面这个，表示只有supervisord才能调用该listener，否则退出
    if 'SUPERVISOR_SERVER_URL' not in os.environ:
        try:
            raise CallError("%s must be run as a supervisor event" % sys.argv[0])
        except CallError as e:
            write_stderr("Error occurred,value: %s\n" % e.value)

        return

    prog = ProcessesMonitor()
    prog.runforever()

if __name__ == '__main__':
    main()
