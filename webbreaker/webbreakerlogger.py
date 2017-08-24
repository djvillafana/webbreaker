#!/usr/bin/env python
# -*-coding:utf-8-*-

import logging.config
import logging
import os.path
import string
import random

LOGGING_CONF = os.path.abspath(os.path.join('webbreaker', 'etc', 'logging.ini'))
SCAN_NAME = "webbreaker" + "-" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))


def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()


@singleton
class Logger():
    def __init__(self):
        logging.config.fileConfig(LOGGING_CONF, defaults={'logfilename': '/tmp/' + SCAN_NAME + '.log'})
        self.file_logr = logging.getLogger('elogger')
        self.file_logr.logfilepath = '/tmp/' + SCAN_NAME + '.log'
