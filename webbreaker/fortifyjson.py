#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import os
import socket

#50805619 or 51093981 or 9
# TODO: fix the project.id must be correct string numeric.  new projects ['project']['id'] does not exists and ['committed'] = False
json_application_version = {
    "name": "",
    "description": "",
    "active": True,
    "committed": True,
    "issueTemplateId": "",
    "project":
        {
            "name": "",
            "description": "",
            "issueTemplateId": "Prioritized-HighRisk-Project-Template",
            "id": "9"
        }
}

#default fortify ssc attribute values
json_ssc_bulk_attributes = {
    "uri": "",
    "httpVerb": "PUT",
    "postData": [
        {
            "attributeDefinitionId": 1,
            "values": [
                {
                    "guid": "High"
                }
            ],
            "value": "null"
        },
        {
            "attributeDefinitionId": 5,
            "values": [
                {
                    "guid": "Active"
                }
            ],
            "value": "null"
        },
        {
            "attributeDefinitionId": 6,
            "values": [
                {
                    "guid": "Internal"
                }
            ],
            "value": "null"
        },
        {
            "attributeDefinitionId": 7,
            "values": [
                {
                    "guid": "externalpublicnetwork"
                }
            ],
            "value": "null"
        },
        {
            "attributeDefinitionId": 10,
            "values": [
                {
                    "guid": "WA"
                }
            ],
            "value": "null"
        },
        {
            "attributeDefinitionId": 11,
            "values": [],
            "value": "null"
        },
        {
            "attributeDefinitionId": 12,
            "values": [],
            "value": "null"
        },
        {
            "attributeDefinitionId": 2,
            "values": [],
            "value": "null"
        },
        {
            "attributeDefinitionId": 3,
            "values": [],
            "value": "null"
        },
        {
            "attributeDefinitionId": 4,
            "values": [],
            "value": "null"
        }
    ]
}

# addid this for v16.10
json_ssc_bulk_action = {
    "uri": "",
    "httpVerb": "POST",
    "postData": [
        {
            "type": "COPY_FROM_PARTIAL",
            "values": {
                "projectVersionId": "",
                "previousProjectVersionId": "",
                "copyAnalysisProcessingRules": True,
                "copyBugTrackerConfiguration": True,
                "copyCurrentStateFpr": False,
                "copyCustomTags": True
            }
        }
    ]
}

json_ssc_bulk_responsibilities = {
    "uri": "",
    "httpVerb": "PUT",
    "postData": [
        {
            "responsibilityGuid": "projectmanager",
            "userId": "null"
        },
        {
            "responsibilityGuid": "securitychampion",
            "userId": "null"
        },
        {
            "responsibilityGuid": "developmentmanager",
            "userId": "null"
        }
    ]
}

json_ssc_bulk_appversion = {
    "uri": "",
    "httpVerb": "PUT",
    "postData": {
        "committed": True
    }
}

json_ssc_bulk = {
    "requests": []
}

json_ssc_filetoken = {
    "fileTokenType": "UPLOAD"
}


def formatted_application_version_payload(project_name, version_name, issuetemplateid, runenv):
    global json_application_version

    json_application_version['project']['issueTemplateId'] = issuetemplateid
    json_application_version['project']['name'] = project_name

    json_application_version['issueTemplateId'] = issuetemplateid
    json_application_version['name'] = version_name

    if runenv == "jenkins":
        json_application_version['description'] = "WebInspect scan from WebBreaker " + os.getenv('JOB_URL', "jenkins server")
    else:
        json_application_version['description'] = "WebBreaker scan from WebBreaker host " + socket.getfqdn()

    return json_application_version


def formatted_bulk_ssc_payload(attributes_uri, responsibilities_uri, action_uri, application_version_uri):
    global json_ssc_bulk_attributes

    str_json_bulk_attributes = json.dumps(json_ssc_bulk_attributes)
    str_json_bulk_attributes = str_json_bulk_attributes.replace('"true"', "true")
    str_json_bulk_attributes = str_json_bulk_attributes.replace('"false"', "false")
    str_json_bulk_attributes = str_json_bulk_attributes.replace('"null"', "null")
    json_ssc_bulk_attributes = json.loads(str_json_bulk_attributes)

    json_ssc_bulk_attributes['uri'] = attributes_uri

    global json_ssc_bulk_responsibilities
    str_json_ssc_bulk_responsibilities = json.dumps(json_ssc_bulk_responsibilities)
    str_json_ssc_bulk_responsibilities = str_json_ssc_bulk_responsibilities.replace('"true"', "true")
    str_json_ssc_bulk_responsibilities = str_json_ssc_bulk_responsibilities.replace('"false"', "false")
    str_json_ssc_bulk_responsibilities = str_json_ssc_bulk_responsibilities.replace('"null"', "null")
    json_ssc_bulk_responsibilities = json.loads(str_json_ssc_bulk_responsibilities)

    json_ssc_bulk_responsibilities['uri'] = responsibilities_uri

    #added for v16.10
    global json_ssc_bulk_action
    str_json_ssc_bulk_action = json.dumps(json_ssc_bulk_action)
    str_json_ssc_bulk_action = str_json_ssc_bulk_action.replace('"true"', "true")
    str_json_ssc_bulk_action = str_json_ssc_bulk_action.replace('"false"', "false")
    str_json_ssc_bulk_action = str_json_ssc_bulk_action.replace('"null"', "null")
    json_ssc_bulk_action = json.loads(str_json_ssc_bulk_action)

    json_ssc_bulk_action['uri'] = action_uri

    global json_ssc_bulk_appversion
    str_json_ssc_bulk_appversion = json.dumps(json_ssc_bulk_appversion)
    str_json_ssc_bulk_appversion = str_json_ssc_bulk_appversion.replace('"true"', "true")
    str_json_ssc_bulk_appversion = str_json_ssc_bulk_appversion.replace('"false"', "false")
    str_json_ssc_bulk_appversion = str_json_ssc_bulk_appversion.replace('"null"', "null")
    json_ssc_bulk_appversion = json.loads(str_json_ssc_bulk_appversion)

    json_ssc_bulk_appversion['uri'] = application_version_uri

    global json_ssc_bulk
    json_ssc_bulk['requests'].append(json_ssc_bulk_attributes)
    json_ssc_bulk['requests'].append(json_ssc_bulk_responsibilities)
    json_ssc_bulk['requests'].append(json_ssc_bulk_action)
    json_ssc_bulk['requests'].append(json_ssc_bulk_appversion)

    return json_ssc_bulk


def formatted_filetoken_payload():
    return json_ssc_filetoken
