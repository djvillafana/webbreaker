#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
from webbreaker.webbreakerlogger import Logger


class WebBreakerArgs(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='WebBreaker is an API client that launches Dynamic Application Security Tests (DAST).'
                        'It is developed by Target Corporation and designed to centrally manage and administer a portfolio '
                        'of commercial and open-source DAST products by integrating functional security tests into a '
                        'DevOps pipeline.  The supported products are WebInspect and Fortify SSC, more products '
                        'will be added in the future.',
            usage='''webbreaker <command> [<args>]

                The most commonly used webbreaker commands are:
                   webinspect       HWebinspect is the industry leading DAST product designed to thoroughly analyze today’s
                                    complex Web applications and Web services for security vulnerabilities.
                   --settings       Load the pre-configured WebInspect configuration file available on your WebInspect instance.  Default value is the setting file Default that is shipped with WebInspect.
                   --scan_name      Dynamic value that can be overriden, either the Jenkins environment variable $JOB_NAME or WEBINSPECT-<random alpha-numeric>
                   -x               Scan artifact format for uploading to either SSC (fpr) or ThreadFix (xml).  Values are either fpr or xml.
                   --scan_mode      Overrides the setting scan mode value.  Acceptable values are crawl, scan, or all.
                   --scan_scope     Overrides the scope value.  Acceptable values are all, strict, children, and ancestors.
                   --workflow_macros Overrides the login macro. Acceptable values are login .webmacros files available on the WebInspect scanner to be used.
                   --scan_policy    Overrides the existing scan policy determined by the settings file.  Optional scan policies are Aggressive SQL Injection(1010), Apache Struts(1015), Criticals and Highs(1008),
                                    Cross-Site Scripting(1002), NoSQL and Node.js(1011), OWASP Top 10 Application Security Risks 2013(1012), OWASP Top 10 Application Security Risks – 2007(1003), OWASP Top 10 Application Security Risks – 2010(1009),
                                    SQL Injection(1001), Quick(4).
                   --scan_start     Overrides scanning method to use either a `url` or a workflow `.webmacro`.  Acceptable values are simply `url` or `macro`.
                   --start_urls     Overrides the specific url(s) to include in the scope of the scan, this option MUST include it's option dependency `--scan_start=url`.
                   --fortify_user   User to authenticate for uploading scans and create Fortify SSC Project/Application Version if none exists.
                   --fortify_secret Password to authenticate for uploading scans and create Fortify SSC Project/Application Version if none exists.

                An example of a complete command WITH overrides would be:
                    python webbreaker.py webinspect --settings example --scan_name webinspect-test
                    --scan_mode all --login_macro example-com-login --scan_policy example-policy --start_urls http://test.example.com

                An example of a complete command WITHOUT overrides would be:
                    python webbreaker.py webinspect --settings example --scan_name example-test

                An example of a complete command for a Jenkins Shell plugin would be:
                python webbreaker.py webinspect --settings=${SCAN_SETTING} --scan_name=${BUILD_TAG}

                NOTE: Run python setup.py install if root otherwise with --user option.
                ''')

        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            Logger.file_logr.debug('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def webinspect(self):
        parser = argparse.ArgumentParser(description='Create a Webinspect scan and/or uploads to '
                                                     'Fortify SSC.')

        parser.add_argument('--settings',
                            dest='settings',
                            action='store',
                            default='Default',
                            required=False
                            )
        parser.add_argument('--scan_name',
                            dest='scan_name',
                            nargs='?',
                            help="Specify name of scan '--scan_name ${BUILD_TAG}'"
                            )
        parser.add_argument('--url',
                            dest='url',
                            nargs='?',
                            required=False,
                            help="***THIS VALUE IS DEPRECATED, AND WILL BE IGNORED***"
                            )
        parser.add_argument('--size',
                            dest='size',
                            nargs='?',
                            required=False,
                            help="Size of scanner required. Valid values if provided are 'medium' or 'large'")
        parser.add_argument('-x',
                            dest='extension',
                            default='fpr',
                            help="Three acceptable formats .fpr, .xml, and .scan. ThreadFix requires .xml and "
                            "Fortify SSC requires .fpr. Default is set to -x fpr, the native scan WebInspect format is .scan.",
                            required=False
                            )
        parser.add_argument('--scan_mode',
                            dest='scan_mode',
                            nargs='?',
                            help="--scan_mode crawl, scan, or all",
                            required=False
                            )
        parser.add_argument('--scan_scope',
                            dest='scan_scope',
                            nargs='?',
                            help="--scan_scope children, ",
                            required=False
                            )
        parser.add_argument('--login_macro',
                            dest='login_macro',
                            nargs='?',
                            help="--login_macro=test-login",
                            required=False
                            )
        parser.add_argument('--scan_policy',
                            dest='scan_policy',
                            nargs='?',
                            help="--scan_policy names supported are either custom or built-in WebInspect policies, for example \n"
                            "AggressiveSQLInjection, AllChecks, ApacheStruts, Application,"
                            "Assault, CriticalsAndHighs, CrossSiteScripting, Development, Mobile, NoSQLAndNode.js"
                            "OpenSSLHeartbleed, OWASPTop10ApplicationSecurityRisks2013, OWASPTop10ApplicationSecurityRisks2007"
                            "OWASPTop10ApplicationSecurityRisks2010, PassiveScan, Platform, PrivilegeEscalation,"
                            "QA, Quick, Safe, SOAP, SQLInjection, Standard and TransportLayerSecurity",
                            required=False
                            )
        parser.add_argument('--scan_start',
                            dest='scan_start',
                            help='--scan_start url or macro',
                            required=False
                            )
        parser.add_argument('--start_urls',
                            dest='start_urls',
                            nargs='*',
                            help='Enter a single url or a list separated by spaces. '
                            'For example --scan_url http://test.example.com http://test2.example.com',
                            required=False
                            )
        parser.add_argument('--upload_settings', dest='upload_settings', nargs='?',
                            help="--upload_settings litecart, upload setting file to the webinspect scanner "
                            "settings are hosted under webbreaker/etc/webinspect/settings, "
                            "all settings files end with an .xml extension, the xml extension is not needed "
                            "and shouldn't be included.",
                            required=False
                            )
        parser.add_argument('--upload_policy', dest='upload_policy', nargs='?',
                            help="--upload_policy xss, upload policy file to the webinspect scanner"
                            "policies are hosted under webbreaker/etc/webinspect/policies, all policy "
                            "files end with a .policy extension, the policy extension is not needed and "
                            "shouldn't be included.",
                            required=False
                            )
        parser.add_argument('--upload_webmacros', dest='upload_webmacros', nargs='*',
                            help="--upload_webmacro litecart-login, webmacro to the webinspect scanner "
                            "macros are hosted under webbreaker/etc/webinspect/webmacros, all webmacro "
                            "files end with a .webmacro extension, the webmacro extension is not needed "
                            "and shouldn't be included.",
                            required=False
                            )
        parser.add_argument('--fortify_user',
                            dest='fortify_user',
                            nargs='?',
                            help="--fortify_user"
                            )
        parser.add_argument('--list_scans',
                            dest='list_scans',
                            nargs='?',
                            help="--list_scans, list all scans under the webinspect url",
                            required=False
                            )
        parser.add_argument('--scan_throttle',
                            dest='scan_throttle',
                            nargs='?',
                            required=False,
                            help="***NOT YET IMPLEMENTED***"
                            )
        parser.add_argument('--allowed_hosts',
                            dest='allowed_hosts',
                            nargs='*',
                            required=False,
                            help="Include the hosts to scan without the protocol or scheme http:// or https://, "
                                 "either a single host or a list of hosts separated by spaces on a single line. "
                                 "If --allowed_hosts is not provided, all hosts explicitly stated within the option,"
                                 "--start_urls will be used.  Keep in mind, if this option is used you must re-enter "
                                 "your host as provided in --start_urls!"
                            )
        parser.add_argument('--workflow_macros',
                            dest='workflow_macros',
                            nargs='*',
                            required=False,
                            help="--workflow_macros litecart-workflow "
                            "macros are hosted under webbreaker/etc/webinspect/webmacros, all webmacro "
                            "files end with a .webmacro extension, the webmacro extension is not needed "
                            "and shouldn't be included. macros listed here will be uploaded and will be used as"
                            "the workflow macros for the scan being launched."
                            )

        args = parser.parse_args(sys.argv[2:])

        return args
