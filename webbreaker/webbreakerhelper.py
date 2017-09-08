#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


class WebBreakerHelper(object):
    @classmethod
    def check_run_env(cls):
        jenkins_home = os.getenv('JENKINS_HOME', '')
        if jenkins_home:
            return "jenkins"
        return None

