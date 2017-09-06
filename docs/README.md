# WebBreaker Documentation

## Table of Contents
[Introduction](#introduction)

- [Description: `description`](#description)

[User Guide](#user-guide)

- [Installation: `installation`](#installation)
- [Supported Features `supported_features`](#supported-features)
- [Usage](#usage)
- [Logging](#logging)
- [Notifications](#notification)

[Configurations](#configurations)

- [Fortify configuration: `fortify_config`](#fortify-config)
- [WebInspect configuration: `webinspect_config`](#webinspect-config)
- [Logging configuration: `logging_config`](#logging-config)
- [Email configuration: `email_config`](#email-config)
- [WebInspect settings: `webinspect_settings`](#webinspect-settings)
- [WebInspect policies: `webinspect_policies`](#webinspect-policies)
- [WebInspect webmacros: `webinspect_webmacros`](#webinspect-webmacros)

## Introduction `introduction`

### Description `description`
Build functional security testing, into your software development and release cycles! WebBreaker provides the capabilities to automate and centrally manage Dynamic Application Security Testing (DAST) as part of your DevOps pipeline.

## User Guide `user-guide`

### Installation: `installation`

#### Source Installation
There are two (2) methods to install WebBreaker from github.com.
* ```git clone https://github.com/target/webbreaker```
* ```cd webbreaker```
* ```python setup.py install --user```

#### Package Install
WebBreaker releases are packaged on github.com and can be installed locally.
* ```pip install -e git+https://github.com/target/webbreaker.git#egg=webbreaker```

### Supported Features: `supported_features`

* Jenkins global environmental variable inheritance with scan options.
* WebInspect REST API support for v9.30 and above. 
* Export both XML and FPR WebInspect formats to Fortify Software Security Center (SSC) or other compatible vulnerability management web applications for vulnerability analysis/triage.
* Ability to automatically upload scan results to Fortify SSC or other third-party vulnerability management software.
* Centrally administer all configurations required to launch WebInspect scans.
* Remotely query arbitrary policies, settings, webmacros, from any WebInspect deployment.
* Configurable property .ini files to support your [Foritfy](webbreaker/etc/fortify.ini) and [WebInspect](webbreaker/etc/webinspect.ini) deployments.
* Enterprise scalability with configurable Just-In-Time (JIT) scheduling to distribute your WebInspect scans between two (2) or greater sensors.
* ChatOps extensibility and [email notifications](webbreaker/etc/email.ini) on scan start and completion.
* Local [logging](webbreaker/etc/logging.ini) of WebInspect scan state.
* [Superset data visualization dashboard](https://github.com/airbnb/superset) support for scan status and performance.

### Usage
#### Command Hierarchy
Webbreak utilizes a structure of upper-level and lower-level commands to enable interaction with multiple 3rd party platforms. The two platforms currently supported are WebInspect and Fortfiy and they can be accessed using their respective upper-level commands. Webbreaker supports multiple functions for each platform which are accessed via lower-level commands. The current command structure is listed below.

- webbreaker
  - webinspect
    - scan
    - list
    - download
  - fortify
    - list
    - upload

A promper Webbreaker command utilizes the structure 'webbreaker [webinspect|fortify] [lower-level command] [OPTIONS]'

#### Lower Level Command Features
- webinspect scan
  - This command will choose an available webinspect server and initiate a scan based on the given options. Upon scan completion the results will be downloaded in the specified format.
- webinspect list
  - This command requires the --server option and will list the Name, ID, and Status of all scans found on that host. This command also accepts the --scan_name option and if provided will limit the output to scans which match that name.
- webinspect download
  - This command requires the --server and --scan_name options and will download scan results in the desired format. If multiple scans match --scan_name they will be listed and nothing will be downloaded.
- fortify list
  - This command accepts a --application option and if given will list all version of that application found in Fortify. If --application  is not used, this command will list all versions of all applications found on Fortify.
- fortify upload
  - This command requires the --fortify_version and -x options and will upload the scan file {fortify_version}.{x} to the specified application version on Fortify.

## Logging
WebBreaker may be implemented with Elastic Stack for log aggregation. Recommended compenents include Filebeat agents installed on all WebInspect servers, forwarding to Logstash, and visualized in Kibana. General implementation details are [here](https://qbox.io/blog/welcome-to-the-elk-stack-elasticsearch-logstash-kibana/).  A recommended approach is to tag log events and queries with ```WebInspect``` and ```webbreaker```, but remember queries are case sensitive.

## Notifications
WebBreaker provides notifications for start-scan and end-scan events. A simple publisher/subscriber pattern is implemented under the ```webbreaker/notifiers```.  A Reporter object will hold a collection of Notifiers, each of which implements a Notify function responsible for creating the desired notification. Currently, two notification types are implemented email and database.

The email notifier merges the provided event data into an HTML email message and sends the message. All SMTP-related settings are stored in [webbreaker/etc/email.ini](https://github.com/target/webbreaker/blob/master/webbreaker/etc/email.ini), and read during the webbreaker execution.

If an error occurs on behalf of the notifiers at any point during the process of creating or sending notifications, the event will be logged, without any interruption of WebBreaker execution or the WebInspect scan.

## Configurations

### Fortify Configuration: `fortify_config`
Software Security Center (SSC) configuration file `webbreaker/etc/fortify.ini` administers communication with Fortify SSC, and other Application settings.  Both `Project Template` and `Application` are static values declared in `fortify.ini`.  The `--scan_name` value will be used as the SSC Version name, created within the `Application` specified in the `fortify.ini` illustrated below.

#### File
*webbreaker/etc/fortify.ini*

#### Example
```
[fortify]
fortify_url=http://localhost:8080/ssc
project_template=Prioritized High Risk Issue Template
application_name=WEBINSPECT
fortify_secret=XXX
```


### WebInspect Configuration: `webinspect_config`
WebInspect scan configuration files for `settings`, `policies`, and `webmacros` are versioned and hosted from a GIT repository determined in `webbreaker/etc/webinspect.ini`.  Additionally, all WebInspect policies and servers are managed from this configuration file.  The section `[api endpoints]` provides a _Just-In-Time_ (JIT) scheduler or the ability to load balance scans amongst a WebInspect cluster.

#### File
*webbreaker/etc/webinspect.ini*

#### Example
```
[webinspect_policies]
AggressiveSQLInjection=032b1266-294d-42e9-b5f0-2a4239b23941
AllChecks=08cd4862-6334-4b0e-abf5-cb7685d0cde7
ApacheStruts=786eebac-f962-444c-8c59-7bf08a6640fd
Application=8761116c-ad40-438a-934c-677cd6d03afb
Assault=0a614b23-31fa-49a6-a16c-8117932345d8
Blank=adb11ba6-b4b5-45a6-aac7-1f7d4852a2f6
CriticalsAndHighs=7235cf62-ee1a-4045-88f8-898c1735856f
CrossSiteScripting=49cb3995-b3bc-4c44-8aee-2e77c9285038
Development=9378c6fa-63ec-4332-8539-c4670317e0a6
Mobile=be20c7a7-8fdd-4bed-beb7-cd035464bfd0
NoSQLAndNode.js=a2c788cc-a3a9-4007-93cf-e371339b2aa9
OpenSSLHeartbleed=5078b547-8623-499d-bdb4-c668ced7693c
OWASPTop10ApplicationSecurityRisks2013=48cab8a0-669e-438a-9f91-d26bc9a24435
OWASPTop10ApplicationSecurityRisks2007=ece17001-da82-459a-a163-901549c37b6d
OWASPTop10ApplicationSecurityRisks2010=8a7152d5-2637-41e0-8b14-1330828bb3b1
PassiveScan=40bf42fb-86d5-4355-8177-4b679ef87518
Platform=f9ae1fc1-3aba-4559-b243-79e1a98fd456
PrivilegeEscalation=bab6348e-2a23-4a56-9427-2febb44a7ac4
QA=5b4d7223-a30f-43a1-af30-0cf0e5cfd8ed
Quick=e30efb2a-24b0-4a7b-b256-440ab57fe751
Safe=def6a5b3-d785-40bc-b63b-6b441b315bf0
SOAP=a7eb86b8-c3fb-4e88-bc59-5253887ea5b1
SQLInjection=6df62f30-4d47-40ec-b3a7-dad80d33f613
Standard=cb72a7c2-9207-4ee7-94d0-edd14a47c15c
TransportLayerSecurity=0fa627de-3f1c-4640-a7d3-154e96cda93c

[api_endpoints]
large=2
medium=1
server01=https://webinspect-server-1.example.com:8083
server02=https://webinspect-server-2.example.com:8083
server03=https://webinspect-server-3.example.com:8083
server04=https://webinspect-server-4.example.com:8083
server05=https://webinspect-server-5.example.com:8083
server06=https://webinspect-server-6.example.com:8083
server07=https://webinspect-server-7.example.com:8083
server08=https://webinspect-server-8.example.com:8083
server09=https://webinspect-server-9.example.com:8083
server10=https://webinspect-server-10.example.com:8083
e01: %(server01)s|%(large)s
e02: %(server02)s|%(large)s
e03: %(server03)s|%(large)s
e04: %(server04)s|%(large)s
e05: %(server05)s|%(large)s
e06: %(server06)s|%(medium)s
e07: %(server07)s|%(medium)s
e08: %(server08)s|%(medium)s
e09: %(server09)s|%(medium)s
e10: %(server10)s|%(medium)s

[webinspect_size]
large=2
medium=1

[webinspect_default_size]
default=large

[configuration_repo]
git = git@github.com:target/webbreaker.git
dir = webbreaker/etc/webinspect/
```

### Logging Configuration: `logging_config`
The `webbreaker/etc/logging.ini` implements the standard Python logging facility, logs and events are created under `/tmp`.

#### File
*webbreaker/etc/logging.ini*

#### Example
[See Python Logging](https://docs.python.org/3/library/logging.html)

### Email Configuration: `email_config`
Notifications for start-scan and end-scan events. A simple publisher/subscriber pattern is implemented under the "notifiers" folder.

A Reporter object holds a collection of Notifier objects, each of which implements a Notify function responsible for creating the desired notification. Currently, two notification types are implemented email and database.

The email notifier merges the provided event data into an HTML email message and sends the message. All SMTP-related settings are stored in .emailrc, and read during program startup.

#### File
*webbreaker/etc/email.ini*

#### Example
````
[emailer]
smtp_host=smtp.example.com
smtp_port=25
from_address=webbreaker-no-reply@example.com
to_address=webbreaker-activity@example.com
email_template:<html>
              <head></head>
              <body></body>
````

### WebInspect Settings: `webinspect_settings`
All WebInspect distributions are packaged with a `Default.xml` file that may be overridden and uploaded to the WebInspect deployment with the webbreaker option `--settings`.  The setting xml file contains all possible options for your scan including, a WebInspect scan including policy, workflow and/or login macro, scan depth, and allowed hosts.

*Note:* The `etc/webinspect.ini` property file contains a section `configuration_repo`, a unique GIT repo is defined by the user and is mutually exclusive from the WebBreaker source.  The assumption is each WebBreaker installation will have a unique GIT URL defined.  Upon each execution, the repo refreshes *all* settings file(s), assuming that there may be newly created, deletions, or modifications of settings files.  All settings files used in execution must reside in this respective repo under `etc/webinspect/settings`.

#### Directory
*webbreaker/etc/webinspect/settings*

### WebInspect Policies: `webinspect_policies`
Grouping of proprietary WebInspect tests to perform.  Tests or rules are represented in an `xml` element with a `.policy` file extension.  Custom tests or Checks are mapped to a unique WebInspect ID.  The mapping for all policies shipped with WebInspect are mapped with their respective GUID under `etc/webinspect.ini` within the `[webinspect_policies]` section.

*Note:* All custom polices are automatically uploaded to the targeted WebInspect server and must be referenced as a GUID.  

The `etc/webinspect.ini` property file contains a section `configuration_repo`, a unique GIT repo is defined by the user and is mutually exclusive from the WebBreaker source.  The assumption is each WebBreaker installation will have a unique GIT URL defined.  Upon each execution, the repo refreshes *all* settings file(s), assuming that there may be newly created, deletions, or modifications of settings files.  All settings files used in execution must reside in this respective repo under `etc/webinspect/settings`.


#### Directory
*webbreaker/etc/webinspect/policies*

### WebInspect Webmacros: `webinspect_webmacros`
Proprietary functional recordings of either a login or workflow of the website to scan, both files are encoded and are not compatable with any 3rd party product.  If a website requires authentication the login webmacro is required otherwise WebInspect will not be able to test any page enforcing authentication.  The workflow macro is a recording of a base case functional use of the website and is optional.  Alernatively, a website can be scanned by providing a list of URLs in-scope to scan.

*Note:* The `etc/webinspect.ini` property file contains a section `configuration_repo`, a unique GIT repo is defined by the user and is mutually exclusive from the WebBreaker source.  The assumption is each WebBreaker installation will have a unique GIT URL defined.  Upon each execution, the repo refreshes *all* settings file(s), assuming that there may be newly created, deletions, or modifications of settings files.  All settings files used in execution must reside in this respective repo under `etc/webinspect/settings`.

#### Directory
*webbreaker/etc/webinspect/webmacros*
