#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from contextlib import contextmanager
import os, datetime
from signal import *
import json
try:
    import urlparse
    from urlparse import urlparse
except ImportError: #Python3
    import urllib.parse as urlparse

from webbreaker.notifiers import database
from webbreaker.webbreakerconfig import WebBreakerConfig

handle_scan_event = None
reporter = WebBreakerConfig().create_reporter()

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