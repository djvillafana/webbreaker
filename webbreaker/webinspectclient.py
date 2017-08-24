#!/usr/bin/env python
# -*-coding:utf-8-*-

import json
import ntpath
import requests
from webinspectapi import WebInspectApi as webinspectapi
from webbreaker.webbreakerlogger import Logger
from webbreaker.webbreakerhelper import WebBreakerHelper
from webbreaker.webinspectconfig import WebInspectConfig
from webbreaker.webinspectjitscheduler import WebInspectJitScheduler

requests.packages.urllib3.disable_warnings()


class WebinspectClient(object):
    def __init__(self, webinspect_setting, endpoint=None):

        # Select an appropriate endpoint if none was provided.
        if not endpoint:
            config = WebInspectConfig()
            lb = WebInspectJitScheduler(endpoints=config.endpoints, size_list=config.sizing,
                                        size_needed=webinspect_setting['webinspect_scan_size'])
            endpoint = lb.get_endpoint()
            if not endpoint:
                raise EnvironmentError("Scheduler found no available endpoints.")

        self.url = endpoint
        self.settings = webinspect_setting['webinspect_settings']
        self.scan_name = webinspect_setting['webinspect_scan_name']
        self.extension = webinspect_setting['extension']
        self.webinspect_upload_settings = webinspect_setting['webinspect_upload_settings']
        self.webinspect_upload_policy = webinspect_setting['webinspect_upload_policy']
        self.webinspect_upload_webmacros = webinspect_setting['webinspect_upload_webmacros']
        self.scan_mode = webinspect_setting['webinspect_overrides_scan_mode']
        self.scan_scope = webinspect_setting['webinspect_overrides_scan_scope']
        self.login_macro = webinspect_setting['webinspect_overrides_login_macro']
        self.scan_policy = webinspect_setting['webinspect_overrides_scan_policy']
        self.scan_start = webinspect_setting['webinspect_overrides_scan_start']
        self.start_urls = webinspect_setting['webinspect_overrides_start_urls']
        self.workflow_macros = webinspect_setting['webinspect_workflow_macros']
        self.allowed_hosts = webinspect_setting['webinspect_allowed_hosts']
        self.scan_size = webinspect_setting['webinspect_scan_size']
        self.runenv = WebBreakerHelper.check_run_env()

        Logger.file_logr.debug("url: {}".format(self.url))
        Logger.file_logr.debug("settings: {}".format(self.settings))
        Logger.file_logr.debug("scan_name: {}".format(self.scan_name))
        Logger.file_logr.debug("extension: {}".format(self.extension))
        Logger.file_logr.debug("upload_settings: {}".format(self.webinspect_upload_settings))
        Logger.file_logr.debug("upload_policy: {}".format(self.webinspect_upload_policy))
        Logger.file_logr.debug("upload_webmacros: {}".format(self.webinspect_upload_webmacros))
        Logger.file_logr.debug("workflow_macros: {}".format(self.workflow_macros))
        Logger.file_logr.debug("allowed_hosts: {}".format(self.allowed_hosts))
        Logger.file_logr.debug("scan_mode: {}".format(self.scan_mode))
        Logger.file_logr.debug("scan_scope: {}".format(self.scan_scope))
        Logger.file_logr.debug("login_macro: {}".format(self.login_macro))
        Logger.file_logr.debug("scan_policy: {}".format(self.scan_policy))
        Logger.file_logr.debug("scan_start: {}".format(self.scan_start))
        Logger.file_logr.debug("start_urls: {}".format(self.start_urls))

    def __settings_exists__(self):
        try:
            api = webinspectapi(self.url, verify_ssl=False)
            response = api.list_settings()

            if response.success:
                for setting in response.data:
                    if setting in self.settings:
                        return True

        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("Unable to determine if settings exist {}".format(e))
            Logger.file_logr.error("Will proceed as though settings do NOT exist on webinspect server.")

        return False

    def create_scan(self):
        """
        Launches and monitors a scan
        :return: If scan was able to launch, scan_id. Otherwise none.
        """
        overrides = json.dumps(webinspectjson.formatted_settings_payload(self.settings, self.scan_name, self.runenv,
                                                                         self.scan_mode, self.scan_scope,
                                                                         self.login_macro,
                                                                         self.scan_policy, self.scan_start,
                                                                         self.start_urls, self.workflow_macros,
                                                                         self.allowed_hosts))

        api = webinspectapi(self.url, verify_ssl=False)
        response = api.create_scan(overrides)

        logger_response = json.dumps(response, default=lambda o: o.__dict__, sort_keys=True)
        Logger.file_logr.info("Request sent to {0}:\n{1}".format(self.url, overrides))
        Logger.file_logr.info("Response from {0}:\n{1}".format(self.url, logger_response))

        if response.success:
            scan_id = response.data['ScanId']
            #TODO: Change to appropriate log level, such as logger.info
            Logger.file_logr.critical('WebInspect scan launched on {0} your scan id: {1} !!\n'.format(self.url, scan_id))
        else:
            Logger.file_logr.error("No scan was launched! {}".format(response.message))
            return False

        return scan_id

    def export_scan_results(self, scan_id):
        """
        Save scan results to file
        :param scan_id:
        :return:
        """
        # Export scan as a xml for Threadfix or other Vuln Management System
        Logger.file_logr.debug('Exporting scan: {}'.format(scan_id))
        detail_type = 'Full' if self.extension == 'xml' else None
        api = webinspectapi(self.url, verify_ssl=False)
        response = api.export_scan_format(scan_id, self.extension, detail_type)

        if response.success:
            try:
                with open('{0}.{1}'.format(self.scan_name, self.extension), 'wb') as f:
                    logger.critical('Scan results file is available: {0}.{1}'.format(self.scan_name, self.extension))
                    f.write(response.data)
            except UnboundLocalError as e:
                Logger.file_logr.error('Error saving file locally {}'.format(e))
        else:
            Logger.file_logr.error('Unable to retrieve scan results. {} '.format(response.message))

    def get_policy_by_guid(self, policy_guid):
        api = webinspectapi(self.url, verify_ssl=False)
        response = api.get_policy_by_guid(policy_guid)
        if response.success:
            return response.data
        else:
            return None

    def get_policy_by_name(self, policy_name):
        api = webinspectapi(self.url, verify_ssl=False)
        response = api.get_policy_by_name(policy_name)
        if response.success:
            return response.data
        else:
            return None

    def get_scan_issues(self, scan_name=None, scan_guid=None, pretty=False):
        try:

            if scan_name:
                api = webinspectapi(self.url, verify_ssl=False)
                response = api.get_scan_by_name(scan_name)
                if response.success:
                    scan_guid = response.data[0]['ID']
                else:
                    Logger.file_logr.error(response.message)
                    return None

            api = webinspectapi(self.url, verify_ssl=False)
            response = api.get_scan_issues(scan_guid)
            if response.success:
                return response.data_json(pretty=pretty)
            else:
                return None
        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("get_scan_issues failed: {}".format(e))

    def get_scan_log(self, scan_name=None, scan_guid=None):
        try:

            if scan_name:
                api = webinspectapi(self.url, verify_ssl=False)
                response = api.get_scan_by_name(scan_name)
                if response.success:
                    scan_guid = response.data[0]['ID']
                else:
                    Logger.file_logr.error(response.message)
                    return None

            api = webinspectapi(self.url, verify_ssl=False)
            response = api.get_scan_log(scan_guid)
            if response.success:
                return response.data_json()
            else:
                return None
        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("get_scan_log failed: {}".format(e))

    def get_scan_status(self, scan_guid):
        api = webinspectapi(self.url, verify_ssl=False)
        try:
            response = api.get_current_status(scan_guid)
            status = json.loads(response.data_json())['ScanStatus']
            return status
        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("get_scan_status failed: {}".format(e))
            return "Unknown"

    def list_policies(self):
        try:
            api = webinspectapi(self.url, verify_ssl=False)
            response = api.list_policies()

            if response.success:
                for policy in response.data:
                    Logger.file_logr.info("{}".format(policy))
            else:
                Logger.file_logr.info("{}".format(response.message))

        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("list_policies failed: {}".format(e))

    def list_scans(self):

        try:
            api = webinspectapi(self.url, verify_ssl=False)
            response = api.list_scans()

            if response.success:
                for scan in response.data:
                    Logger.file_logr.info("{}".format(scan))
            else:
                Logger.file_logr.info("{}".format(response.message))

        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("list_scans failed: {}".format(e))

    def list_webmacros(self):
        try:
            api = webinspectapi(self.url, verify_ssl=False)
            response = api.list_webmacros()

            if response.success:
                for webmacro in response.data:
                    Logger.file_logr.info("{}".format(webmacro))
            else:
                Logger.file_logr.info("{}".format(response.message))

        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("list_webmacros failed: {}".format(e))

    def policy_exists(self, policy_guid):
        # true if policy exists
        api = webinspectapi(self.url, verify_ssl=False)
        response = api.get_policy_by_guid(policy_guid)
        return response.success

    def stop_scan(self, scan_guid):
        api = webinspectapi(self.url, verify_ssl=False)
        response = api.stop_scan(scan_guid)
        return response.success

    def upload_policy(self):
        # if a policy of the same name already exists, delete it prior to upload
        try:
            api = webinspectapi(self.url, verify_ssl=False)
            # bit of ugliness here. I'd like to just have the policy name at this point but I don't
            # so find it in the full path
            response = api.get_policy_by_name(ntpath.basename(self.webinspect_upload_policy).split('.')[0])
            if response.success and response.response_code == 200:  # the policy exists on the server already
                api = webinspectapi(self.url, verify_ssl=False)
                response = api.delete_policy(response.data['uniqueId'])
                if response.success:
                    Logger.file_logr.debug("Deleted policy {} from server".format(ntpath.basename(self.webinspect_upload_policy).split('.')[0]))
        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("check/deletion of existing policy failed: {}".format(e))

        try:
            api = webinspectapi(self.url, verify_ssl=False)
            response = api.upload_policy(self.webinspect_upload_policy)

            if response.success:
                Logger.file_logr.debug("Uploaded policy {} to server.".format(self.webinspect_upload_policy))
            else:
                Logger.file_logr.error("Error uploading policy {0}. {1}".format(self.webinspect_upload_policy,
                                                                      response.message))

        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("Error uploading policy {}".format(e))

    def upload_settings(self):

        try:
            api = webinspectapi(self.url, verify_ssl=False)
            response = api.upload_settings(self.webinspect_upload_settings)

            if response.success:
                Logger.file_logr.debug("Uploaded settings {} to server.".format(self.webinspect_upload_settings))
            else:
                Logger.file_logr.error("Error uploading settings {0}. {1}".format(self.webinspect_upload_settings,
                                                                        response.message))

        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("Error uploading settings {}".format(e))

    def upload_webmacros(self):
        try:
            for webmacro in self.webinspect_upload_webmacros:
                api = webinspectapi(self.url, verify_ssl=False)
                response = api.upload_webmacro(webmacro)
                if response.success:
                    Logger.file_logr.debug("Uploaded webmacro {} to server.".format(webmacro))
                else:
                    Logger.file_logr.error("Error uploading webmacro {0}. {1}".format(webmacro, response.message))

        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("Error uploading webmacro {}".format(e))

    def wait_for_scan_status_change(self, scan_id):
        """
        Blocking call, will remain in this method until status of scan changes
        :param scan_id:
        :return:
        """
        # WebInspect Scan has started, wait here until it's done
        api = webinspectapi(self.url, verify_ssl=False)
        response = api.wait_for_status_change(scan_id)  # this line is the blocker

        if response.success:
            Logger.file_logr.debug('Scan status {}'.format(response.data))
        else:
            Logger.file_logr.debug('Scan status not known because: {}'.format(response.message))
