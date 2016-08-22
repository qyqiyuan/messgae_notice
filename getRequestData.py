#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from __future__ import division
import urlparse
import json


def get_form_data(data):
    try:
        data = urlparse.parse_qs(data)
    except:
        data = None
    finally:
        return data


def get_json_data(data):
    try:
        data = json.loads(data)
    except:
        data = None
    finally:
        return data

operator = {"form": get_form_data, "json": get_json_data, }


def get_request_data(type, data):
    data = operator.get(type)(data)
    return data
