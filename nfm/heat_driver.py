import os
import logging
import json
import threading
import uuid
import urllib2
import yaml
from flask import Flask
from flask import request
from tosca import tosca
from api.api_gateway import api_gateway

app = Flask(__name__)


true = 'True'
false = 'False'

openstack_o_url = "http://10.10.26.179:8004/"
openstack_token_url = "http://10.10.26.179:35357/"


class vnfResInfo:
    
    def __init__(self):
        self.vnf_res_info_lock = threading.Lock()
        self.heat_res_info = {}

    
    '''
    {
        (vnf_res_id):{
            'vnfResStatus' :
            'relatedSliceResId' :
            'vnfResId' :
            'dcResId' :
            'heatStackId':
            'stack_name' :
            'relatedVimInfo' :{
                'vimType' :
                'vimMgrEndPoint' :
            }
            'outputInfo':{
                (outputVnfdId):{
                    'outputHeatId' :
                    'value' :
                }
            }
        }
    }
    '''
    
    def createVnfInfo(self, vnf_res_id):
        self.vnf_res_info_lock.acquire()
        if vnf_res_id in self.heat_res_info:
            self.vnf_res_info_lock.release()
            return
        self.heat_res_info[vnf_res_id] = {}
        self.heat_res_info[vnf_res_id]['vnfResId'] = vnf_res_id
        self.vnf_res_info_lock.release()
   
   
    def getVnfInfo(self, vnf_res_id):
        self.vnf_res_info_lock.acquire()
        if vnf_res_id not in self.heat_res_info:
            self.vnf_res_info_lock.release()
            return None
        else:
            self.vnf_res_info_lock.release()
            return self.heat_res_info[vnf_res_id]
    
    
    def setVnfInfoSliceResId(self, vnf_res_id, slice_res_id):
        self.vnf_res_info_lock.acquire()
        self.heat_res_info[vnf_res_id]['relatedSliceResId'] = slice_res_id
        self.vnf_res_info_lock.release()

    
    def setVnfResStatus(self, vnf_res_id, vnf_res_status):
        self.vnf_res_info_lock.acquire()
        print '---------set VnfResStatus----------'
        self.heat_res_info[vnf_res_id]['vnfResStatus'] = vnf_res_status
        self.vnf_res_info_lock.release()

    
    def setDcResId(self, vnf_res_id, dc_res_id):
        self.vnf_res_info_lock.acquire()
        self.heat_res_info[vnf_res_id]['dcResId'] = dc_res_id
        self.vnf_res_info_lock.release()

    def setHeatStackId(self, vnf_res_id, heat_stack_id):
        self.vnf_res_info_lock.acquire()
        print "-----set heatStackId --------"
        self.heat_res_info[vnf_res_id]['heatStackId'] = heat_stack_id
        self.vnf_res_info_lock.release()

    def setStackName(self, vnf_res_id, stack_name):
        self.vnf_res_info_lock.acquire()
        self.heat_res_info[vnf_res_id]['stack_name'] = stack_name
        self.vnf_res_info_lock.release()
    

    def setRelatedVimInfo(self, vim_type, vim_mgr_end_point):
        self.vnf_res_info_lock.acquire()
        self.heat_res_info[vnf_res_id]['relatedVimInfo'] = { \
                'vimType' :  vim_type, \
                'vimMgrEndPoint' : vim_mgr_end_point \
                }
        self.vnf_res_info_lock.release()

    def setOutputInfo(self, vnf_res_id, output_vnfd_id, output_heat_id, value):
        self.vnf_res_info_lock.acquire()
        if 'outputInfo' not in self.heat_res_info[vnf_res_id]:
            self.heat_res_info[vnf_res_id]['outputInfo'] = {}
        self.heat_res_info[vnf_res_id]['outputInfo'][output_vnfd_id] = { \
				'outputHeatId' : output_heat_id, \
				'value' : value \
                }
        self.vnf_res_info_lock.release()
  

