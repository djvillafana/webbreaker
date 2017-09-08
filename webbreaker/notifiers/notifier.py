#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Notifier(object):

    """
    Base class for all notifiers
    """

    def __init__(self, name=None):
        self._name = name

    def notify(self, event):
        """Create notification of event.
        :param event: The event for which to create a notification
        """
        pass
