#!/usr/bin/env python
#  -*- coding: utf-8 -*-


__author__ = "Brandon Spruth (brandon.spruth2@target.com), Jim Nelson (jim.nelson2@target.com)"
__copyright__ = "(C) 2017 Target Brands, Inc."
__contributors__ = ["Brandon Spruth", "Jim Nelson"]
__status__ = "Production"
__license__ = "MIT"

try:
    from signal import *
    import urlparse
    from urlparse import urlparse
    import httplib
except ImportError: #Python3
    import html.entities as htmlentitydefs
    import urllib.parse as urlparse
    import html.parser as HTMLParser
    import httplib2
try: #Python3
    import urllib.request as urllib
except:
    import urllib
import os, datetime
import requests.exceptions
import json
from pyfiglet import Figlet
from git.exc import GitCommandError
from contextlib import contextmanager
from webbreaker import __version__ as version
from webbreaker.webbreakerlogger import Logger
from webbreaker.webbreakerargs import WebBreakerArgs
from webbreaker.webbreakerconfig import WebBreakerConfig
import webbreaker.webbreakerhelper
from webbreaker.webinspectclient import WebinspectClient
from webbreaker.webinspectconfig import WebInspectConfig
from webbreaker.notifiers import database

handle_scan_event = None
reporter = None

# Use a closure for events related to scan status changes
def create_scan_event_handler(webinspect_client, scan_id, webinspect_settings):
    def scan_event_handler(event_type, external_termination=False):

        event = {}
        event['scanid'] = scan_id
        event['server'] = urlparse(webinspect_client.url).geturl()
        event['scanname'] = webinspect_settings['webinspect_scan_name']
        event['event'] = event_type
        event['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        event['subject'] = 'WebBreaker ' + event['event']

        if webinspect_settings['webinspect_allowed_hosts']:
            event['targets'] = webinspect_settings['webinspect_allowed_hosts']
        else:
            event['targets'] = webinspect_settings['webinspect_scan_targets']

        reporter.report(event)

        if external_termination:
            webinspect_client.stop_scan(scan_id)

    return scan_event_handler

# Special function here - called only when we're in a context (defined below) of intercepting process-termination
# signals. If, while a scan is executing, WebBreaker receives a termination signal from the OS, we want to
# handle that as a scan-end event prior to terminating. So, this function will be called by the python signal
# handler within the scan-running context.
def write_end_event(*args):
    handle_scan_event('scan_end', external_termination=True)
    os._exit(0)


@contextmanager
def scan_running():
    # Intercept the "please terminate" signals
    original_sigint_handler = getsignal(SIGINT)
    original_sigabrt_handler = getsignal(SIGABRT)
    original_sigterm_handler = getsignal(SIGTERM)
    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, write_end_event)
    try:
        yield
    except:
        raise
    finally:
        # Go back to normal signal handling
        signal(SIGABRT, original_sigabrt_handler)
        signal(SIGINT, original_sigint_handler)
        signal(SIGTERM, original_sigterm_handler)


def save_issues(webinspect_client, scanid, webinspect_settings):

    try:
        database_settings = WebBreakerConfig().parse_database_settings()
        db = database.DatabaseNotifier(database_settings)
        all_issues = webinspect_client.get_scan_issues(scan_guid=scanid)
        t = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        for issues in json.loads(all_issues):
            issue={}
            issue['scanid'] = scanid
            issue['scanname'] = webinspect_settings['webinspect_scan_name']
            issue['timestamp'] = t
            issue['issue_json'] = json.dumps(issues)
            db.issue_export(issue)
    except Exception:
        pass


