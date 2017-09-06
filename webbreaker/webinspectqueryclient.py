#!/usr/bin/env python
# -*-coding:utf-8-*-

import json
import ntpath
import requests
import webinspectapi.webinspect as webinspectapi
from webbreaker.webbreakerlogger import Logger
from webbreaker.webbreakerhelper import WebBreakerHelper
from webbreaker.webinspectconfig import WebInspectConfig
from webbreaker.webinspectjitscheduler import WebInspectJitScheduler

requests.packages.urllib3.disable_warnings()


class WebinspectQueryClient(object):
    def __init__(self, host, protocol):
        self.host = protocol + '://' + host
        Logger.file_logr.debug("WebinspectQueryClient created for host: {}".format(self.host))

    def get_scan_by_name(self, scan_name):
        """
        Search Webinspect server for a scan matching scan_name
        :param scan_name:
        :return: List of search results
        """
        api = webinspectapi.WebInspectApi(self.host, verify_ssl=False)
        return api.get_scan_by_name(scan_name).data

    def export_scan_results(self, scan_id, scan_name, extension):
        """
        Save scan results to file
        :param scan_id:
        :return:
        """
        # Export scan as a xml for Threadfix or other Vuln Management System
        Logger.file_logr.debug('Exporting scan: {}'.format(scan_id))
        detail_type = 'Full' if extension == 'xml' else None
        api = webinspectapi.WebInspectApi(self.host, verify_ssl=False)
        response = api.export_scan_format(scan_id, extension, detail_type)

        if response.success:
            try:
                with open('{0}.{1}'.format(scan_name, extension), 'wb') as f:
                    Logger.file_logr.critical('Scan results file is available: {0}.{1}'.format(scan_name, extension))
                    f.write(response.data)
            except UnboundLocalError as e:
                Logger.file_logr.error('Error saving file locally {}'.format(e))
        else:
            Logger.file_logr.error('Unable to retrieve scan results. {} '.format(response.message))



    def list_scans(self):
        """
        List all scans found on host
        :param scan_id:
        :return:
        """
        api = webinspectapi.WebInspectApi(self.host, verify_ssl=False)
        response = api.list_scans()
        if response.success:
            for scan in response.data:
                Logger.file_logr.critical("{0:80} {1:40} {2:10}".format(scan['Name'], scan['ID'], scan['Status']))
        else:
            Logger.file_logr.critical("{}".format(response.message))

