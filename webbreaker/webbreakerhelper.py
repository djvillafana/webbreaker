#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from webbreaker.webbreakerlogger import Logger


class WebBreakerHelper(object):
    @classmethod
    def check_run_env(cls):
        jenkins_home = os.getenv('JENKINS_HOME', '')
        if jenkins_home:
            return "jenkins"
        return None


    @classmethod
    def getcommand(cls):
        """
        Determine what command is being provided on the command line and return it. If command is not present,
        print help and exit.
        :return: The command string
        """
        parser = argparse.ArgumentParser(
            description='WebBreaker is an API client that launches Dynamic Application Security Tests (DAST).'
                        'The supported products are WebInspect and Fortify SSC, more commercial products to be added in the future.',
            usage='''webbreaker <command> [<args>]

        The most commonly used webbreaker commands are:
           webinspect       Supported dynamic security testing product
           --settings       Load the pre-configured WebInspect configuration file available on your WebInspect instance.  Default value is the setting file Default that is shipped with WebInspect.
           --scan_name      Dynamic value that can be overriden, either the Jenkins environment variable $JOB_NAME or WEBINSPECT-<random alpha-numeric>
           -x               Scan artifact format for uploading to either SSC (fpr) or ThreadFix (xml).  Values are either fpr or xml.
           --scan_mode      Overrides the setting scan mode value.  Acceptable values are crawl, scan, or all.
           --scan_scope     Overrides the scope value.  Acceptable values are all, strict, children, and ancestors.
           --login_macro     Overrides the login macro. Acceptable values are login .webmacros files available on the WebInspect scanner to be used.
           --scan_policy    Overrides the existing scan policy determined by the settings file.  Optional scan policies are Aggressive SQL Injection(1010), Apache Struts(1015), Criticals and Highs(1008),
                            Cross-Site Scripting(1002), NoSQL and Node.js(1011), OWASP Top 10 Application Security Risks 2013(1012), OWASP Top 10 Application Security Risks – 2007(1003), OWASP Top 10 Application Security Risks – 2010(1009),
                            SQL Injection(1001), Quick(4).
           --scan_start     Overrides scanning method to use either a `url` or a workflow `.webmacro`.  Acceptable values are simply `url` or `macro`.
           --start_urls     Overrides the specific url(s) to include in the scope of the scan, this option MUST include it's option dependency `--scan_start=url`.
           --fortify_user   User to authenticate for uploading scans and create Fortify SSC Project/Application Version if none exists.
           --fortify_secret Password to authenticate for uploading scans and create Fortify SSC Project/Application Version if none exists.

        An example of a complete command WITH overrides would be:
            python webbreaker.py webinspect --settings test-example --scan_name test-example-com
            --scan_mode all --login_macro test-example-login --scan_policy custom-xss --start_urls http://test.example.com

        An example of a complete command WITHOUT overrides would be:
            python webbreaker.py webinspect --settings test-example-com --scan_name test-example-com

        An example of a complete command for a Jenkins Shell plugin would be:
        python webbreakercli.py webinspect --settings=${SCAN_SETTING} --scan_name=${BUILD_TAG}

        NOTE: Run python setup.py install if root otherwise with --user option.
        ''')

        parser.add_argument('command', help='Subcommand to run')
        try:
            args = parser.parse_args(sys.argv[1:2])
            if args.command == 'webinspect':
                return args.command
            else:
                raise AttributeError("webinspect is the only recognized command")
        except AttributeError as e:
            Logger.file_logr.debug('Unrecognized command. {}'.format(str(e)))
            parser.print_help()
            exit(1)
