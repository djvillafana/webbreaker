#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
import requests.packages.urllib3
from requests.auth import HTTPBasicAuth
import fortifyjson
from webbreaker.webbreakerhelper import WebBreakerHelper
from webbreaker.webbreakerlogger import Logger

requests.packages.urllib3.disable_warnings()
project_version_id = ""


class FortifyClient(object):
    def __init__(self, fortify_url, project_template, application_name, fortify_secret, fortify_user, scan_name, extension):
        self.ssc_server             = fortify_url
        self.project_template       = project_template
        self.application_name       = application_name
        self.user                   = fortify_user
        self.password               = fortify_secret
        self.fortify_version        = scan_name
        self.extension              = extension
        self.runenv                 = WebBreakerHelper.check_run_env()

    def __gettoken__(self):
        try:
            Logger.file_logr.debug("Fortify SSC Server settings are:")
            Logger.file_logr.debug("================================")
            Logger.file_logr.debug("ssc_server: {}".format(self.ssc_server))
            Logger.file_logr.debug("user: {}".format(self.user))
            Logger.file_logr.debug("password: {}".format('*' * len(self.password)))
            Logger.file_logr.debug("application_name: {}".format(self.application_name))
            Logger.file_logr.debug("project_template: {}".format(self.project_template))
            Logger.file_logr.debug("version_name: {}".format(self.fortify_version))
            Logger.file_logr.debug("================================\n")
        except TypeError as e:
            Logger.file_logr.info(
                "Unable to create project version in Fortify SSC, due to empty or incorrect credentials: {} ".format(e))
        try:
            response = requests.post(self.ssc_server + '/api/v1/auth/obtain_token/', verify=True,
                                     headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth(self.user, self.password))

            response.raise_for_status()
            token_data = json.loads(response.text)
            authtoken = token_data['data']['token']

            return authtoken

        except (requests.exceptions.SSLError, requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            Logger.file_logr.warn("Connection to Fortify SSC Server was unsuccessful for getToken!: {}".format(e))
        except (ValueError, UnboundLocalError, TypeError, AttributeError) as e:
            Logger.file_logr.warn("Unable to create a session at {0}, due to incorrect credentials ! {1}".format(self.ssc_server, e))

    def __getissuetemplateid__(self):
        auth_token = self.__gettoken__()

        issue_template_endpoint_uri = "/api/v1/issueTemplates"
        url = self.ssc_server + issue_template_endpoint_uri + "?q=name:" + "\"" + self.project_template + "\""
        response = requests.get(url, headers={'Authorization': 'FortifyToken ' + auth_token}, verify=False)

        response.raise_for_status()
        issuetemplateid = ""

        if response.status_code == 200:
            json_issue_template = json.loads(response.text)
            data_list = json_issue_template['data']

            for data in data_list:
                if data['name'] == self.project_template:
                    issuetemplateid = data['id']

        if issuetemplateid == "":
            return -1
        return issuetemplateid

    # TODO: create classmethod for __application_exists for validation
    def __application_exists__(self):
        auth_token = self.__gettoken__()

        project_endpoint_uri = "/api/v1/projectVersions"
        url = self.ssc_server + project_endpoint_uri
        response = requests.get(url, headers={'Authorization': 'FortifyToken ' + auth_token}, verify=False)
        response.raise_for_status()

        projects = json.loads(response.text)
        project_list = projects['data']
        for project in project_list:
            if self.application_name == project['project']['name']:
                application_id = project['project']['id']
                return application_id

    def __existing_project_version_id__(self):
        auth_token = self.__gettoken__()

        project_endpoint_uri = "/api/v1/projectVersions"
        url = self.ssc_server + project_endpoint_uri

        response = requests.get(url, headers={'Authorization': 'FortifyToken ' + auth_token}, verify=False)
        response.raise_for_status()

        if response.status_code == 200:
            projects = json.loads(response.text)
            project_list = projects['data']

            for project in project_list:
                if project['name'] == self.fortify_version:
                    project_version_id = project['id']
                    return project_version_id

    def __post_bulk__(self, data):
        auth_token = self.__gettoken__()

        bulk_endpoint_uri = "/api/v1/bulk"
        url = self.ssc_server + bulk_endpoint_uri
        response = requests.post(url, data, headers={'Content-Type': 'application/json',
                                                     'Authorization': 'FortifyToken ' + auth_token}, verify=False)
        response.raise_for_status()
        if response.status_code == 200:
            return 0
        return -1

    def create_project(self):
        global project_version_id
        auth_token = self.__gettoken__()

        try:
            issue_template_id = self.__getissuetemplateid__()
            data = json.dumps(
                fortifyjson.formatted_application_version_payload(self.application_name, self.fortify_version,
                                                                     issue_template_id, self.runenv))
            existing_project_version_id = self.__existing_project_version_id__()

            if existing_project_version_id:
                Logger.file_logr.debug("The Project Version: {}, was previously created!".format(self.fortify_version))
                project_version_id = existing_project_version_id
                #global project_version_id

            else:
                response = requests.post(self.ssc_server + "/api/v1/projectVersions", data,
                                         headers={'Content-Type': 'application/json',
                                                  'Authorization': 'FortifyToken ' + auth_token}, verify=False)
                if response.status_code == 201:
                    json_project_version = json.loads(response.text)

                    project_version_id = json_project_version['data']['id']
                    #global project_version_id

                    attributes_uri = self.ssc_server + "/api/v1/projectVersions/" + str(
                        project_version_id) + "/attributes"
                    responsibilities_uri = self.ssc_server + "/api/v1/projectVersions/" + str(
                        project_version_id) + "/responsibilities"
                    action_uri = self.ssc_server + "/api/v1/projectVersions/" + str(
                        project_version_id) + "/action"
                    appversion = self.ssc_server + "/api/v1/projectVersions/" + str(
                        project_version_id) + "?hideProgress=true"

                    bulk_data = json.dumps(
                        fortifyjson.formatted_bulk_ssc_payload(attributes_uri, responsibilities_uri, action_uri,
                                                                  appversion))
                    if self.__post_bulk__(bulk_data) == 0:
                        Logger.file_logr.info("Fortify SSC settings:")
                        Logger.file_logr.info("================================")
                        Logger.file_logr.info("Fortify SSC URL: {}".format(self.ssc_server))
                        Logger.file_logr.info("Fortify SSC Template: {}".format(json_project_version['data']['issueTemplateName']))
                        Logger.file_logr.info("Fortify SSC Project: {}".format(json_project_version['data']['project']['name']))
                        Logger.file_logr.info("Fortify SSC Version: {}".format(json_project_version['data']['name']))
                        Logger.file_logr.info("================================\n")
                    else:
                        Logger.file_logr.debug("Error creating project/application version in Fortify SSC!")

                if not response.status_code // 100 == 2:
                    if response.status_code == 400:
                        Logger.file_logr.debug("Error: The Fortify SSC Project/Application {}, is ".format(response.text))
                    elif response.status_code == 500:
                        Logger.file_logr.debug("Error: There was an issue with The Fortify SSC Project/Application {0},"
                                     " is not available, please create one...".format(self.application_name))
                    else:
                        Logger.file_logr.debug("Error: Unexpected response {}".format(response.text))

        except requests.exceptions.RequestException as e:
            Logger.file_logr.debug("Error: SSL Error or Invalid URL{}".format(e))

    def __getfiletoken__(self):
        auth_token = self.__gettoken__()

        try:
            filetoken_endpoint_uri = "/api/v1/fileTokens"
            url = self.ssc_server + filetoken_endpoint_uri

            data = json.dumps(fortifyjson.formatted_filetoken_payload())

            response = requests.post(url, data,
                                     headers={'Content-Type': 'application/json',
                                              'Authorization': 'FortifyToken ' + auth_token}, verify=False)
            response.raise_for_status()
            filetoken_data = json.loads(response.text)
            filetoken = filetoken_data['data']['token']

            return filetoken

        except (requests.exceptions.SSLError, requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            #logger.error("Connection to Fortify SSC Server was unsuccessful on getting token!: {}".format(e))
            raise e
        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("Unable to establish a Fortify SSC session! {}".format(e))

    def upload_scan(self):
        auth_token = self.__gettoken__()
        file_token = self.__getfiletoken__()

        try:
            upload_endpoint_uri = "/upload/resultFileUpload.html?mat="
            url = self.ssc_server + upload_endpoint_uri

            files = {'file': ('{0}.{1}'.format(self.fortify_version, self.extension),
                              open('{0}.{1}'.format(self.fortify_version, self.extension), 'rb'),)}

            response = requests.post(url + file_token, {"entityId": project_version_id, "Upload": "Submit Query"},
                                     verify=False, files=files, headers={'Authorization': 'FortifyToken ' + auth_token})
            #Let us know we were successful
            Logger.file_logr.info("Your scan file {0}.{1}, has been successfully uploaded to {2}!".format(self.fortify_version,
                                                                                                self.extension,
                                                                                                self.ssc_server))
            if response.status_code == 200:
                response.raise_for_status()
            else:
                Logger.file_logr.error("Error uploading {0}.{1}!!!".format(self.fortify_version, self.extension, ))

            if not response.status_code // 100 == 2:
                Logger.file_logr.error("Error: Unexpected response {}".format(response.text))

        except IOError as e:
            Logger.file_logr.error("Unable to upload file {0}.{1} to {2}".format(
                self.fortify_version, self.extension, self.ssc_server, e))
        except (requests.exceptions.SSLError, requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            Logger.file_logr.error("Connection to {0} was unsuccessful!: {1}".format(self.ssc_server, e))
        except (ValueError, UnboundLocalError) as e:
            Logger.file_logr.error("No token provided or request sent to Fortify SSC is invalid: {}".format(e))
