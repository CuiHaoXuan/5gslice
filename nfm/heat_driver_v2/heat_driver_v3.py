import os
import types
import logging
import json
import threading
import uuid
import urllib2
import copy
import yaml
import re
import time
import random
import stackinformation
from sshAgent import sshAgent
from flask import Flask
from flask import request

app = Flask(__name__)


true = 'True'
false = 'False'
default_version = '2016-10-14'
default_public_net = 'f9e0f188-0d29-49b4-8676-e0def23e62a5'
default_granularity = 'vnfc'
SavePath = os.getcwd() + '/hot'

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
        self.heat_res_info[vnf_res_id]['vnfResStatus'] = vnf_res_status
        self.vnf_res_info_lock.release()

    def setDcResId(self, vnf_res_id, dc_res_id):
        self.vnf_res_info_lock.acquire()
        self.heat_res_info[vnf_res_id]['dcResId'] = dc_res_id
        self.vnf_res_info_lock.release()

    def setHeatStackId(self, vnf_res_id, heat_stack_id):
        self.vnf_res_info_lock.acquire()
        self.heat_res_info[vnf_res_id]['heatStackId'] = heat_stack_id
        self.vnf_res_info_lock.release()

    def getStackName(self, vnf_res_id):
        return self.heat_res_info[vnf_res_id]['stack_name']

    def setStackName(self, vnf_res_id, stack_name):
        self.vnf_res_info_lock.acquire()
        self.heat_res_info[vnf_res_id]['stack_name'] = stack_name
        self.vnf_res_info_lock.release()

    def setRelatedVimInfo(self, vim_type, vim_mgr_end_point):
        self.vnf_res_info_lock.acquire()
        self.heat_res_info[vnf_res_id]['relatedVimInfo'] = {
            'vimType' :  vim_type,
            'vimMgrEndPoint' : vim_mgr_end_point
        }
        self.vnf_res_info_lock.release()

    def InitOutputInfo(self, vnf_res_id, output_vnfd_id):
        self.vnf_res_info_lock.acquire()
        if 'outputInfo' not in self.heat_res_info[vnf_res_id]:
            self.heat_res_info[vnf_res_id]['outputInfo'] = {}
        self.heat_res_info[vnf_res_id]['outputInfo'][output_vnfd_id] = { \
            'outputHeatId' : 'null', \
        }
        self.vnf_res_info_lock.release()

