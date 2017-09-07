#!/usr/bin/env python
# -*-coding:utf-8-*-

import logging.config
import logging
import datetime
import sys
import os


FORMATTER = logging.Formatter('%(levelname)s: %(message)s')
DATETIME_SUFFIX = datetime.datetime.now().strftime("%m-%d-%Y-%H%M%S")
APP_LOG = os.path.abspath(os.path.join('/tmp/', 'webbreaker-' + DATETIME_SUFFIX + '.log'))
DEBUG_LOG = os.path.abspath(os.path.join('/tmp/', 'webbreaker-debug-' + DATETIME_SUFFIX + '.log'))
SPLUNK_LOG = os.path.abspath(os.path.join('/tmp/', 'splunk-' + DATETIME_SUFFIX + '.log'))
STOUT_LOG = os.path.abspath(os.path.join('/tmp', 'webbreaker-out' + DATETIME_SUFFIX + '.log'))


def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()


def get_console_logger():
    console_logger = logging.getLogger()
    console_logger.setLevel(logging.NOTSET)
    #TODO: remove levelname from console_formatter
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setFormatter(FORMATTER)
    # Only send stout INFO level messages
    ch.setLevel(logging.INFO)
    # stout does not include less than and equal to WARNING
    ch.addFilter(LessThenFilter(logging.WARNING))
    console_logger.addHandler(ch)
    return console_logger


def get_app_logger(name=None):
    default = "__webbreaker__"
    log_map = {"__webbreaker__": APP_LOG}

    if name:
        app_logger = logging.getLogger(name)
    else:
        app_logger = logging.getLogger(default)

    formatter = logging.Formatter('%(asctime)s: %(name)s %(levelname)s(%(message)s')
    fh = logging.FileHandler(log_map[name], 'a')
    fh.setFormatter(formatter)
    app_logger.setLevel(logging.DEBUG)
    app_logger.addHandler(fh)
    return app_logger


def get_debug_logger(name=None):
    #log_map = {"__webbreaker_debug__": DEBUG_LOG}
    debug_logger = logging.getLogger(name)
    debug_logger.setLevel(logging.NOTSET)
    debug_formatter = logging.Formatter('%(asctime)s: %(name)s %(levelname)s(%(message)s')

    fh = logging.FileHandler(DEBUG_LOG, mode='a')
    fh.setFormatter(debug_formatter)
    fh.setLevel(logging.DEBUG)
    debug_logger.addHandler(fh)

    return debug_logger


# Override existing hierarchical filter logic in logger mod
class LessThenFilter(logging.Filter):
    def __init__(self, level):
        self._level = level
        logging.Filter.__init__(self)

    def filter(self, rec):
        return rec.levelno < self._level


@singleton
class Logger():
    def __init__(self):
        self.app = get_app_logger("__webbreaker__")
        self.debug = get_debug_logger("__webbreaker_debug__")
        self.console = get_console_logger()