class heatDriver:
    vnf_res_info = vnfResInfo()
    def __init__(self):
        self.vnf_res_info = vnfResInfo() 
        os.system('cat /dev/null > /etc/ansible/hosts')
        os.system('cat /dev/null > /root/.ssh/config')
        os.system('cat /dev/null > /root/.ssh/known_hosts')
       # self.__configLogging()

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

    def __getStackOutput(self,vnf_res_id):
        output_key_list = []
        print "in 150 vnf_res_info is : ", self.vnf_res_info.heat_res_info
        
        info = self.__getTokenId('demo', 'demo')
        if(info == None):
            print 'Error : Autentication failure'
            return
 
        token_id = info['token_id']
        tenant_id = info['tenant_id']

        stack_id = self.vnf_res_info.heat_res_info[vnf_res_id]['heatStackId']
        stack_name = self.vnf_res_info.heat_res_info[vnf_res_id]['stack_name']
        url = openstack_o_url + "v1/" + tenant_id + "/stacks/" + stack_name + "/" + stack_id + "/" + "outputs"
        print 'get output url is ', url
        http_req = urllib2.Request(url)
        http_req.add_header('X-Auth-Token', token_id)

        try:
            r_data = eval( urllib2.urlopen(http_req).read() )
            outputs_list = r_data['outputs']
            for item in outputs_list : 
                output_key = item['output_key']
                output_key_list.append(output_key)
        
        except urllib2.URLError as e:
            if hasattr(e, 'code'):
                print 'get outputs error! Error code : ', e.code
            elif hasattr(e, 'reason'):
                print 'Reason : ', e.reason
            return None
        

        print 'DEBUG :    output_key_list is ', output_key_list
	complete = 1
        for key in output_key_list:
            #if 'privateIp' in key:
            #    if key == 'CP_mgmt_{{HSS-NODE}}_privateIp':
            #        new_key = 'CP_{{HSS-NODE}}_{{HSS-PORTAL}}_publicIp'
            #    elif key == 'CP_mgmt_{{MME-NODE}}_privateIp':
            #        new_key = 'CP_{{MME-NODE}}_{{MME-PORTAL}}_publicIp'
            #    elif key == 'CP_mgmt_{{SPGW-NODE}}_privateIp':
            #        new_key = 'CP_{{SPGW-NODE}}_{{SPGW-PORTAL}}_publicIp'
            #    else:
            #        new_key = key
            #else:
            new_key = key
            print "############debug######"
            print "key is ", key
            print "new_key is", new_key
            print key.split
            url =  openstack_o_url + "v1/" + tenant_id + "/stacks/" + stack_name + "/" + stack_id + "/" + "outputs/" + new_key
            http_req = urllib2.Request(url)
            http_req.add_header('X-Auth-Token', token_id)

            try:
                r_data = urllib2.urlopen(http_req).read() 
                print "------url is ----- -   " ,url
                print "------rdata is -----   ", r_data
                r_data = json.loads(r_data)
                output_value = r_data['output']['output_value']
		if output_value == None:
		    complete = 0
		    return
                self.vnf_res_info.setOutputInfo(vnf_res_id, key, key, output_value)
		print "DEBUG     ",key, "----------------", output_value
            
            except urllib2.URLError as e:
                if hasattr(e, 'code'):
                    print 'get output_value error! Error code : ', e.code
                elif hasattr(e, 'reason'):
                    print 'Reason : ', e.reason
                return None

        if output_key_list:
            self.vnf_res_info.setVnfResStatus(vnf_res_id, 'deploy completes' )




    def __openstackCreateStack(self, hot):
        req = {}
        r_data = {}
        
        #print hot  
        
        info = self.__getTokenId('demo', 'demo')
        if(info == None):
            print 'Error : Autentication failure'
            return
 
        token_id = info['token_id']
        tenant_id = info['tenant_id']
        #req['tenant_id'] = tenant_id
        #req['files'] = hot
        #print hot
        stack_create_url = openstack_o_url + "v1/" + tenant_id + "/stacks"
	print stack_create_url
        #req_urlencode = json.dumps( hot )
        #print "DEBUG:     ",type(hot)
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
        print r_data

        
        stack_id = r_data['stack']['id']
        return stack_id
        

    def __createVnfResId(self):
        return uuid.uuid1()

    def __configLogging(self):
        logging.basicConfig(level = logging.DEBUG, 
                format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt = '%m-%d %H:%M',
                filename = 'heat_driver.log',
                filemode = 'w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
	formatter = logging.Formatter('%(name)-12s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger(' ').addHandler(console)
        self.logger = logging.getLogger('heat_driver')
 
    
    def createVnfResInt( self, data ):
        #heat_driver.loogger.debug("receive a vnf-resource-creating request")
        slice_res_id = data['sliceResId']
        dc_res_id = data['dcResId']
        print type(data['vnfdContent'])
        print data['vnfdContent']
        vnfd_content = eval (str(data['vnfdContent'])) 

	print "vnfd_content type is : ", type(vnfd_content)
        status = 'deploying'

        vnf_res_id = str(self.__createVnfResId())

        self.vnf_res_info.createVnfInfo( vnf_res_id )
        self.vnf_res_info.setVnfInfoSliceResId(vnf_res_id, slice_res_id)
        self.vnf_res_info.setDcResId(vnf_res_id,  dc_res_id )
        self.vnf_res_info.setVnfResStatus(vnf_res_id, status )
        convertor = tosca(vnfd_content)
        hot = json.dumps( convertor.toscaToJson() )
        #hot = json.JSONEncoder().encode(convertor.toscaToJson())
	print hot
	stack_name = vnfd_content['description'] + '01' 
        self.vnf_res_info.setStackName(vnf_res_id, stack_name)
        res_info = convertor.getResInfo()
        stack_id = self.__openstackCreateStack(hot)
        self.vnf_res_info.setHeatStackId(vnf_res_id, stack_id)
        print "in 272 : ", self.vnf_res_info
        return {'status' : 'request accepted', 'vnfResId' : vnf_res_id}

    
    def getVnfResInfo(self, vnf_res_id):
        if vnf_res_id in self.vnf_res_info.heat_res_info:
            print 'vnf_res_info is : ',self.vnf_res_info
            self.__getStackOutput(vnf_res_id)
            return self.vnf_res_info.heat_res_info[vnf_res_id]


driver = heatDriver()
@app.route('/5gslm/iaa/driver/heat/v1/vnf/<vnf_res_id>/resource/json', methods = ['GET'])
def get_resource(vnf_res_id):
    return str (driver.getVnfResInfo(vnf_res_id) )


@app.route('/5gslm/iaa/driver/heat/v1/vnf/management/create/json', methods = ['POST'])
def create_vnf():
    if request.json:
        data = request.json
    elif request.form:
        data = request.form
    print "!!!!!!!!!!!!!!!!!!!!!!!!!data!!!!!!!!!!"
    cmd = 'echo %s >> /10.txt'
    os.system(cmd%(data))
    #res = driver.createVnfResInt(data)
    #print res
    #return str(res)

if __name__=='__main__':
	app.run(host = '0.0.0.0',port = 8093)
