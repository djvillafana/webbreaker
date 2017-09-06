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


def get_file_logger(name=None):
    default = "__webbreaker__"
    log_map = {"__webbreaker__": APP_LOG, "__webbreaker_debug__": DEBUG_LOG}

    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger(default)

    formatter = logging.Formatter('%(asctime)s: %(name)s %(levelname)s(%(message)s')
    fh = logging.FileHandler(log_map[name], 'a')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # TODO: separate this out between app and debug files
    logger.setLevel(logging.DEBUG)
    return logger


def get_stout_logger(name=None):
    default = "__webbreaker_stout__"
    stout_log_map = {"__webbreaker_stout__": STOUT_LOG, "__splunk__": SPLUNK_LOG}

    if name:
        stout_logger = logging.getLogger(name)
    else:
        stout_logger = logging.getLogger(default)

    oh = logging.StreamHandler(stream=sys.stdout)
    oh.setFormatter(FORMATTER)
    # Only send stout INFO level messages
    oh.setLevel(logging.INFO)
    # stout does not include less than and equal to WARNING
    oh.addFilter(LessThenFilter(logging.WARNING))
    stout_logger.addHandler(oh)
    return stout_logger


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
        self.app = get_file_logger("__webbreaker__")
        self.debug = get_file_logger("__webbreaker_debug__")
        self.output = get_stout_logger("__webbreaker_stout__")
        self.splunk = get_stout_logger("__splunk_webinspect__")

        self.console = get_console_logger()

