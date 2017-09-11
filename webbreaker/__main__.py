#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Brandon Spruth (brandon.spruth2@target.com), Jim Nelson (jim.nelson2@target.com)," \
             "Matt Dunaj (matthew.dunaj@target.com)"
__copyright__ = "(C) 2017 Target Brands, Inc."
__contributors__ = ["Brandon Spruth", "Jim Nelson", "Matthew Dunaj"]
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
import datetime
import requests.exceptions
import json
from git.exc import GitCommandError
import click
from pyfiglet import Figlet
from webbreaker import __version__ as version
from webbreaker.webbreakerlogger import Logger
from webbreaker.webinspectconfig import WebInspectConfig
from webbreaker.webinspectclient import WebinspectClient
from webbreaker.webinspectqueryclient import WebinspectQueryClient
from webbreaker.fortifyclient import FortifyClient
from webbreaker.fortifyconfig import FortifyConfig
from webbreaker.webinspectscanhelpers import create_scan_event_handler
from webbreaker.webinspectscanhelpers import scan_running


handle_scan_event = None
reporter = None


class Config(object):
    def __init__(self):
        self.debug = False

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--help', help='Enter a product command: webinspect or fortify')
@pass_config
def cli(config, help):
    """WebBreaker is a Dynamic Application Security Test Orchestration (DASTO) product, with API support for.
    WebInspect and Fortify SSC, more commercial products to be added in the future."""

    # Show something pretty to start
    f = Figlet(font='slant')
    Logger.console.info("\n\n{0}Version {1}\n".format(f.renderText('WebBreaker'), version))
    Logger.console.info("Logging to files: {}".format(Logger.app_logfile))
    config.help = help


@cli.group(help="""WebInspect is dynamic application security testing software for assessing security of Web
applications and Web services.""")
@pass_config
def webinspect(config):
    pass


@webinspect.command()
@click.option('--scan_name',
              type=str,
              required=False,
              help="Specify name of scan --scan_name ${BUILD_TAG}")
@click.option('--settings',
                type=str,
                default='Default',
                required=True,
                help="""Specify name of settings file, without the .xml extension. WebBreaker will 
                 by default try to locate this file in in the repo found in webinspect.ini. If your 
                 file is not in the repo, you may instead pass an absolute path to the file""")
@click.option('--size',
              required=False,
              type=click.Choice(['medium', 'large']),
              help="Size of scanner required. Valid values if provided are 'medium' or 'large'")
@click.option('--scan_mode',
              required=False,
              type=click.Choice(['crawl', 'scan', 'all']),
              help="Overrides the setting scan mode value.  Acceptable values are crawl, scan, or all.")
@click.option('--scan_scope',
              required=False,
              help="Overrides the scope value.  Acceptable values are all, strict, children, and ancestors.")
@click.option('--login_macro',
              required=False,
              help="Overrides existing or adds a recorded login sequence to authenticate to the targeted application")
@click.option('--scan_policy',
              required=False,
              help="""Are either custom or built-in WebInspect policies, for example \n
                    AggressiveSQLInjection, AllChecks, ApacheStruts, Application,
                    Assault, CriticalsAndHighs, CrossSiteScripting, Development, Mobile, NoSQLAndNode.js
                    OpenSSLHeartbleed, OWASPTop10ApplicationSecurityRisks2013, OWASPTop10ApplicationSecurityRisks2007
                    OWASPTop10ApplicationSecurityRisks2010, PassiveScan, Platform, PrivilegeEscalation,
                    QA, Quick, Safe, SOAP, SQLInjection, Standard and TransportLayerSecurity""")
@click.option('--scan_start',
              required=False,
              help="Type of scan to be performed list-driven or workflow-driven scan."
                   " Acceptable values are `url` or `macro`")
@click.option('--start_urls',
              required=False,
              multiple=True,
              help="""Enter a single url or multiple each with it's own --start_urls.\n
                    For example --start_urls http://test.example.com --start_urls http://test2.example.com""")
