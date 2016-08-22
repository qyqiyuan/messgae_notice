#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from __future__ import division
import requests


def post_data(url, data):
    r = requests.post(url, data=data, timeout=1)
    return r.text


def get_data(url, data):
    r = requests.get(url, params=data, timeout=1)
    return r.text

operator = {"post": post_data, "get": get_data, }


def request_data(request_type, url, data):
    data = operator.get(request_type)(url, data)
    return data
