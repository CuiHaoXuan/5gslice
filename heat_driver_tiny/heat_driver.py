import os
import logging
import json
import threading
import uuid
import urllib2
import yaml
from flask import Flask
from flask import request

app = Flask(__name__)


true = 'True'
false = 'False'

openstack_o_url = "http://10.10.26.179:8004/"
openstack_token_url = "http://10.10.26.179:35357/"



class heatDriver:

    def __getTokenId(self, tenant_name, password):
        print "get token id"
        ret = {}
        url = openstack_token_url + "v2.0/tokens"
        body = {'auth' : {"tenantName" : tenant_name, 'passwordCredentials' : {'username':tenant_name, 'password': password}}}
        body_urlencode = json.JSONEncoder().encode(body)
	http_req = urllib2.Request(url, body_urlencode)
        http_req.add_header('Content-type', 'application/json')
	try:
            r_data = eval( urllib2.urlopen(http_req).read() )
            token_id = r_data['access']['token']['id']
            tenant_id = r_data['access']['token']['tenant']['id']
            ret['token_id'] = token_id
            ret['tenant_id'] = tenant_id
            print token_id
            print tenant_id
            return ret

        except urllib2.URLError as e:
            if hasattr(e, 'code'):
                print 'get tenant_id error! Error code : ', e.code
            elif hasattr(e, 'reason'):
                print 'Reason : ', e.reason
            return None



    def openstackCreateStack(self, hot):
        req = {}
        r_data = {}
        
        #print hot  
        
        info = self.__getTokenId('demo', 'demo')
        if(info == None):
            print 'Error : Autentication failure'
            return
 
        token_id = info['token_id']
        tenant_id = info['tenant_id']
        stack_create_url = openstack_o_url + "v1/" + tenant_id + "/stacks"
	print stack_create_url
        http_req = urllib2.Request(stack_create_url, hot)
        http_req.add_header('X-Auth-Token', token_id)
        http_req.add_header('Content-type','application/json')
        try:
            r_data = eval ( urllib2.urlopen(http_req).read() )
            print r_data
            
        except urllib2.URLError as e:
            if hasattr(e, 'code'):
                print 'openstack_create_stack error! Error code : ', e.code
            elif hasattr(e, 'error'):
                print 'Reason:', e.error

        return r_data
        

    
driver = heatDriver()

@app.route('/5gslm/iaa/driver/heat/v1/vnf/management/create/<hot_name>/json', methods = ['POST'])
def create_vnf(hot_name):
    hot_file = open(hot_name)
    hot = eval(hot_file.read())
    hot = json.JSONEncoder().encode(hot)
    res = driver.openstackCreateStack(hot)
    return 

if __name__=='__main__':
	app.run(host = '0.0.0.0',port = 8094)
