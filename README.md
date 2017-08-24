### Introduction ###
Build functional security testing, into your software development and release cycles! WebBreaker provides the capabilities to automate and centrally manage Dynamic Application Security Testing (DAST) as part of your DevOps pipeline.

WebBreaker truly enables all members of the Software Security Development Life-Cycle (SDLC), with access to security testing, greater test coverage with increased visibility by providing Dynamic Application Security Test Orchestration (DASTO).  Current support is limited to the World's most popular commercial DAST product, WebInspect.

### System Architecture ###
![WebBreaker System Architecture](images/WebBreakerSystemArchitecture.jpg)

### Supported Features ###
* Immutable WebInspect scan configurations for Cloud scanning
* Extensible scan telemetry with ArcSight, ELK, Splunk, etc.
* Event notifications with scan launch and completion
* [Superset data visualization dashboard](https://github.com/airbnb/superset) support for scan status and performance.
* Enterprise load balancing between 2 or greater WebInspect Sensors
* Support for scan collaborative analysis with Fortify SSC
* Docker container support
* Jenkins global environmental variable inheritance with scan options.
* WebInspect REST API support for v9.30 and above. 

### Usage Options ###
The table below lists currently supported WebBreaker command-line options that are either required or optional accompanied with their description. 

Usage: `webbreaker [webinspect|fortify]`

    Options:
      --settings            WebInspect scan configuration file, if no setting file is specified the ```Default``` file
                            shipped with WebInspect will be used.
      -h, --help            show this help message and exit
      --scan_name           Used as both a scan instance variable and file name.  Default value is 
                            _`WEBINSPECT-<random-5-alpha-numerics>`, or Jenkins global
                            environment variables may be declared, such as $BUILD_TAG.
      --scan_policy         Overrides the existing scan policy from the value in the setting file from `--settings`,
                            see `webinspect.ini` for built-in values.  Any custom policy must include only the GUID.
                            Do NOT include the `.policy` extension.
      
      --login_macro         Overrides the login macro declared in the original setting file from `--settings` and
                            uploads it to the WebInspect server.
      --workflow_macros     Workflow macros are located under webbreaker/etc/webinspect/webmacros, all webmacro files
                            end with a .webmacro extension, do NOT include the `webmacro` extension.
      -x                    Export file type for scan files or artifacts.  Supported filetypes are either
                            the default `.fpr` for Fortify SSC or `.xml` for ThreadFix.
      --scan_mode           Acceptable values are `crawl`, `scan`, or `all`. 
      --scan_scope          Acceptable values are `all`, `strict`, `children`, and `ancestors`.
      --scan_start          Acceptable values are `url` or `macro`.
      --allowed_hosts       Hosts to scan, either a single host or a list of hosts separated by spaces. If not provided,
                            all values from `--start_urls` will be used.
      --fortify_user        User to authenticate, upload scan and and create Fortify SSC Project/Application Version if
                            none exists.  Connection values for the Fortify SSC are determined in
                            `webbreaker/etc/fortify.ini`.
                            

### Quick Local Installation ###
There are two (2) methods to install WebBreaker from github.com.
* ```git clone https://github.com/target/webbreaker```
* ```python setup.py install --user```

### Usage Examples ###

The three (3) command-line usage examples illustrate the minimum _required_, _scans without a setting file_ and _continuous deployment_ with a Jenkins Free Style job.

+ Minimal WebBreaker command, setup.py needs to be ran once for installing python dependencies.  Your Python site-packages must be included in your PATH to run from the command-line locally.
```
> webbreaker webinspect --settings=Default.xml
```
+ WebBreaker command without the _`--settings`_ option, creating an authenitcated scan with no pre-determined scan values.
```
> webbreaker webinspect --login_macro=some_login_macro --start_urls=example.com --scan_policy=Standard --scan_start=url --allowed_hosts=foo.example.com bar.example.com
```
+ Jenkins command-line with Shell plugin in Build or Post-Build task:
```
> webbreaker webinspect --settings=Default.xml --scan_name=${BUILD_TAG}
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

### Logging
WebBreaker may be implemented with Elastic Stack for log aggregation. Recommended compenents include Filebeat agents installed on all WebInspect servers, forwarding to Logstash, and visualized in Kibana. General implementation details are [here](https://qbox.io/blog/welcome-to-the-elk-stack-elasticsearch-logstash-kibana/).  A recommended approach is to tag log events and queries with ```WebInspect``` and ```webbreaker```, but remember queries are case sensitive.
 
### Notifications
WebBreaker provides notifications for start-scan and end-scan events. A simple publisher/subscriber pattern is implemented under the ```webbreaker/notifiers```.  A Reporter object will hold a collection of Notifiers, each of which implements a Notify function responsible for creating the desired notification. Currently, two notification types are implemented email and database.

The email notifier merges the provided event data into an HTML email message and sends the message. All SMTP-related settings are stored in [webbreaker/etc/email.ini](https://github.com/target/webbreaker/blob/master/webbreaker/etc/email.ini), and read during the webbreaker execution.

The database notifier inserts the provided event data into a PostgreSQL table. All database connection settings are stored in an external file located at the path defined under the 'database' section of [webbreaker/etc/webbreaker.ini](https://github.com/target/webbreaker/blob/master/webbreaker/etc/webbreaker.ini).

If an error occurs on behalf of the notifiers at any point during the process of creating or sending notifications, the event will be logged, without any interruption of WebBreaker execution or the WebInspect scan.

### Bugs and Feature Requests

Found something that doesn't seem right or have a feature request? [Please open a new issue](https://github.com/target/webbreaker/issues/new/).

### Copyright and License

* Copyright 2017 Target Brands, Inc.
* [Licensed under MIT](LICENSE.txt).
