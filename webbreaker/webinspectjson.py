#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from webbreaker.webbreakerlogger import Logger


json_scan_settings = {
    "settingsName": "",
    "overrides": {
        "scanName": ""
         }
    }


def formatted_settings_payload(settings, scan_name, runenv, scan_mode, scan_scope, login_macro, scan_policy,
                               scan_start, start_urls, workflow_macros, allowed_hosts):

    global json_scan_settings
    json_scan_settings['settingsName'] = settings
    # scanName option
    if runenv == "jenkins":
        json_scan_settings['overrides']['scanName'] = os.getenv('BUILD_TAG')
    else:
        json_scan_settings['overrides']['scanName'] = scan_name

    # crawlAuditMode option
    if scan_mode:
        json_scan_settings['overrides']['crawlAuditMode'] = ""
        if scan_mode == "scan":
            json_scan_settings['overrides']['crawlAuditMode'] = 'AuditOnly'
        elif scan_mode == "crawl":
            json_scan_settings['overrides']['crawlAuditMode'] = 'CrawlOnly'
        else:
            json_scan_settings['overrides']['crawlAuditMode'] = 'CrawlAndAudit'

    if scan_scope:
        json_scan_settings['overrides']['scanScope'] = ""
        if scan_scope == "all":
            json_scan_settings['overrides']['scanScope'] = 'Unrestricted'
        elif scan_scope == "strict":
            json_scan_settings['overrides']['scanScope'] = 'Self'
        elif scan_scope == "children":
            json_scan_settings['overrides']['scanScope'] = 'Children'
        elif scan_scope == "ancestors":
            json_scan_settings['overrides']['scanScope'] = 'Ancestors'
        else:
            #json_scan_settings['overrides']['scanScope'] = 'None'
            Logger.file_logr.error("Usage: all, strict, children, or ancestors are options! \n"
                         "The value {} for scan_scope is not available!".format(scan_scope))

    if login_macro:
        json_scan_settings['overrides']['loginMacro'] = login_macro

    if scan_policy:
        json_scan_settings['overrides']['policyId'] = scan_policy

    if scan_start:
        json_scan_settings['overrides']['startOption'] = ""
        if scan_start == "url":
            json_scan_settings['overrides']['startOption'] = "Url"
        elif scan_start == "macro":
            json_scan_settings['overrides']['startOption'] = "Macro"
        else:
            Logger.file_logr.error("usage: url or macro are options NOT scan_start: {}!".format(scan_start))

    if start_urls:
        json_scan_settings['overrides']['startUrls'] = start_urls

    if workflow_macros:
        json_scan_settings['overrides']['workflowMacros'] = workflow_macros

    if allowed_hosts:
        json_scan_settings['overrides']['allowedHosts'] = allowed_hosts

    return json_scan_settings
