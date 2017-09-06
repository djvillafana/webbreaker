### Introduction ###
Build functional security testing, into your software development and release cycles! WebBreaker provides the capabilities to automate and centrally manage Dynamic Application Security Testing (DAST) as part of your DevOps pipeline.

WebBreaker truly enables all members of the Software Security Development Life-Cycle (SDLC), with access to security testing, greater test coverage with increased visibility by providing Dynamic Application Security Test Orchestration (DASTO).  Current support is limited to the World's most popular commercial DAST product, WebInspect.

### System Architecture ###
![WebBreaker System Architecture](images/WebBreakerSystemArchitecture.jpg)

### Supported Features ###
* Command-line (CLI) scan administration of WebInspect with Foritfy SSC products.
* Docker container support
* [Jenkins Continuous Deployment](https://jenkins.io) support
* Email alerting or notification.
* Extensible event scan logging with scan output.
* [WebInspect REST API](https://pypi.python.org/pypi/webinspectapi) support for v9.30 and later.
* [Fortify Software Security Center (SSC) REST API](https://pypi.python.org/pypi/fortifyapi) support for v16.10 and later.
* WebInspect scan cluster support between two (2) or greater WebInspect servers/sensors
* Extensible scan telemetry with ELK and Splunk
* GIT support for WebInspect scan configurations.

### Usage ###
WebBreaker implements a command-line interface (CLI), specific to a Product.  The CLI supports upper-level and lower-level commands with respective options to enable interaction with Dynamic Application Security Test (DAST) products.  The two Products supported are WebInspect and Fortfiy.  Below is complete documentation of WebBreaker's usage.

Usage:
=======
    SYNOPSIS:
    webbreaker [webinspect|fortify] [list|scan|download|upload] [OPTIONS]

    DESCRIPTION:
    WebBreaker is a light-weight, scalable, distributed, and automated dynamic security testing framework with a rich
    command set providing both high-level Product operations and Dynamic Application Security Test Orchestration (DASTO) on Products.

    COMMANDS:
    Webbreaker is separated into Upper ("Products") and Lower level ("Actions") commands with their respective options.

    UPPER-LEVEL COMMANDS:
    webbreaker-fortify
    Administer WebInspect scan results with Fortify Software Security Center (SSC).  Available `Actions` are
    add, list, and upload.

    webbreaker-webinspect
    Select WebInspect as your commercial scanner or Dynamic Application Security Test (DAST) product.  Available  `Actions` are
    scan, list and download.

    LOWER-LEVEL COMMANDS
    webbraker-list
    List current and past WebInspect scans.

    webbreaker-scan
    Create or launch a WebInspect scan from a fully licensed WebInspect server or host. Scan results are automatically
    downloaded in both XML and FPR formats.

    webbreaker-download
    Download or export a WebInspect scan locally.

    fortify-upload
    Upload a WebInspect scan to Fortify Software Security Center (SSC).

    WEBINSPECT SCAN OPTIONS:
      --settings            WebInspect scan configuration file, if no setting file is specified the ```Default``` file
                            shipped with WebInspect will be used.
      --scan_name           Used for the command 'webinspect scan' as both a scan instance variable and file name.  Default value is
                            _`WEBINSPECT-<random-5-alpha-numerics>`, or Jenkins global
                            environment variables may be declared, such as $BUILD_TAG.
      --scan_policy         Overrides the existing scan policy from the value in the setting file from `--settings`,
                            see `webinspect.ini` for built-in values.  Any custom policy must include only the GUID.
                            Do NOT include the `.policy` extension.
      --login_macro         Overrides the login macro declared in the original setting file from `--settings` and
                            uploads it to the WebInspect server.
      --workflow_macros     Workflow macros are located under webbreaker/etc/webinspect/webmacros, all webmacro files
                            end with a .webmacro extension, do NOT include the `webmacro` extension.
      --scan_mode           Acceptable values are `crawl`, `scan`, or `all`.
      --scan_scope          Acceptable values are `all`, `strict`, `children`, and `ancestors`.
      --scan_start          Acceptable values are `url` or `macro`.
      --start_urls          Enter a single url or multiple each with it's own --start_urls.
                            For example --start_urls http://test.example.com --start_urls http://test2.example.com
      --allowed_hosts       Hosts to scan, either a single host or a list of hosts separated by spaces. If not provided,
                            all values from `--start_urls` will be used.
      --size                WebInspect scan servers are managed with the `webinspect.ini` file, however a medium or large
                            size WebInspect server defined in the config can be explicitely declared with `--size medium`
                            or `--size large`.

      WEBINSPECT LIST OPTIONS:
      --server              Query a list of past and current scans from a specific WebInspect server or host.
      --scan_name           Limit query results to only those matching a given scan name
      --protocol            Specify which protocol should be used to contact the WebInspect server. Valid protocols
                            are 'https' and 'http'. If not provided, this option will default to 'https'

      WEBINSPECT DOWNLOAD OPTIONS:
      --scan_name           Specify the desired scan name to be downloaded from a specific WebInspect server or host.
      --server              Required option for downloading a specific WebInspect scan.  Server must be appended to all
                            WebInspect download Actions.
      --protocol            Specify which protocol should be used to contact the WebInspect server. Valid protocols
                            are 'https' and 'http'. If not provided, this option will default to 'https'

      FORTIFY LIST OPTIONS:
      --application         Provides a listing of Fortify SSC Version(s) within a specific Application or Project.
      --fortify_user /      If provided WebBreaker authenticates to Fortify using these credentials. If not provided
        --fortify_password  WebBreaker attempts to use a secret for fortify.ini. If no secret is found our the secret is
                            no longer valid, you will be prompted for these credentials.

      FORTIFY UPLOAD OPTIONS:
      --fortify_user /      If provided WebBreaker authenticates to Fortify using these credentials. If not provided
        --fortify_password  WebBreaker attempts to use a secret for fortify.ini. If no secret is found our the secret is
                            no longer valid, you will be prompted for these credentials.
      --fortify_version     Used for the command 'fortify upload' this option specifies the application version name and
                            is used to both locate the file to be uploaded and the correct fortify application version
                            to upload the file to.
      -x                    Specifies the extension of the file to be uploaded. WebBreaker will attempt to upload the file
                            {fortify_version}.{x}

### Quick Local Installation ###
There are two (2) methods to install WebBreaker from github.com.
* ```git clone https://github.com/target/webbreaker```
* ```python setup.py install --user```

### Usage Examples ###

The three (3) command-line usage examples illustrate the minimum _required_, _scans without a setting file_ and _continuous deployment_ with a Jenkins Free Style job.

+ Minimal WebBreaker command, setup.py needs to be ran once for installing python dependencies.  Your Python site-packages must be included in your PATH to run from the command-line locally.
```
> webbreaker webinspect scan --settings=Default.xml
```
+ WebBreaker command without the _`--settings`_ option, creating an authenitcated scan with no pre-determined scan values.
```
> webbreaker webinspect scan --login_macro=some_login_macro --start_urls=example.com --scan_policy=Standard --scan_start=url --allowed_hosts=foo.example.com bar.example.com
```
+ Jenkins command-line with Shell plugin in Build or Post-Build task:
```
> webbreaker webinspect scan --settings=Default.xml --scan_name=${BUILD_TAG}
```

### Executing or Running WebBreaker ###

```
webbreaker webinspect --url=https://some.webinspect.server.com --settings=MyCustomWebinspectSetting --scan_policy=Application --scan_name=some_scan_name
 _       __     __    ____                  __            
| |     / /__  / /_  / __ )________  ____ _/ /_____  _____
| | /| / / _ \/ __ \/ __  / ___/ _ \/ __ `/ //_/ _ \/ ___/
| |/ |/ /  __/ /_/ / /_/ / /  /  __/ /_/ / ,< /  __/ /    
|__/|__/\___/_.___/_____/_/   \___/\__,_/_/|_|\___/_/     

Version 1.2.0

JIT Scheduler has selected endpoint https://some.webinspect.server.com:8083.
WebInspect scan launched on https://some.webinspect.server.com:8083 your scan id: ec72be39-a8fa-46b2-ba79-10adb52f8adb !!

Scan results file is available: some_scan_name.fpr
Scan has finished.
Webbreaker complete.
```

**NOTE:**

* Include your site-packages, if they are not declared ```export PATH=$PATH:$PYTHONPATH```
* WebBreaker is compatible with Jenkins Global Environmental variables or other custom parameterized strings in Jenkins can be passed, for example --scan_name=${BUILD_TAG}.

### Bugs and Feature Requests

Found something that doesn't seem right or have a feature request? [Please open a new issue](https://github.com/target/webbreaker/issues/new/).

### Copyright and License

* Copyright 2017 Target Brands, Inc.
* [Licensed under MIT](LICENSE.txt).
