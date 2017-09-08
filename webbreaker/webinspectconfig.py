#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import ConfigParser as configparser
except ImportError: #Python3
    import configparser
import argparse
import os
import random
import string
import re
import xml.etree.ElementTree as ET
from git import Repo
from webbreaker.webbreakerlogger import Logger
from webbreaker.webbreakerhelper import WebBreakerHelper
from subprocess import CalledProcessError, Popen, PIPE, Popen, STDOUT

runenv = WebBreakerHelper.check_run_env()


# TODO: Test on Python2
try:  # Python 2
    config = configparser.SafeConfigParser()
except NameError:  # Python 3
    config = configparser.ConfigParser()


class WebInspectEndpoint(object):
    def __init__(self, uri, size):
        self.uri = uri
        self.size = size


class WebInspectSize(object):
    def __init__(self, size, max_scans):
        self.size = size
        self.max_scans = max_scans


class WebInspectConfig(object):
    def __init__(self):
        try:
            webinspect_dict = self.__get_webinspect_settings__()
            self.endpoints = webinspect_dict['endpoints']
            self.sizing = webinspect_dict['size_list']
            self.default_size = webinspect_dict['default_size']
            self.webinspect_git = webinspect_dict['git']
            self.webinspect_dir = webinspect_dict['dir']
            self.mapped_policies = webinspect_dict['mapped_policies']
        except KeyError as e:
            Logger.console.error("Your configurations file or scan setting is incorrect see log: {}!!!".format(Logger.app_logfile))
            Logger.app.error("Your configurations file or scan setting is incorrect : {}!!!".format(e))

    def __get_webinspect_settings__(self):
        webinspect_dict = {}
        webinspect_setting = os.path.abspath(os.path.join('webbreaker', 'etc', 'webinspect.ini'))

        try:
            config.read(webinspect_setting)
            webinspect_dict['git'] = config.get("configuration_repo", "git")
            webinspect_dict['dir'] = config.get("configuration_repo", "dir")
            webinspect_dict['default_size'] = config.get("webinspect_default_size", "default")
            webinspect_dict['mapped_policies'] = [[option, config.get('webinspect_policies', option)] for option in
                                                  config.options('webinspect_policies')]

            # python 2.7 config parser doesn't offer cross-section interpolation so be a bit magical about
            # which entries under api_endpoints get list comp'd. i.e. starts with e
            api_endpoints = [[option, config.get('api_endpoints', option)] for option in
                             config.options('api_endpoints')]
            webinspect_dict['endpoints'] = [[endpoint[1].split('|')[0], endpoint[1].split('|')[1]] for endpoint in
                                            api_endpoints if endpoint[0].startswith('e')]
            webinspect_dict['size_list'] = [[option, config.get('webinspect_size', option)] for option in
                                            config.options('webinspect_size')]

        except (configparser.NoOptionError, CalledProcessError) as noe:
            Logger.app.error("{} has incorrect or missing values {}".format(webinspect_setting, noe))
        except configparser.Error as e:
            Logger.app.error("Error reading webinspect settings {} {}".format(webinspect_setting, e))

        return webinspect_dict

    def __getScanTargets__(self, settings_file_path):
        """
        Given a settings file at the provided path, return a set containing
        the targets for the scan.
        :param settings_file_path: Path to WebInspect settings file
        :return: unordered set of targets
        """
        targets = set()
        try:
            tree = ET.parse(settings_file_path)
            root = tree.getroot()
            for target in root.findall("xmlns:HostFolderRules/"
                                       "xmlns:List/"
                                       "xmlns:HostFolderRuleData/"
                                       "xmlns:HostMatch/"
                                       "xmlns:List/"
                                       "xmlns:LookupList/"
                                       "xmlns:string", namespaces={'xmlns': 'http://spidynamics.com/schemas/scanner/1.0'}):
                targets.add(target.text)
        except Exception as e:
            Logger.app.error("Unable to determine scan targets {0}".format(e))

        return targets

    def parse_webinspect_options(self, options):
        webinspect_dict = {}

        if not options['scan_name']:
            try:
                if runenv == "jenkins":
                    options['scan_name'] = os.getenv("JOB_NAME")
                    if "/" in options['scan_name']:
                        options['scan_name'] = os.getenv("BUILD_TAG")
                else:
                    options['scan_name'] = "webinspect" + "-" + "".join(
                        random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            except AttributeError as e:
                Logger.app.error("The {0} is unable to be created! {1}".format(options['scan_name'], e))

        if options['upload_settings']:
            if not os.path.isfile(options['upload_settings']):
                try:
                    options['upload_scan_settings'] = str("{}".format(os.path.join(os.path.dirname(__file__),
                                                                       self.webinspect_dir, 'settings',
                                                                       options['upload_settings'] + '.xml')))
                except (AttributeError, TypeError) as e:
                    Logger.app.error("The {0} is unable to be assigned! {1}".format(options['upload_settings'], e))
            else:
                options['upload_scan_settings'] = options['upload_settings']
        else:
            if not os.path.isfile(options['settings']):
                options['upload_settings'] = str("{}".format(os.path.join(os.path.dirname(__file__),
                                                                   self.webinspect_dir, 'settings',
                                                                   options['settings'] + '.xml')))
            else:
                options['upload_settings'] = options['settings']
                # Settings is used later by the api so we need to cut off the filepath info
                options['settings'] = re.search('.*/(.*)\.xml', options['settings']).group(1)

        # if login macro has been specified, ensure it's uploaded.
        if options['login_macro']:
            if options['upload_webmacros']:
                # add macro to existing list.
                options['upload_webmacros'].append(options['login_macro'])
            else:
                # add macro to new list
                options['upload_webmacros'] = []
                options['upload_webmacros'].append(options['login_macro'])

        # if workflow macros have been provided, ensure they are uploaded
        if options['workflow_macros']:
            if options['upload_webmacros']:
                # add macros to existing list
                options['upload_webmacros'].extend(options['workflow_macros'])
            else:
                # add macro to new list
                options['upload_webmacros'] = list(options['workflow_macros'])

        if options['upload_webmacros']:
            try:
                # trying to be clever, remove any duplicates from our upload list
                options['upload_webmacros'] = list(set(options['upload_webmacros']))
                corrected_paths = []
                for webmacro in options['upload_webmacros']:
                    if not os.path.isfile(webmacro):
                        corrected_paths.append(str("{}".format(os.path.join(os.path.dirname(__file__),
                                                     self.webinspect_dir, 'webmacros',
                                                     webmacro + '.webmacro'))))
                    else:
                        corrected_paths.append(webmacro)
                options['upload_webmacros'] = corrected_paths

            except (AttributeError, TypeError) as e:
                Logger.app.error("The {0} is unable to be assigned! {1}".format(options['upload_webmacros'], e))

        # if upload_policy provided explicitly, follow that. otherwise, default to scan_policy if provided
        if options['upload_policy']:
            if not os.path.isfile(options['upload_policy']):
                options['upload_policy'] = str("{}".format(os.path.join(os.path.dirname(__file__),
                                                           self.webinspect_dir, 'policies',
                                                           options['upload_policy'] + '.policy')))

        elif options['scan_policy']:
            if not os.path.isfile(options['scan_policy']):
                options['upload_policy'] = str("{}".format(os.path.join(os.path.dirname(__file__),
                                                           self.webinspect_dir, 'policies',
                                                           options['scan_policy'] + '.policy')))
            else:
                options['upload_policy'] = options['scan_policy']

        # Determine the targets specified in a settings file
        targets = self.__getScanTargets__(options['upload_settings'])

        # Unless explicitly stated --allowed_hosts by default will use all values from --start_urls
        if not options['allowed_hosts']:
            options['allowed_hosts'] = options['start_urls']

        try:
            webinspect_dict['webinspect_settings'] = options['settings']
            webinspect_dict['webinspect_scan_name'] = options['scan_name']
            webinspect_dict['webinspect_upload_settings'] = options['upload_settings']
            webinspect_dict['webinspect_upload_policy'] = options['upload_policy']
            webinspect_dict['webinspect_upload_webmacros'] = options['upload_webmacros']
            webinspect_dict['webinspect_overrides_scan_mode'] = options['scan_mode']
            webinspect_dict['webinspect_overrides_scan_scope'] = options['scan_scope']
            webinspect_dict['webinspect_overrides_login_macro'] = options['login_macro']
            webinspect_dict['webinspect_overrides_scan_policy'] = options['scan_policy']
            webinspect_dict['webinspect_overrides_scan_start'] = options['scan_start']
            webinspect_dict['webinspect_overrides_start_urls'] = options['start_urls']
            webinspect_dict['webinspect_scan_targets'] = targets
            webinspect_dict['webinspect_workflow_macros'] = options['workflow_macros']
            webinspect_dict['webinspect_allowed_hosts'] = options['allowed_hosts']
            webinspect_dict['webinspect_scan_size'] = options['size'] if options['size'] else self.default_size
            webinspect_dict['fortify_user'] = options['fortify_user']

        except argparse.ArgumentError as e:
            Logger.app.error("There was an error in the options provided!: ".format(e))

        return webinspect_dict

    def fetch_webinspect_configs(self):
        full_path = os.path.join(os.path.dirname(__file__), self.webinspect_dir)
        try:
            if not os.path.isdir(full_path):
                Logger.console.info(
                    "Fetching the WebInspect configurations from {}\n".format(full_path))
                Repo.clone_from(self.webinspect_git, full_path)

            else:
                Logger.console.info(
                    "Updating your WebInspect configurations from {}.format(full_path))
                repo = Repo.init(full_path)
                repo.git.reset('--hard')
                repo.remotes.origin.pull()
        # TODO: Need an exit here
        #Cmd('git') failed due to: exit code(128)
        except (CalledProcessError, AttributeError) as e:
            Logger.app.error("Uh oh something is wrong with your WebInspect configurations!!".format(e))
