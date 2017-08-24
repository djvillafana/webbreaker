#!/usr/bin/env python
# -*- coding: utf-8 -*-


import click
from pyfiglet import Figlet
from webbreaker import __version__ as version
from webbreaker.webbreakerlogger import Logger


class Config(object):
    def __init__(self):
        self.debug = False

#pass_config = click.make_pass_file(Config, ensure=True)


@click.group()
@click.option('--debug', is_flag=True)
#@click.option('--webinspect-config', click.File())
#@pass_config
def cli(config, debug):
    config.debug = debug
    if webinspect_config is None:
        webinspect_config = 'etc/webinspect.ini'
    config.webinspect_config = webinspect_config


@cli.command()
@click.option('--scan_name',
              type=str,
              default='-',
              required=False,
              help="Specify name of scan --scan_name ${BUILD_TAG}")
@click.option('--settings',
                type=str,
                default='Default',
                required=True,
                help="Specify name of settings file, without the .xml extension,"
                   " under the webbreaker/etc/webinspect/settings directory --settings=")
def webinspect(config, settings, scan_name):
    """WebBreaker is an API client that launches Dynamic Application Security Tests (DAST).
    The supported products are WebInspect and Fortify SSC, more commercial products to be added in the future."""

    # Show something pretty to start
    f = Figlet(font='slant')
    Logger.file_logr.critical("\n\n{0}Version {1}\n".format(f.renderText('WebBreaker'), version))
    Logger.file_logr.critical("logging to file: {0}".format(logger.logfilepath))

    # Get the DAST command to run. Only option for now - webinspect. If it's there, we're ok to continue.
    #command = WebBreakerHelper.getcommand()
    #logger.debug("Running DAST command '{}'".format(str(command)))
    if config.debug:
        click.echo("We are in debug mode!!")
    click.echo("Webinspect Config: {}".format (config.webinspect_config))

    Logger.file_logr.critical('!!! HELLO !!!\n++++++++++++++++++\n '
                    'settings: {0}\n '
                    'scan_name: {1}\n++++++++++++++++++\n'
                    .format (settings, scan_name))
