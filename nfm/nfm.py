from flask import Flask
from flask import request
from flask import render_template

import urllib2
import httplib
import json
from api.api_gateway import api_gateway
import threading
import datetime

app = Flask(__name__)

class NFM:

    '''
    slice_id, task_id and opJob_id in deployments request stored in the processing_list 
    task_dict = {
        task_id:
        {
            'opJob_id':nfmJob_id
            
        }
    }
    
    '''

    task_dict = {}
   
   ##########invoke driver interface : deploy interface file or exec commands#######
    def invokeDriverInterface(self, url, data, nfmJob_id):
        data['sender'] = 'nfm'
        if 'deployment' in data:
            commands_list = data['deployment']
        elif 'invoking_commands' in data:
            commands_list = data['invoking_commands']
	else:
            commands_list = []
	    commands_list.append(data)
        data_urlencode = json.JSONEncoder().encode(data)
        request = urllib2.Request(url,data_urlencode)
        response = eval ( urllib2.urlopen(request).read() )
        opJob_id = response['opJob_id']
        for command in commands_list:
            task_id = command['task_id']
            if task_id not in self.task_dict:
                self.task_dict[task_id] = {}
            self.task_dict[ task_id ][opJob_id] = nfmJob_id
        print 'self.task_dict : ', self.task_dict[ task_id ]
	return


    #######invoke sliceOM interface : when sliceOM's commands executed, send response to sliceOM###
    def invokeSliceOMInterface(self, url, data, task_id, nfmJob_id):
        print 'send to slice O&M'
        data_urlencode = json.JSONEncoder().encode(data)
        request = urllib2.Request(url,data_urlencode)
    
    #######forwad command to nfm driver #######
    def forwardToDriver(self, data, url_info):
        url = API.getUrl( url_info )
        nfmJob_id = self.getNfmJob_id()
        t = threading.Thread(target=self.invokeDriverInterface, args = [url, data, nfmJob_id])
        t.start()
        return nfmJob_id


    def sendToUpper(self, data,  url_info):
        opJob_id = data["opJob_id"]
        if "detail" not in data:
            return
        detail = data['detail']
        task_id = detail[0]['task_id']
        nfmJob_id = self.task_dict[task_id][opJob_id]
        response = {}
        response['nfmJob_id'] = nfmJob_id
        response['detail'] = data['detail']
        response_urlencode = json.JSONEncoder().encode( response )
        url = API.getUrl( url_info )
        request = urllib2.Request(url,response_urlencode)
        print "DEBUG : ", response_urlencode
        for detail_item in detail:
            task_id = detail_item['task_id']
            self.task_dict[task_id].pop(opJob_id)
        if self.task_dict[task_id] == {}:
            self.task_dict.pop(task_id)
        

    def getNfmJob_id(self):
        now = datetime.datetime.now().microsecond
        return str(now)

    def recordNfmDriverResponse(self, data):

	opJob_id = data['opJob_id']
        if "detail" not in data:
            return
        detail = data['detail']
        for detail_item in detail:
            task_id = detail_item['task_id']
            result = detail_item['result']
	    if 'errors' in detail_item:
	        errors = detail_item['errors']
	        for error in errors:
		    slice_id = error['slice_id']
		    vnf_id = error['vnf_id']
		    vnfc_id = error['vnfc_id']
		    interface_id = error['interface_id']
		    error_info = error['error_information']
		    print "ERROR: ", slice_id, " : ", vnf_id, " : ", vnfc_id, " : ", interface_id, " error info : ", error_info

nfm = NFM()
API = api_gateway()

@app.route('/5gslm/iaa/nfm/v1/interface/invoking/json', methods = ['POST'])
def nfmSingleInterfaceInvoking():
    '''
    record task_id, then forward the request to driver
    '''
    data = eval( request.get_data() )
    url_info = {'module':'nfm_driver', 'interface':'interface_invoking','metadata':{'driver_name':'ansible'}}
    nfmJob_id = nfm.forwardToDriver(data, url_info)
    return nfmJob_id

@app.route('/5gslm/iaa/nfm/v1/interfaces/invoking/json', methods = ['POST'])
def nfmInterfacesInvoking():
    '''
    record task_id, then forward the request to driver
    '''
    data = eval( request.get_data() )
    url_info = {'module':'nfm_driver', 'interface':'interfaces_invoking','metadata':{'driver_name':'ansible'}}
    nfmJob_id = nfm.forwardToDriver(data, url_info)
    return nfmJob_id, 202, {'Content-Type' : 'application/json'}


@app.route('/5gslm/iaa/nfm/v1/interface/deployment/json', methods = ['POST'])
def nfmInterfaceDeployment():
    '''
        record slice_id and task_id ,then forward the request to driver
    '''
    data = eval( request.get_data() )
    print "###########debug : deployment ", data
    url_info = {'module':'nfm_driver', 'interface':'file_deployment','metadata':{'driver_name':'ansible'}}
    nfmJob_id = nfm.forwardToDriver(data, url_info)
    return nfmJob_id


@app.route('/5gslm/iaa/nfm/v1/nfm_driver/interface_invoking/response/json', methods = ['POST'])
def nfmDriverInvokingResponse():
    data = eval( request.get_data() )
    print "###########debug : deployment ", data

    nfm.recordNfmDriverResponse(data)
    
    url_info = {'module': 'plan_engin', 'interface':'interface_invoking_response'}
    nfm.sendToUpper(data, url_info)
    return "get", 202, {'Content-Type' : 'application/json'}


@app.route('/5gslm/iaa/nfm/v1/nfm_driver/file_deployment/response/json', methods = ['POST'])
def nfmDriverDeploymentResponse():
    data = eval( request.get_data() )
    task_id = data['task_id']
    nfm.recordNfmDriverResponse(data)
    url_info = {'module': 'sliceOM', 'interface':'file_deployment_response'}
    nfm.sendToUpper(data, url_info)
    return "get", 202, {'Content-Type' : 'application/json'}


if __name__=='__main__':
    print 'main()'
    app.run(host = '0.0.0.0')