def main():
    # Show something pretty to start
    f = Figlet(font='slant')
    # TODO: change to appropriate log level, such as logger.info or another level for stanza to be sent to console
    Logger.file_logr.critical("\n\n{0}Version {1}\n".format(f.renderText('WebBreaker'), version))
    Logger.file_logr.critical("logging to file: {0}".format(Logger.file_logr.logfilepath))

    # Get the DAST command to run. Only option for now - webinspect. If it's there, we're ok to continue.
    command = webbreaker.webbreakerhelper.WebBreakerHelper.getcommand()
    Logger.file_logr.debug("Running DAST command '{}'".format(str(command)))

    # Setup our configuration...
    webinspect_config = WebInspectConfig()

    # ...and settings...
    try:
        webinspect_settings = webinspect_config.parse_webinspect_options(WebBreakerArgs().webinspect())
    except AttributeError as e:
        Logger.file_logr.error("Your configuration or setting is incorrect {}!!!".format(e))

    # ...as well as pulling down webinspect server config files from github...
    try:
        webinspect_config.fetch_webinspect_configs()
    except GitCommandError as e:
        Logger.file_logr.critical("{} does not have permission to access the git repo: {}".format(
            webinspect_config.webinspect_git, e))

    # ...and create a reporter for notifications of scan lifecycle...
    global reporter
    reporter = WebBreakerConfig().create_reporter()

    # OK, we're ready to actually do something now

    # The webinspect client is our point of interaction with the webinspect server farm
    try:
        webinspect_client = WebinspectClient(webinspect_settings)
    except (UnboundLocalError, EnvironmentError) as e:
        Logger.file_logr.critical("Incorrect WebInspect configurations found!! {}".format(str(e)))
        exit(1)

    # if a scan policy has been specified, we need to make sure we can find/use it
    if webinspect_client.scan_policy:
        # two happy paths: either the provided policy refers to an existing builtin policy, or it refers to
        # a local policy we need to first upload and then use.

        if str(webinspect_client.scan_policy).lower() in [str(x[0]).lower() for x in webinspect_config.mapped_policies]:
            idx = [x for x, y in enumerate(webinspect_config.mapped_policies) if y[0] == str(webinspect_client.scan_policy).lower()]
            policy_guid = webinspect_config.mapped_policies[idx[0]][1]
            Logger.file_logr.debug("Provided scan_policy {} listed as builtin policyID {}".format(webinspect_client.scan_policy, policy_guid))
            Logger.file_logr.debug("Checking to make sure a policy with that ID exists in WebInspect.")
            if not webinspect_client.policy_exists(policy_guid):
                Logger.file_logr.error(
                    "Scan policy {} cannot be located on server. Stopping".format(webinspect_client.scan_policy))
                exit(1)
            else:
                Logger.file_logr.debug("Found policy {} in WebInspect.".format(policy_guid))
        else:
            # Not a builtin. Assume that caller wants the provided policy to be uploaded
            Logger.file_logr.debug("Provided scan policy is not built-in, so will assume it needs to be uploaded.")
            webinspect_client.upload_policy()
            policy = webinspect_client.get_policy_by_name(webinspect_client.scan_policy)
            if policy:
                policy_guid = policy['uniqueId']
            else:
                Logger.file_logr.error("Unable to locate uploaded policy. Make sure policy name matches policy file name.")
                exit(1)

        # Change the provided policy name into the corresponding policy id for scan creation.
        policy_id = webinspect_client.get_policy_by_guid(policy_guid)['id']
        webinspect_client.scan_policy = policy_id

    # Upload whatever configurations have been provided...
    if webinspect_client.webinspect_upload_settings:
        webinspect_client.upload_settings()

    if webinspect_client.webinspect_upload_webmacros:
        webinspect_client.upload_webmacros()

    # if there was a provided scan policy, we've already uploaded so don't bother doing it again. hack.
    if webinspect_client.webinspect_upload_policy and not webinspect_client.scan_policy:
        webinspect_client.upload_policy()

    # ... And launch a scan.
    try:
        scan_id = webinspect_client.create_scan()

        global handle_scan_event
        handle_scan_event = create_scan_event_handler(webinspect_client, scan_id, webinspect_settings)
        handle_scan_event('scan_start')

        with scan_running():
            webinspect_client.wait_for_scan_status_change(scan_id)  # execution waits here, blocking call

        status = webinspect_client.get_scan_status(scan_id)
        Logger.file_logr.critical("Scan status has changed to {0}.".format(status))
        if status.lower() != 'complete':  # case insensitive comparison is tricky. this should be good enough for now
            Logger.file_logr.critical('Status is not complete. This is unrecoverable. WebBreaker will exit.')
            handle_scan_event('scan_end')
            exit(1)

        webinspect_client.export_scan_results(scan_id)
        save_issues(webinspect_client, scan_id, webinspect_settings)
        handle_scan_event('scan_end')

        Logger.file_logr.critical('Scan has finished.')
    except (requests.exceptions.ConnectionError, httplib.BadStatusLine, requests.exceptions.HTTPError) as e:
        Logger.file_logr.error("Unable to connect to WebInspect {0}, see also: {1}".format(webinspect_settings['webinspect_url'], e))

    # Log the log to the log (LOL)...
    if scan_id:
        Logger.file_logr.info("Scan log: {}".format(webinspect_client.get_scan_log(scan_guid=scan_id)))

    # And wrap up by writing out the issues we found
    # this should be moved into a function...probably a whole 'nother class, tbh
    if scan_id:
        with open('/tmp/' + webinspect_client.scan_name + '.issues', 'w') as outfile:
            end_date = str(datetime.datetime.now())
            sessions = json.loads(webinspect_client.get_scan_issues(scan_guid=scan_id))
            # inject scan-level data into each issue
            for session in sessions:
                issues = session['issues']
                for issue in issues:
                    issue['scan_name'] = webinspect_settings['webinspect_settings']
                    issue['scan_policy'] = webinspect_settings['webinspect_overrides_scan_policy']
                    issue['end_date'] = end_date
                    outfile.write(json.dumps(issue) + '\n')

    # That's it. We're done.
    Logger.file_logr.critical("Webbreaker complete.")

if __name__ == '__main__':
    main()