@click.option('--upload_settings',
              required=False,
              help="""--upload_settings, upload setting file to the webinspect host,
                    settings are hosted under webbreaker/etc/webinspect/settings,
                    all settings files end with an .xml extension, the xml extension is not needed
                    and shouldn't be included.""")
@click.option('--upload_policy',
              required=False,
              help="""--upload_policy xss, upload policy file to the webinspect scanner
                    policies are hosted under webbreaker/etc/webinspect/policies, all policy
                    files end with a .policy extension, the policy extension is not needed and
                    shouldn't be included.""")
@click.option('--upload_webmacros',
              required=False,
              help="""--upload_webmacro to the webinspect scanner macros are hosted under
                    webbreaker/etc/webinspect/webmacros, all webmacro files end with the .webmacro extension,
                     the extension should NOT be included.""")
@click.option('--fortify_user',
              required=False,
              help="--fortify_user authenticates the Fortify SSC user for uploading WebInspect `.fpr` formatted scan")
@click.option('--allowed_hosts',
              required=False,
              multiple=True,
              help="""Include the hosts to scan without the protocol or scheme http:// or https://,
                     either a single host or multiple hosts each with it's own --allowed_hosts.
                     If --allowed_hosts is not provided, all hosts explicitly stated within the option,
                     --start_urls will be used.  Keep in mind, if this option is used you must re-enter
                     your host as provided in --start_urls""")
@click.option('--workflow_macros',
              required=False,
              multiple=True,
              help="""--workflow_macros are located under webbreaker/etc/webinspect/webmacros.
                    Overrides the login macro. Acceptable values are login .webmacros files
                    available on the WebInspect scanner to be used.""")
@pass_config
def scan(config, **kwargs):
    # Setup our configuration...
    webinspect_config = WebInspectConfig()

    ops = kwargs.copy()
    # Convert multiple args from tuples to lists
    ops['start_urls'] = list(kwargs['start_urls'])
    ops['allowed_hosts'] = list(kwargs['allowed_hosts'])
    ops['workflow_macros'] = list(kwargs['workflow_macros'])


    # ...as well as pulling down webinspect server config files from github...
    try:
        webinspect_config.fetch_webinspect_configs()
    except GitCommandError as e:
        Logger.console.critical("{} does not have permission to access the git repo, see log {}".format(
            webinspect_config.webinspect_git, Logger.app_logfile))
        Logger.app.critical("{} does not have permission to access the git repo: {}".format(
        webinspect_config.webinspect_git, e))

    # ...and settings...
    try:
        webinspect_settings = webinspect_config.parse_webinspect_options(ops)
    except AttributeError as e:
        Logger.console.info("Your configuration or settings are incorrect see log {}!!!".format(Logger.app_logfile))
        Logger.app.error("Your configuration or settings are incorrect see log {}!!!".format(e))

    # OK, we're ready to actually do something now

    # The webinspect client is our point of interaction with the webinspect server farm
    try:
        webinspect_client = WebinspectClient(webinspect_settings)
    except (UnboundLocalError, EnvironmentError) as e:
        Logger.console.critical("Incorrect WebInspect configurations found!! See log {}".format(str(Logger.app_logfile)))
        Logger.app.critical("Incorrect WebInspect configurations found!! {}".format(str(e)))
        exit(1)

    # if a scan policy has been specified, we need to make sure we can find/use it
    if webinspect_client.scan_policy:
        # two happy paths: either the provided policy refers to an existing builtin policy, or it refers to
        # a local policy we need to first upload and then use.

        if str(webinspect_client.scan_policy).lower() in [str(x[0]).lower() for x in webinspect_config.mapped_policies]:
            idx = [x for x, y in enumerate(webinspect_config.mapped_policies) if y[0] == str(webinspect_client.scan_policy).lower()]
            policy_guid = webinspect_config.mapped_policies[idx[0]][1]
            Logger.console.info("Provided scan_policy {} listed as builtin policyID {}".format(webinspect_client.scan_policy, policy_guid))
            Logger.console.info("Checking to make sure a policy with that ID exists in WebInspect.")
            if not webinspect_client.policy_exists(policy_guid):
                Logger.file_logr.error(
                    "Scan policy {} cannot be located on server. Stopping".format(webinspect_client.scan_policy))
                exit(1)
            else:
                Logger.console.info("Found policy {} in WebInspect.".format(policy_guid))
        else:
            # Not a builtin. Assume that caller wants the provided policy to be uploaded
            Logger.console.info("Provided scan policy is not built-in, so will assume it needs to be uploaded.")
            webinspect_client.upload_policy()
            policy = webinspect_client.get_policy_by_name(webinspect_client.scan_policy)
            if policy:
                policy_guid = policy['uniqueId']
            else:
                Logger.console.info("The policy name is either incorrect or it is not available in {}."
                                    .format('etc/webinspect/policies'))
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
        Logger.console.critical("Scan status has changed to {0}.".format(status))
        if status.lower() != 'complete':  # case insensitive comparison is tricky. this should be good enough for now
            Logger.console.critical('Scan is incomplete and is unrecoverable. WebBreaker will exit!!')
            handle_scan_event('scan_end')
            exit(1)

        webinspect_client.export_scan_results(scan_id, 'fpr')
        webinspect_client.export_scan_results(scan_id, 'xml')
        handle_scan_event('scan_end')

        Logger.console.critical('Scan is complete.')
    except (requests.exceptions.ConnectionError, httplib.BadStatusLine, requests.exceptions.HTTPError) as e:
        Logger.console.error(
            "Unable to connect to WebInspect {0}, see log: {1}".format(webinspect_settings['webinspect_url'],
                                                                       Logger.app_logfile))
        Logger.app.error(
            "Unable to connect to WebInspect {0}, see also: {1}".format(webinspect_settings['webinspect_url'], e))

    if scan_id:
        Logger.app.info("Scan log: {}".format(webinspect_client.get_scan_log(scan_guid=scan_id)))

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
    Logger.console.critical("Webbreaker has completed.")