class heatConvertor:
    def __init__(self):
        self.vnf_res_info = vnfResInfo()
    def createVnfResInt(self, data):
        self.HOT = {}
        slice_res_id = data['sliceResId']
        dc_res_id = data['dcResId']
        vnfd_content = json.dumps(data['vnfdContent'])
        vnfd_content = vnfd_content.decode("unicode-escape")
        vnfd_content = yaml.load(vnfd_content)
        vnf_res_id = vnfd_content['description'] + '01'
        self.dir = SavePath + '/' + self.__getTime() + vnf_res_id
        self.file = self.__getTime() + vnf_res_id
        cmd = "mkdir %s"%(self.dir)
        os.system(cmd)

        self.vnf_res_id = vnf_res_id
        self.vnf_res_info.createVnfInfo( vnf_res_id )
        for k in vnfd_content['topology_template']['outputs'].keys():
            self.vnf_res_info.InitOutputInfo(vnf_res_id, k)
        self.vnf_res_info.setVnfInfoSliceResId(vnf_res_id, slice_res_id)
        self.vnf_res_info.setDcResId(vnf_res_id,  dc_res_id )
        self.stack_name = vnfd_content['description'] + '01'
        self.vnf_res_info.setStackName(vnf_res_id, self.stack_name)
        status = self.__convert(vnfd_content)
        self.vnf_res_info.setVnfResStatus(vnf_res_id, status )
        return  {'vnfResId': self.vnf_res_id, 'vnfResStatus': status}

    def __convert(self,vnfd_content):
        self.__setHeatVersion(default_version)
        self.__setParameters(default_public_net)
        status = self.__setResources(vnfd_content)
        return status

    def __setHeatVersion(self,version):
        self.HOT['heat_template_version'] = version

    def __setParameters(self,public_net):
        self.HOT['parameters'] = {}
        self.HOT['parameters']['public_net'] = {
            'type':'string',
            'default': public_net 
        }

    def __setResources(self,vnfd_content):
        self.HOT['resources'] = {}
        self.HOT['outputs'] = {}
        self.__vnfc_scaling(vnfd_content)
        file_name = self.__storeHOT()
        status = self.__deployHOT(file_name)
        return status

    # command out at 1-19
    def __deployHOT(self,file_name):
        host = sshAgent('192.168.0.21', 'root', '123456')
        host.connect()
        cmd1 = '. /demo-openrc'
        host.send(cmd1)
        cmd2 = 'openstack stack create -t /autoscaling/test/heat_driver_test/%s %s'%(self.file + '/' + file_name,self.stack_name)
        result = host.send(cmd2)
        result = result.decode("unicode-escape")
        status = 'failed'
        if result.find("CREATE_IN_PROGRESS") != -1 or result.find("CREATE_COMPLETE") != -1:
            status = 'deploying'
        host.close()
        return status

    def __storeHOT(self):
        time = self.__getTime()
        file_name = 'vnf-' + time + '@' + self.vnf_res_id +'.yaml'
        file_path = self.dir  + '/' + file_name
        print file_path
        fd = open(file_path ,'w')
        for key in ['heat_template_version','parameters','resources','outputs']:
            middle = {
                key : self.HOT[key]
            }
            tmp = yaml.dump(middle)
            if key == 'heat_template_version':
                tmp = tmp[1:]
                tmp = tmp[:-2] + '\n'
            fd.write(tmp)
        fd.close()
        scp_put = '''
                spawn scp -r %s  %s@%s:%s
                expect "(yes/no)?" {
                send "yes\r"
                expect "password:"
                send "%s\r"
                } "password:" {send "%s\r"}
                expect eof
                exit'''
        os.system("echo '%s' > scp_put.cmd" % (scp_put % (self.dir, 'root' , '192.168.0.21', '/autoscaling/test/heat_driver_test/', '123456', '123456')))
        os.system('expect scp_put.cmd')
        os.system('rm scp_put.cmd')
        return file_name

    def __getTime(self):
        return time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time()))

    def __createCIDR(self):
        cidr_list = [ str(random.randint(0,254))  for i in range(2) ]
        cidr_str ='172.' +  ".".join(cidr_list) + '.0/24'
        return cidr_str

    def __vnfc_scaling(self,vnfd_content):
        nodes = vnfd_content['topology_template']['node_templates']
        policies = {}
        for policy, properties in vnfd_content['topology_template']['policies'].items():
            increment = int(properties['properties']['increment'])
            target = properties['properties']['targets'][0]
            if target in policies :
                if increment > 0:
                    policies[target]['out'] = increment 
                else:
                    policies[target]['in'] = increment
            else:
                policies[target] = {
                    'target' : target,
                    'cooldown' : properties['properties']['cooldown'],
                    'max_instances' : properties['properties']['max_instances'],
                    'min_instances' : properties['properties']['min_instances'],
                    'default_instances' : properties['properties']['default_instances']
                }
                if increment > 0 :
                    policies[target]['out'] = increment
                else:
                    policies[target]['in'] = increment
        for key in nodes:
            if key in policies.keys() and 'tosca.nodes.nfv.VDU' in nodes[key]['type']:
                policy = policies[key]
                if 'image_name' in nodes[key]['properties']:
                    image = nodes[key]['properties']['image_name']
                flavor = nodes[key]['properties']['flavor_type']
                print key
                key = re.match(r'VDU_\{\{(.*?)\}\}.*',key).group(1)
                if key.find('-') != -1 :
                        key = re.match(r'(.*?)-.*',key).group(1)
                filename = '%s/%s.yaml'%(self.dir,key)
                if not(os.path.exists(filename)):
                    cmd = 'cp %s %s'% (SavePath + '/single-vnfc.yaml',filename)
                    os.system(cmd)
                    cmd = "sed -i 's/server/%s/g' %s"%(key,filename)
                    os.system(cmd)
                typename = key + '.yaml'
                self.HOT['resources'][key] = {
                    'type':'OS::Heat::AutoScalingGroup',
                    'properties': {
                         'min_size': policy['min_instances'],
                         'max_size': policy['max_instances'],
                         'desired_capacity': policy['default_instances'],
                         'resource' : {
                              'type' : typename,
                              'properties': {
                                   'image': 'trustyMonitored',
                                   'flavor': 'm1.small',
                                   'public_net': {
                                       'get_param': 'public_net'
                                   },
                                   'private_net': {
                                       'get_resource': 'internal_VL_Net_private'
                                   }
                              }
                         }
                    }
                }
                key_scaling_up = key + "_SCALING_UP"
                key_scaling_down = key + "_SCALING_DOWN"
                self.HOT['resources'][key_scaling_up] = {
                     'type':'OS::Heat::ScalingPolicy',
                     'properties': {
                         'adjustment_type': 'change_in_capacity',
                         'auto_scaling_group_id': {
                              'get_resource': key
                          },
                         'cooldown': policy['cooldown'] ,
                         'scaling_adjustment': policy['out'] 
                     }
                }
                self.HOT['resources'][key_scaling_down] = {
                    'type':'OS::Heat::ScalingPolicy',
                    'properties': {
                        'adjustment_type': 'change_in_capacity',
                        'auto_scaling_group_id': {
                            'get_resource': key
                        },
                        'cooldown': policy['cooldown'],
                        'scaling_adjustment': policy['in']
                     }
                }
                self.HOT['outputs'][key_scaling_down] = {
                    'value' : {
                        'get_attr' : [ key_scaling_down,'signal_url']
                    }
                }
                self.HOT['outputs'][key_scaling_up] = {
                    'value' : {
                        'get_attr' : [ key_scaling_up,'signal_url']
                    }
                }
                self.HOT['outputs'][key+'_asg_size'] = {
                    'value' : {
                        'get_attr' : [ key,'current_size']
                    }
                }
                self.HOT['outputs'][key+'_refs'] = {
                    'value' : {
                        'get_attr' : [ key,'refs_map']
                    }
                }
                continue
            if 'tosca.nodes.nfv.VL.ELAN' in nodes[key]['type']:
                self.HOT['resources']['internal_VL_Net_private'] = {
                    'type' : 'OS::Neutron::Net'
                }
                self.HOT['resources']['internal_VL_Sub_private'] = {
                    'type' : 'OS::Neutron::Subnet',
                    'properties': {
                        'cidr': self.__createCIDR(),
                        'dns_nameservers': ['8.8.8.8'],
                        'ip_version' : 4,
                            'network_id' : { 'get_resource' : 'internal_VL_Net_private' }
                        }
                }
                self.HOT['resources']['router'] = {
                    'type' : 'OS::Neutron::Router',
                    'properties' : {
                        'external_gateway_info' : {
                            'network' : {
                                'get_param' :  'public_net'
                            }
                        }
                    }
                }
                self.HOT['resources']['router_interface_public'] = {
                    'type' : 'OS::Neutron::RouterInterface',
                    'properties' : {
                        'router' : {
                            'get_resource' : 'router' 
                        },
                        'subnet' : {
                            'get_resource' : 'internal_VL_Sub_private'
                        }
                    }
                }
                continue
            if 'tosca.nodes.nfv.VDU' in nodes[key]['type'] :
                if 'image_name' in nodes[key]['properties']:
                    image = nodes[key]['properties']['image_name']
                flavor = nodes[key]['properties']['flavor_type']
                if key.find('{') == -1:
                    key = key[4:]
                else:
                    key = re.match( r'.*\{\{(.*?)\}\}.*', key, re.M|re.I).group(1)
                self.HOT['resources'][key] = {
                    'type':'OS::Nova::Server',
                    'properties' : {
                        'image' : 'trustyProxy',
                        'flavor': 'm1.small',
                        'key_name' : 'mykey'
                    }
                }
                CP = 'CP_' + key
                self.HOT['resources'][key]['properties']['networks'] = [{
                    'port' : {
                        'get_resource' : CP+'_public_private'
                    }
                }]
                self.HOT['outputs'][key + '_IPs'] = {
                    'value': {
                        'get_attr': [ key , 'networks']
                    }
                }
                continue
            if 'tosca.nodes.nfv.CP' in nodes[key]['type'] :
                if key.find('{') == -1:
                    floating_ip = key + '_public_ip'
                    key = key +  '_public_private'
                elif key.find('PORTAL') != -1 :
                    match = re.match( r'.*_\{\{(.*?)\}\}_.*', key, re.M|re.I)
                    key = 'CP_' + match.group(1) + '_public_private'
                    floating_ip = 'CP_' + match.group(1) + '_public_ip'
                else:
                    continue
                self.HOT['resources'][key] = {
                    'type': 'OS::Neutron::Port',
                    'properties' : {
                        'fixed_ips' : [{
                            'subnet' : {
                                'get_resource' : 'internal_VL_Sub_private'
                            }
                        }],
                        'network': {
                            'get_resource' : 'internal_VL_Net_private'
                        }
                    }
                }
                self.HOT['resources'][floating_ip] = {
                    'type' : 'OS::Neutron::FloatingIP',
                    'properties' : {
                        'floating_network' :  {
                            'get_param' :  'public_net'
                        },
                        'port_id' : {
                            'get_resource' : key
                        }
                    }
                }

    def updateVnfRes(self,vnf_res_id):
        heatstackinfo = stackinformation.stackinformation()
        stack_name = self.vnf_res_info.getStackName(vnf_res_id)
        print "==============stack name=============="
        print stack_name
        resp_dict = heatstackinfo.getStackInfo('demo','demo',stack_name)
        print resp_dict
        if resp_dict['stack_status'] == 'CREATE_IN_PROGRESS':
            return {'vnfResStatus' : 'deploying'}
        if resp_dict['stack_status'] == 'CREATE_COMPLETE':
            for k,v in self.vnf_res_info.heat_res_info[vnf_res_id]['outputInfo'].items():
                match0 = re.match(r'SP_(.*)_scale_(.*)_url',k)
                if not type(match0) is types.NoneType :
                    if match0.group(2) == 'out':
                        flag = match0.group(1) + '_SCALING_UP'
                    else:
                        flag = match0.group(1) + '_SCALING_DOWN'
                    self.vnf_res_info.heat_res_info[vnf_res_id]['outputInfo'][k]['value'] = resp_dict[match0.group(1)+'ASG'][flag]
                    continue
                match1 = re.match(r'CP_{{(.*?)-NODE}}_{{(.*?)-PORTAL}}_(.*)',k)
                if not type(match1) is types.NoneType :
                    ips = []
                    print "==============ASG================="
                    print resp_dict[match1.group(1)+'ASG']['servers']
                    for server , info in resp_dict[match1.group(1)+'ASG']['servers'].items():
                        tmp = {
                            'server' : server,
                            match1.group(3): info['IP'][match1.group(3)]['IP'],
                            'LaunchTime' :  info['LaunchTime']
                        }
                        ips.append(tmp)
                        print "tmp"
                        print tmp
                    print "ips"
                    print ips
                    self.vnf_res_info.heat_res_info[vnf_res_id]['outputInfo'][k]['value'] = copy.deepcopy(ips)
                    print "=================ips================="
                    print self.vnf_res_info.heat_res_info[vnf_res_id]['outputInfo'][k]
                    continue
                match2 = re.match(r'CP_(.*)_{{(.*?)-NODE}}_(.*)',k)
                if not type(match2) is types.NoneType :
                    for i in resp_dict.keys():
                        if i.find(match2.group(1)) != -1:
                            self.vnf_res_info.heat_res_info[vnf_res_id]['outputInfo'][k]['value'] = resp_dict[i][match2.group(3)]
                            break
                    continue
                match3 = re.match(r'CP_(.*)_(.*)',k)
                if not type(match3) is types.NoneType :
                    self.vnf_res_info.heat_res_info[vnf_res_id]['outputInfo'][k]['value'] = resp_dict[match3.group(1) + '_IPs'][match3.group(2)]
                    continue
            print "=====================self.vnf_res_info================="
            self.vnf_res_info.setVnfResStatus(vnf_res_id, 'completed')
            print self.vnf_res_info.heat_res_info[vnf_res_id]
            return self.vnf_res_info.heat_res_info[vnf_res_id]
        elif resp_dict['stack_status'] == 'CREATE_IN_PROGRESS':
            return {'vnfResStatus' : 'deploying'}
        else:
            self.vnf_res_info.heat_res_info[vnf_res_id]['vnfResStatus'] = 'failed'
            return {'vnfResStatus' : 'failed'}

convertor = heatConvertor()
app = Flask(__name__)
@app.route('/5gslm/iaa/driver/heat/v1/vnf/management/create/json', methods = ['POST'])
def create_vnf():
    data = request.json
    result = convertor.createVnfResInt(data)
    return str(result)

@app.route('/5gslm/iaa/driver/heat/v1/vnf/<vnf_res_id>/resource/json', methods = ['GET'])
def get_resource(vnf_res_id):
    result = convertor.updateVnfRes(vnf_res_id)
    return json.dumps(result)

if __name__=='__main__':
        app.run(host = '0.0.0.0',port = 8093)

