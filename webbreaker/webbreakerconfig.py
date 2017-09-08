#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    import ConfigParser as configparser
except ImportError: #Python3
    import configparser
import os
from webbreaker.webbreakerhelper import WebBreakerHelper
from webbreaker.notifiers import emailer
from webbreaker.webbreakerlogger import Logger
from webbreaker.notifiers import reporter

runenv = WebBreakerHelper.check_run_env()

# TODO: Test on Python2
try:  # Python 2
    config = configparser.SafeConfigParser()
except NameError:  # Python 3
    config = configparser.ConfigParser()


class WebBreakerConfig(object):
    def parse_fortify_settings(self):
        fortify_dict = {}
        fortify_setting = os.path.abspath(os.path.join('webbreaker', 'etc', 'fortify.ini'))
        if os.path.exists(fortify_setting):
            fortify_dict = {}
            config.read(fortify_setting)

            try:
                fortify_dict['fortify_url'] = config.get("fortify", "ssc_url")
                fortify_dict['application_name'] = config.get("fortify", "application_name")
                fortify_dict['project_template'] = config.get("fortify", "project_template")
                fortify_dict['fortify_secret'] = config.get("fortify", "fortify_secret")
            except configparser.NoOptionError:
                Logger.console.error("{} has incorrect or missing values!".format(fortify_setting))
        else:
            Logger.console.debug("There is no {}".format(fortify_setting))

        return fortify_dict

    def parse_emailer_settings(self):
        emailer_dict = {}
        emailer_setting = os.path.abspath(os.path.join('webbreaker', 'etc', 'email.ini'))
        if os.path.exists(emailer_setting):
            config.read(emailer_setting)

            try:
                emailer_dict['smtp_host'] = config.get('emailer', 'smtp_host')
                emailer_dict['smtp_port'] = config.get('emailer', 'smtp_port')
                emailer_dict['from_address'] = config.get('emailer', 'from_address')
                emailer_dict['to_address'] = config.get('emailer', 'to_address')
                emailer_dict['email_template'] = config.get('emailer', 'email_template')
            except configparser.NoOptionError:
                Logger.console.error("{} has incorrect or missing values!".format(emailer_setting))

        else:
            Logger.console.info("Your scan email notifier is not configured: {}".format(emailer_setting))

        return emailer_dict


    def create_reporter(self):

        notifiers = []


        emailer_settings = self.parse_emailer_settings()
        notifiers.append(emailer.EmailNotifier(emailer_settings))

        return reporter.Reporter(notifiers)