@webinspect.command('list')
@click.option('--server',
              required=True,
              help="URL of webinspect server. For example --server sample.webinspect.com:8083")
@click.option('--scan_name',
              required=False,
              help="Only list scans matching this scan_name")
@click.option('--protocol',
              required=False,
              type=click.Choice(['http', 'https']),
              default='https',
              help="The protocol used to contact the webinspect server. Default protocol is https")
@pass_config
def webinspect_list(config, server, scan_name, protocol):
    query_client = WebinspectQueryClient(host=server, protocol=protocol)
    try:
        if scan_name:
            results = query_client.get_scan_by_name(scan_name)
            if len(results):
                Logger.console.info("Scans matching the name {} found.".format(scan_name))
                Logger.console.info("{0:80} {1:40} {2:10}".format('Scan Name', 'Scan ID', 'Scan Status'))
                Logger.console.info("{0:80} {1:40} {2:10}\n".format('-' * 80, '-' * 40, '-' * 10))
                for match in results:
                    Logger.console.info(
                        "{0:80} {1:40} {2:10}".format(match['Name'], match['ID'], match['Status']))
            else:
                Logger.console.info("No scans matching the name {} were found.".format(scan_name))
        else:
            query_client.list_scans()
    except:
        Logger.console.info("Unable to complete command 'webinspect list'")


@webinspect.command()
@click.option('--server',
              required=True,
              help="URL of webinspect server. For example --server sample.webinspect.com:8083")
@click.option('--scan_name',
              required=True,
              help="Name of scan to be downloaded")
@click.option('-x',
              required=False,
              default="fpr",
              help="Desired file format of scan download. Extension is defaulted to .fpr")
@click.option('--protocol',
              required=False,
              type=click.Choice(['http', 'https']),
              default='https',
              help="The protocol used to contact the webinspect server. Default protocol is https")
