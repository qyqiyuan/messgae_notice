#!/usr/bin/python
# coding:utf-8
import sys


def write_stdout(s):
    # only eventlistener protocol messages may be sent to stdout
    sys.stdout.write(s)
    sys.stdout.flush()


def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()


def main():
    while 1:
        # transition from ACKNOWLEDGED to READY
        # 状态转换
        write_stdout('READY\n')

        # read header line and print it to stderr
        # 从错误日志里取出一条数据
        line = sys.stdin.readline()
        write_stderr(line)

        # read event payload and print it to stderr
        headers = dict([x.split(':') for x in line.split()])
        data = sys.stdin.read(int(headers['len']))
        write_stderr(data)

        # transition from READY to ACKNOWLEDGED
        # 状态转换
        write_stdout('RESULT 2\nOK')

if __name__ == '__main__':
    main()
