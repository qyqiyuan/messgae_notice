#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-
import config


def get_task_hand_way(access_way):
    task_type = config.task_type.capitalize() + "Obj"
    task_module = __import__("PacketRequest." + task_type, globals(), locals(), [task_type])
    up_access = getattr(task_module, task_type)
    return getattr(up_access(), access_way)