@pass_config
def download(config, server, scan_name, x, protocol):
    query_client = WebinspectQueryClient(host=server, protocol=protocol)
    try:
        search_results = query_client.get_scan_by_name(scan_name)
        if len(search_results) == 0:
            Logger.console.info("No scans matching the name {} where found on this host".format(scan_name))
        elif len(search_results) == 1:
            scan_id = search_results[0]['ID']
            Logger.console.info(
                "Scan matching the name {} found.\nDownloading scan {} ...".format(scan_name, scan_id))
            query_client.export_scan_results(scan_id, scan_name, x)
        else:
            Logger.console.info("Multiple scans matching the name {} found.".format(scan_name))
            Logger.console.info("{0:80} {1:40} {2:10}".format('Scan Name', 'Scan ID', 'Scan Status'))
            Logger.console.info("{0:80} {1:40} {2:10}\n".format('-' * 80, '-' * 40, '-' * 10))
            for result in search_results:
                Logger.console.info("{0:80} {1:40} {2:10}".format(result['Name'], result['ID'], result['Status']))
    except:
        Logger.console.info("Unable to complete command 'webinspect download'")


@cli.group(help="""Collaborative web application for managing WebInspect and Fortify SCA security bugs
across the entire secure SDLC-from development to QA and through production.""")
@pass_config
def fortify(config):
    pass


@fortify.command('list')
@click.option('--fortify_user')
@click.option('--fortify_password')
@click.option('--application',
              required=False,
              help="Name of Fortify application which you would like to list versions of."
              )
@pass_config
def fortify_list(config, fortify_user, fortify_password, application):
    fortify_config = FortifyConfig()
    try:
        if not fortify_user or not fortify_password:
            Logger.console.info("No Fortify username or password provided. Checking fortify.ini for secret")
            if fortify_config.secret:
                Logger.console.info("Fortify secret found in fortify.ini")
                fortify_client = FortifyClient(fortify_url=fortify_config.ssc_url, token=fortify_config.secret)
            else:
                Logger.console.info("Fortify secret not found in fortify.ini")
                fortify_user = click.prompt('Fortify user')
                fortify_password = click.prompt('Fortify password', hide_input=True)
                fortify_client = FortifyClient(fortify_url=fortify_config.ssc_url, fortify_username=fortify_user,
                                               fortify_password=fortify_password)
                fortify_config.write_secret(fortify_client.token)
                Logger.console.info("Fortify secret written to fortify.ini")
            if application:
                reauth = fortify_client.list_application_versions(application)
                if reauth == -1 and fortify_config.secret:
                    Logger.console.info("Fortify secret invalid...reauthorizing")
                    fortify_user = click.prompt('Fortify user')
                    fortify_password = click.prompt('Fortify password', hide_input=True)
                    fortify_client = FortifyClient(fortify_url=fortify_config.ssc_url, fortify_username=fortify_user,
                                                   fortify_password=fortify_password)
                    fortify_config.write_secret(fortify_client.token)
                    Logger.console.info("Fortify secret written to fortify.ini")
                    Logger.console.info("Attempting to rerun 'fortify list --application'")
                    fortify_client.list_application_versions(application)
            else:
                reauth = fortify_client.list_versions()
                if reauth == -1 and fortify_config.secret:
                    Logger.console.info("Fortify secret invalid...reauthorizing")
                    fortify_user = click.prompt('Fortify user')
                    fortify_password = click.prompt('Fortify password', hide_input=True)
                    fortify_client = FortifyClient(fortify_url=fortify_config.ssc_url, fortify_username=fortify_user,
                                                   fortify_password=fortify_password)
                    fortify_config.write_secret(fortify_client.token)
                    Logger.console.info("Fortify secret written to fortify.ini")
                    Logger.console.info("Attempting to rerun 'fortify list'")
                    fortify_client.list_versions()
        else:
            fortify_client = FortifyClient(fortify_url=fortify_config.ssc_url, fortify_username=fortify_user,
                                           fortify_password=fortify_password)
            fortify_config.write_secret(fortify_client.token)
            Logger.console.info("Fortify secret written to fortify.ini")
            if application:
                fortify_client.list_application_versions(application)
            else:
                fortify_client.list_versions()

    except:
        Logger.console.critical("Unable to complete command 'fortify list'")


