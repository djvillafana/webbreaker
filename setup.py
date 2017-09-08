#!/usr/bin/env python
#  -*- coding: utf-8 -*-


import sys
import os
from setuptools.command.test import test as TestCommand
from webbreaker import __version__ as version
from cryptography.fernet import Fernet
from datetime import datetime
import base64

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

requires = ['click',
            'configparser>=3.5.0',
            'dpath>=1.4.0',
            'fortifyapi',
            'gitpython',
            'logging',
            'httplib2',
            'ndg-httpsclient',
            'mock',
            'pyasn1',
            'pyfiglet>=0.7.5',
            'pyOpenSSL',
            'cryptography>=1.8.0',
            'webinspectapi>=1.0.15',
            'requests']

tests_require = ['pytest', 'pytest-cache', 'pytest-cov']


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import shlex
        import pytest
        err = pytest.main(shlex.split(self.pytest_args))
        sys.exit(err)

def set_secret():
    key = Fernet.generate_key()
    with open(".webbreaker", 'w') as secret_file:
        secret_file.write(key.decode())
    os.chmod('.webbreaker', 0o400)
    print("New secret has been set.")

if sys.argv[-1] == 'secret':
    set_secret()
    sys.exit(0)

# build and install helper
if sys.argv[-1] == 'install':
    os.system('python setup.py install --user')
    sys.exit(0)

if sys.argv[-1] == 'build':
    os.system('python setup.py sdist bdist_wheel')
    sys.exit(0)

try:
    setup(
        name='webbreaker',
        description='Application to automate Dynamic Application Security Test Orchestration (DASTO).',
        long_description=open('README.md').read(),
        version=version,
        author='Brandon Spruth, Jim Nelson, Matthew Dunaj',
        author_email='brandon.spruth2@target.com, jim.nelson2@target.com, matthew.dunaj@target.com',
        license='MIT',
        url="https://github.com/target/webbreaker",
        packages=find_packages(exclude=['docs', 'tests']),
        include_package_data=True,
        zip_safe=False,
        py_modules=['webbreaker.webbreakercli'],
        package_data={'configs': ['webbreaker/etc/logging.ini',
                                  'webbreaker/etc/fortify.ini',
                                  'webbreaker/etc/email.ini',
                                  'webbreaker/etc/webinspect.ini',
                                  'images/WebBreakerArchitecture.jpg']
        },
        install_requires=requires,
        entry_points='''
            [console_scripts]
            webbreaker=webbreaker.webbreakercli:cli
        ''',
        classifiers=[
            'Programming Language :: Python',
            'Development Status :: 4 - Beta',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation ::CPython'],
        extras_require={'test': tests_require},
        tests_require=['pytest'],
        cmdclass={'test': PyTest}
    )
finally:
    if not os.path.isfile('.webbreaker'):
        set_secret()
