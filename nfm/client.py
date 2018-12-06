import urllib2
import httplib
import json
import time
test_data = {
  "deployment": [
    {
      "slice_id": "slice_0",
      "task_id": "task_0",
      "vnf_node_list": [
        {
          "vnf_node_id": "vnf0",
          "config_agent_info": {
              "agent_public_address": "10.10.7.96",
              "agent_mgmt_address": "10.10.7.96",
              "agent_username":"root",
              "agent_password":"123456"
              },

          "vnfc_node_list": [
            {
              "vnfc_node_id": "vnfc1",
              "mgmt_address": "172.168.10.7",
              "vnfc_node_user": "spgw",
              "vnfc_node_passwd": "123",
              "interface_list": [
                {
                  "interface_id": "init0",
                  "scope": "deployment",
                  "format": "ifconfig",
                  "path": "/home/spgw/"
                },
                {
                    "interface_id": "init1",
                    "scope": "install",
                    "format": "free",
                    "path": "/home/spgw/"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}

test_single_interface_invoking = {
	"slice_id" : "slice_0",
	"task_id"  : "task_1",
	"vnf_node_id" : "vnf0",
	"vnfc_node_id" : "vnfc1",
	"scope" : "install"
}


test_interface_invoking = {
  "invoking_commands": [
    {
      "slice_id": "slice_0",
      "task_id": "task_0",
      "vnf_node_list": [
        {
          "vnf_node_id": "vnf0",
          "vnfc_node_list": [
            {
              "vnfc_node_id": "vnfc1",
              "interface_list": [
                {
                  "interface_id": "init0",
                  "scope": "deployment"
                },
                {
                    "interface_id": "init1",
                    "scope": "install"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}

test_deployment_urlencode = json.JSONEncoder().encode(test_data)
requrl_deployment = "http://localhost:5000/5gslm/iaa/nfm/v1/interface/deployment/json"
request = urllib2.Request(requrl_deployment, test_deployment_urlencode)
result = urllib2.urlopen(request).read()
print "deployment finished\n"

'''
time.sleep(20)

test_interface_invoking_urlencode = json.JSONEncoder().encode(test_interface_invoking)
requrl_invoking =  "http://localhost:5000/nfm/v1/interfaces/invoking/json"
request = urllib2.Request(requrl_invoking, test_interface_invoking_urlencode)
result = urllib2.urlopen(request).read()
print "invoking finished\n"

time.sleep(5)

test_interface_invoking_urlencode = json.JSONEncoder().encode(test_single_interface_invoking)
requrl_invoking =  "http://localhost:5000/nfm/v1/interface/invoking/json"
request = urllib2.Request(requrl_invoking, test_interface_invoking_urlencode)
result = urllib2.urlopen(request).read()
'''