@fortify.command()
@click.option('--fortify_user')
@click.option('--fortify_password')
@click.option('--application',
              required=False,
              help="Name of the Fortify application that version belongs to. If this option is not provided, application_name from fortify.ini will be used.")
@click.option('--version',
              required=True,
              help="Name of Fortify application version which you would like to upload a scan to.")
@click.option('--scan_name',
              required=False,
              help="If the name of the file is different than --version, use this option to to specify the name of the file (without the extension)")
@pass_config
def upload(config, fortify_user, fortify_password, application, version, scan_name):
    fortify_config = FortifyConfig()
    # Fortify only accepts fpr scan files
    x = 'fpr'
    if application:
        fortify_config.application_name = application
    if not scan_name:
        scan_name = version
    try:
        if not fortify_user or not fortify_password:
            Logger.console.info("No Fortify username or password provided. Checking fortify.ini for secret")
            if fortify_config.secret:
                Logger.console.info("Fortify secret found in fortify.ini")
                fortify_client = FortifyClient(fortify_url=fortify_config.ssc_url,
                                               project_template=fortify_config.project_template,
                                               application_name=fortify_config.application_name,
                                               token=fortify_config.secret, scan_name=version, extension=x)
            else:
                Logger.console.info("Fortify secret not found in fortify.ini")
                fortify_user = click.prompt('Fortify user')
                fortify_password = click.prompt('Fortify password', hide_input=True)
                fortify_client = FortifyClient(fortify_url=fortify_config.ssc_url,
                                               project_template=fortify_config.project_template,
                                               application_name=fortify_config.application_name,
                                               fortify_username=fortify_user,
                                               fortify_password=fortify_password, scan_name=version,
                                               extension=x)
                fortify_config.write_secret(fortify_client.token)
                Logger.console.info("Fortify secret written to fortify.ini")
        else:
            fortify_client = FortifyClient(fortify_url=fortify_config.ssc_url,
                                           project_template=fortify_config.project_template,
                                           application_name=fortify_config.application_name,
                                           fortify_username=fortify_user,
                                           fortify_password=fortify_password, scan_name=version, extension=x)
            fortify_config.write_secret(fortify_client.token)
            Logger.console.info("Fortify secret written to fortify.ini")

        reauth = fortify_client.upload_scan(file_name=scan_name)

        if reauth == -2:
            # The given application doesn't exist
            Logger.file_logr.critical("Fortify Application {} does not exist. Unable to upload scan.".format(application))

        if reauth == -1 and fortify_config.secret:
            Logger.console.info("Fortify secret invalid...reauthorizing")
            fortify_user = click.prompt('Fortify user')
            fortify_password = click.prompt('Fortify password', hide_input=True)
            fortify_client = FortifyClient(fortify_url=fortify_config.ssc_url,
                                           project_template=fortify_config.project_template,
                                           application_name=fortify_config.application_name,
                                           fortify_username=fortify_user,
                                           fortify_password=fortify_password, scan_name=version, extension=x)
            fortify_config.write_secret(fortify_client.token)

            Logger.console.info("Fortify secret written to fortify.ini")
            Logger.console.info("Attempting to re-run 'fortify upload'")
            app_error = fortify_client.upload_scan(file_name=scan_name)

            if app_error == -2:
                # The given application doesn't exist
                Logger.console.critical(
                    "Fortify Application {} does not exist. Unable to upload scan.".format(application))
    except:
        Logger.console.critical("Unable to complete command 'fortify upload'")


if __name__ == '__main__':
    cli()
