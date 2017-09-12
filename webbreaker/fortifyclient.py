#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import socket
from webbreaker.webbreakerhelper import WebBreakerHelper
from webbreaker.webbreakerlogger import Logger
from fortifyapi.fortify import FortifyApi


class FortifyClient(object):
    def __init__(self, fortify_url, project_template=None, application_name=None, fortify_username=None,
                 fortify_password=None, scan_name=None, extension=None, token=None):
        self.ssc_server = fortify_url
        self.project_template = project_template
        self.application_name = application_name
        self.user = fortify_username
        self.password = fortify_password
        self.fortify_version = scan_name
        self.extension = extension
        self.runenv = WebBreakerHelper.check_run_env()
        self.token = token
        if not token:
            self.token = self.get_token()

        if not self.token:
            Logger.app.critical("Unable to obtain a Fortify API token.")
            raise ValueError("Unable to obtain a Fortify API token.")

    def get_token(self):
        try:
            api = FortifyApi(self.ssc_server, username=self.user, password=self.password, verify_ssl=False)
            response = api.get_token()
            if response.success:
                token = response.data['data']['token']
                return token
            else:
                Logger.app.critical(response.message)
        except Exception as e:
            Logger.app.critical("Exception while getting Fortify token: {0}".format(e.message))

        return None

    def __get_project_id__(self, project_name):
        api = FortifyApi(self.ssc_server, token=self.token, verify_ssl=False)
        response = api.get_projects()
        if response.success:
            for project in response.data['data']:
                if project['name'] == project_name:
                    return project['id']
        return None

    def __project_version_description__(self):
        if self.runenv == "jenkins":
            return "WebInspect scan from WebBreaker " + os.getenv('JOB_URL', "jenkins server")
        else:
            return "WebBreaker scan from WebBreaker host " + socket.getfqdn()

    def __create_project_version__(self):
        """
        Create, add required attributes to, and commit a new project version
        :return: The new project_version_id if successful. Otherwise, None.
        """
        api = FortifyApi(self.ssc_server, token=self.token, verify_ssl=False)
        try:
            # It's kinda dumb for this api call to require both project name and id?
            response = api.create_project_version(project_name=self.application_name,
                                                  project_id=self.__get_project_id__(self.application_name),
                                                  project_template=self.project_template,
                                                  version_name=self.fortify_version,
                                                  description=self.__project_version_description__())

            if not response.success:
                raise ValueError("Failed to create a new project version")

            project_version_id = response.data['data']['id']

            # At Target, only one attribute is required
            response = api.add_project_version_attribute(project_version_id=project_version_id,
                                                         attribute_definition_id=self.__get_attribute_definition_id__(
                                                             search_expression='name:"CI Number"'),
                                                         value='New WebBreaker Application',
                                                         values=[])
            if not response.success:
                raise ValueError("Failed to create required project version attribute")

            response = api.commit_project_version(project_version_id=project_version_id)
            if not response.success:
                raise ValueError("Failed to commit new project version")
                #Logger.app.debug("Created new project version id {0}".format(project_version_id))
            return project_version_id

        except Exception as e:
            Logger.app.critical("Exception trying to create project version. {0}".format(e.message))

        return None

    def __get_attribute_definition_id__(self, search_expression):
        api = FortifyApi(self.ssc_server, token=self.token, verify_ssl=False)
        response = api.get_attribute_definition(search_expression=search_expression)
        if response.success:
            return response.data['data'][0]['id']
        else:
            return None

    def __get_project_version__(self):
        """
        If a project version already exists, return it's project_version_id
        If a project version does NOT exist, create it and return it's project_version_id
        If none of the above succeeds, log the reason(s) and return None
        :return:
        """
        api = FortifyApi(self.ssc_server, token=self.token, verify_ssl=False)
        try:
            response = api.get_project_versions()  # api should support a search expression here. alas...
            if response.success:
                for project_version in response.data['data']:
                    if project_version['project']['name'] == self.application_name:
                        if project_version['name'] == self.fortify_version:
                            # we have a matching project version
                            Logger.app.debug("Found existing project version {0}".format(project_version['id']))
                            return project_version['id']
                # Didn't find a matching project version, verify that our project exists
                for project_version in response.data['data']:
                        if project_version['project']['name'] == self.application_name:
                            # Our project exsits, so create a new version
                            return self.__create_project_version__()
                # Let upload_scan know that our project doesn't exist
                return -2
            elif "401" in response.message:
                # Avoid printing error for invalid token. Return -1 to reauth
                return -1
            else:
                Logger.app.critical("Failed to get project version. {0}".format(response.message))
        except Exception as e:
            Logger.app.critical("Exception trying to get project version. {0}".format(e.message))

        return None

    def upload_scan(self, file_name):
        api = FortifyApi(self.ssc_server, token=self.token, verify_ssl=False)
        project_version_id = self.__get_project_version__()
        # If our project doesn't exist, exit upload_scan
        if project_version_id == -2:
           return -2
        if project_version_id == -1:
            return -1
        if not project_version_id:
            project_version_id = self.__create_project_version__()
        if project_version_id:
            response = api.upload_artifact_scan(file_path=('{0}.{1}'.format(file_name, self.extension)),
                                                project_version_id=project_version_id)

        if response.success:
            Logger.console.info(
                "Your scan file {0}.{1}, has been successfully uploaded to {2}!".format(file_name,
                                                                                        self.extension,
                                                                                        self.ssc_server))
        elif not response.success and "401" in response.message:
            return response.response_code
        else:
            Logger.console.error("Error uploading {0}.{1}!!!".format(self.fortify_version, self.extension))
            Logger.app.error("Error uploading {0}.{1}!!!".format(self.fortify_version, self.extension))
        return response

    def list_projects(self):
        api = FortifyApi(self.ssc_server, token=self.token, verify_ssl=False)
        response = api.get_projects()
        if response.success:
            Logger.console.info("{0:^5} {1:30}".format('ID', 'Name'))
            Logger.console.info("{0:5} {1:30}".format('-'*5, '-'*30))
            for proj in response.data['data']:
                Logger.console.info("{0:^5} {1:30}".format(proj['id'], proj['name']))
        return None

    def list_versions(self):
        api = FortifyApi(self.ssc_server, token=self.token, verify_ssl=False)
        response = api.get_project_versions()
        if response.success:
            Logger.console.info("{0:^5} {1:30}".format('ID', 'Name'))
            Logger.console.info("{0:5} {1:30}".format('-'*5, '-'*30))
            for version in response.data['data']:
                Logger.console.info("{0:^5} {1:30}".format(version['id'], version['name']))
        elif not response.success and "401" in response.message:
            return response.response_code
        return None

    def list_application_versions(self, application):
        api = FortifyApi(self.ssc_server, token=self.token, verify_ssl=False)
        response = api.get_project_versions()
        if response.success:
            Logger.console.info("{0:^5} {1:30}".format('ID', 'Name'))
            Logger.console.info("{0:5} {1:30}".format('-' * 5, '-' * 30))
            for version  in response.data['data']:
                if version['project']['name'] == application:
                    Logger.console.info("{0:^5} {1:30}".format(version['id'], version['name']))
        elif not response.success and "401" in response.message:
            return response.response_code
        return None
