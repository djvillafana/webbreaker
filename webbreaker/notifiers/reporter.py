#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Reporter(object):

    def __init__(self, notifiers):
        self.notifiers = notifiers

    def report(self, event):

        for notifier in self.notifiers:
            notifier.notify(event)
