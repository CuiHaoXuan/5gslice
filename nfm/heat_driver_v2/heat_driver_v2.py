import os
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
import stackinfo
import sshAgent
from flask import Flask
from flask import request

app = Flask(__name__)


true = 'True'
false = 'False'
default_version = '2016-10-14'
default_public_net = 'eced47fb-317b-42a1-bc55-beff769460b7'
default_granularity = 'vnfc'
SavePath = '/code_phase_two/nfm/heat_driver_v2/hot'

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
        #print '---------set VnfResStatus----------'
        self.heat_res_info[vnf_res_id]['vnfResStatus'] = vnf_res_status
        self.vnf_res_info_lock.release()


    def setDcResId(self, vnf_res_id, dc_res_id):
        self.vnf_res_info_lock.acquire()
        self.heat_res_info[vnf_res_id]['dcResId'] = dc_res_id
        self.vnf_res_info_lock.release()

    def setHeatStackId(self, vnf_res_id, heat_stack_id):
        self.vnf_res_info_lock.acquire()
        #print "-----set heatStackId --------"
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

class heatConvertor:
    def __init__(self):
        self.vnf_res_info = vnfResInfo()
        #os.system('cat /dev/null > /etc/ansible/hosts')
        #os.system('cat /dev/null > /root/.ssh/config')
        #os.system('cat /dev/null > /root/.ssh/known_hosts')

    def createVnfResInt(self, data):
	self.HOT = {}
	self.dir = SavePath + '/' + self.__getTime()
	cmd = "mkdir %s"%(self.dir)
	os.system(cmd)

        slice_res_id = data['sliceResId']
        dc_res_id = data['dcResId']
        vnfd_content = yaml.load(data['vnfdContent'])
        status = 'deploying'
        vnf_res_id = "0200020"
        self.vnf_res_info.createVnfInfo( vnf_res_id )
        self.vnf_res_info.setVnfInfoSliceResId(vnf_res_id, slice_res_id)
        self.vnf_res_info.setDcResId(vnf_res_id,  dc_res_id )
        self.vnf_res_info.setVnfResStatus(vnf_res_id, status )

        self.__convert(vnfd_content)

        stack_name = vnfd_content['description'] + '01'
        self.vnf_res_info.setStackName(vnf_res_id, stack_name)
	return  {'StackName': stack_name}

    def __convert(self,vnfd_content):
        self.__setHeatVersion(default_version)
        self.__setParameters(default_public_net,default_granularity)
        self.__setConditions()
        self.__setResources(vnfd_content)
        #self.__setOutputs(vnfd_content)
	#data_string = json.JSONEncoder().encode(self.HOT)
	#print type(data_string)
	#print yaml.dump(self.HOT)

    def __setHeatVersion(self,version):
        self.HOT['heat_template_version'] = version

    def __setParameters(self,public_net,granularity):
	self.HOT['parameters'] = {}
	self.HOT['parameters']['public_net'] = {
		'type':'string',
		'default': public_net 
	}
	self.HOT['parameters']['granularity'] = {
		'type':'string',
		'default': granularity 
	}

    def __setConditions(self):
	self.HOT['conditions'] = {}
	self.HOT['conditions']['create_vnfc_res'] = {
		'equals' : [{'get_param':'granularity'},'vnfc']
	}
	self.HOT['conditions']['create_vnf_res'] = {
		'equals' : [{'get_param':'granularity'},'vnf']
	}

    def __setResources(self,vnfd_content):
	self.HOT['resources'] = {}
	self.HOT['outputs'] = {}
        self.__vnfc_scaling(vnfd_content)
	self.__vnf_scaling(vnfd_content)
	self.__storeHOT()

    def __storeHOT(self):
	time = self.__getTime()
	file_name = 'vnf-' + time + '.yaml'
	file_path = self.dir  + '/' + file_name
	fd = open(file_path ,'w')
	for key in ['heat_template_version','parameters','conditions','resources','outputs']:
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
		spawn scp %s/*  %s@%s:%s
		expect "(yes/no)?" {
		send "yes\r"
		expect "password:"
		send "%s\r"
		} "password:" {send "%s\r"}
		expect eof
		exit'''
        os.system("echo '%s' > scp_put.cmd" % (scp_put % (self.dir, 'root' , '10.10.26.179', '/autoscaling/test/heat_driver_test/', '123456', '123456')))
        os.system('expect scp_put.cmd')
        os.system('rm scp_put.cmd')

	
    def __getTime(self):
	return time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time()))

    def __createCIDR(self):
	cidr_list = [ str(random.randint(0,254))  for i in range(2) ]
	cidr_str ='172.' +  ".".join(cidr_list) + '.0/24'
	return cidr_str

    def __vnf_scaling(self,vnfd_content):
	tmp = {
		'heat_template_version': '2016-10-14',
		'parameters' : {
			'public_net': {
				'type' : 'string',
				'description' : 'the provider network'
			}
		},
	}
	resources = {}
        nodes = vnfd_content['topology_template']['node_templates']
        for key in nodes:
            if 'tosca.nodes.nfv.VDU' in nodes[key]['type']:
                if 'image_name' in nodes[key]['properties']:
                    image = nodes[key]['properties']['image_name']
                elif 'image_name' not in nodes[key]['properties']:
                    self.__error_handler('image')
                flavor = nodes[key]['properties']['flavor_type']
                #if !self.__flavor_check(flavor,image) :
                #    self.__error_handler('flavor')
                key = re.match( r'.*\{\{(.*?)\}\}.*', key, re.M|re.I).group(1)
		resources[key] = {
                    'type':'OS::Nova::Server',
		    'properties' : {
			'image' : 'ubuntu14.04',
			'flavor': 'm1.large',
			'key_name' : 'mykey'
		    }
		}
		CP = 'CP_' + key
		resources[key]['properties']['networks'] = [{
			'port' : {
			    'get_resource' : CP+'_public_private'
			}
	        }]
		continue
            if 'tosca.nodes.nfv.CP' in nodes[key]['type']:
                match = re.match( r'.*_\{\{(.*?)\}\}_.*', key, re.M|re.I)
		key = 'CP_' + match.group(1) + '_public_private'
		floating_ip = 'CP_' + match.group(1) + '_public_ip'
		resources[key] = {
		    'type' : 'OS::Neutron::Port',
		    'properties' : {
			'fixed_ips' : [{
			    'subnet' : {
				'get_resource' : 'internal_VL_Sub_private'
			    }
			}],
			'network' : {
			    'get_resource' : 'internal_VL_Net_private'
			}
		    }
		}
		resources[floating_ip] = {
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
		continue
            if 'tosca.nodes.nfv.VL.ELAN' in nodes[key]['type']:
                resources['internal_VL_Net_private'] = {
                        'type' : 'OS::Neutron::Net'
                }
                resources['internal_VL_Sub_private'] = {
                        'type' : 'OS::Neutron::Subnet',
                        'properties': {
                                'cidr': self.__createCIDR(),
                                'dns_nameservers': ['8.8.8.8'],
                                'ip_version' : 4,
                                'network_id' : { 'get_resource' : 'internal_VL_Net_private' }
                        }
                }
                resources['router'] = {
                        'type' : 'OS::Neutron::Router',
                        'properties' : {
                                'external_gateway_info' : {
                                        'network' : {
                                                'get_param' :  'public_net'
                                        }
                                }
                        }
                }
                resources['router_interface_public'] = {
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
	tmp['resources'] = resources
	tmp_yaml = yaml.dump(tmp)
	file_path = self.dir + '/' + vnfd_content['description'] + '.yaml'
        fd = open(file_path,'w')
	fd.write(tmp_yaml)
	fd.close()
	fd_path = SavePath + '/' + 'single-stack.yaml'
	fd = open(fd_path,'r')
	content = fd.read()
	content_dict = yaml.load(content)
	for k in content_dict['resources']:
		key = vnfd_content['description'] + '-' +  k[7:]
		self.HOT['resources'][key] = copy.deepcopy(content_dict['resources'][k])
		self.HOT['resources'][key]['condition'] = 'create_vnf_res'
		if (content_dict['resources'][k]['type'] == 'OS::Heat::AutoScalingGroup'):
			self.HOT['resources'][key]['properties']['resource']['type'] = vnfd_content['description'] + '.yaml'
			self.HOT['outputs'][ vnfd_content['description'] + '_asg_size'] = {
                                'condition' : 'create_vnf_res',
                                'value' : {
                                        'get_attr' : [ key , 'current_size' ]
                                }
			}
			self.HOT['outputs'][ vnfd_content['description'] + '_refs'] = {
                                'condition' : 'create_vnf_res',
                                'value' : {
                                        'get_attr' : [ key , 'refs_map' ]
                                }
                        }
		else:
			self.HOT['resources'][key]['properties']['auto_scaling_group_id']['get_resource'] = vnfd_content['description'] + '-scaling_group'
			self.HOT['outputs'][key] = {
				'condition' : 'create_vnf_res',
				'value' : {
					'get_attr' : [ key , 'signal_url' ]
				}
			}
	fd.close()
	'''
	cmd = ['cp %s/single-stack.yaml %s'%(SavePath,single_stack),
		"sed -i 's/server/%s/g' %s"%(vnfd_content['description'],single_stack),
		"sed -i 's#yaml#%s#g' %s "%(file_path,single_stack) ]
	result = [ os.system(i) for i in cmd ]
	'''

	
    def __vnfc_scaling(self,vnfd_content):
        nodes = vnfd_content['topology_template']['node_templates']
	for key in nodes:
	    if 'tosca.nodes.nfv.VDU' in nodes[key]['type']:
                if 'image_name' in nodes[key]['properties']:
                    image = nodes[key]['properties']['image_name']
                elif 'image_name' not in nodes[key]['properties']:
                    self.__error_handler('image')
                flavor = nodes[key]['properties']['flavor_type']
		#if !self.__flavor_check(flavor,image) :
		#    self.__error_handler('flavor')
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
		#print 'file exsit'
		typename = key + '.yaml'
		self.HOT['resources'][key] = {
                    'type':'OS::Heat::AutoScalingGroup',
                    'condition':'create_vnfc_res',
                    'properties': {
                         'min_size':1,
                         'max_size':3,
                         'desired_capacity':1,
                         'resource' : {
                              'type' : typename,
                              'properties': {
                                   'image': 'ubuntu14.04',
                                   'flavor': 'm1.large',
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
                     'condition': 'create_vnfc_res',
                     'properties': {
                             'adjustment_type': 'change_in_capacity',
                             'auto_scaling_group_id': {
                                     'get_resource': key
                              },
                             'cooldown': 60,
                             'scaling_adjustment': 1
                     }
             	}
		self.HOT['resources'][key_scaling_down] = {
                     'type':'OS::Heat::ScalingPolicy',
                     'condition': 'create_vnfc_res',
                     'properties': {
                             'adjustment_type': 'change_in_capacity',
                             'auto_scaling_group_id': {
                                     'get_resource': key
                              },
                             'cooldown': 60,
                             'scaling_adjustment': -1
                     }
             	}
		self.HOT['outputs'][key_scaling_down] = {
			'value' : {
				'get_attr' : [ key_scaling_down,'signal_url']
			},
			'condition' : 'create_vnfc_res'
		}
		self.HOT['outputs'][key_scaling_up] = {
			'value' : {
				'get_attr' : [ key_scaling_up,'signal_url']
			},
			'condition' : 'create_vnfc_res'
		}
		self.HOT['outputs'][key+'_asg_size'] = {
			'value' : {
				'get_attr' : [ key,'current_size']
			},
			'condition' : 'create_vnfc_res'
		}
		self.HOT['outputs'][key+'_refs'] = {
			'value' : {
				'get_attr' : [ key,'refs_map']
			},
			'condition' : 'create_vnfc_res'
		}
		continue
	    if 'tosca.nodes.nfv.VL.ELAN' in nodes[key]['type']:
		self.HOT['resources']['internal_VL_Net_private'] = {
			'type' : 'OS::Neutron::Net',
			'condition' : 'create_vnfc_res'
		}
		self.HOT['resources']['internal_VL_Sub_private'] = {
			'type' : 'OS::Neutron::Subnet',
			'condition' : 'create_vnfc_res',
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
			},
			'condition' : 'create_vnfc_res'
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
			},
			'condition' : 'create_vnfc_res'
		}		


convertor = heatConvertor()
mystackinfo = stackinfo.stackinfo()

app = Flask(__name__)
@app.route('/5gslm/iaa/driver/heat/v1/vnf/management/create/json', methods = ['POST'])
def create_vnf():
    data = request.json
    result = convertor.createVnfResInt(data)
    return str(result)

@app.route('/5gslm/iaa/driver/heat/v1/vnf/<vnf_res_id>/resource/json', methods = ['GET'])
def get_resource(vnf_res_id):
    return str(mystackinfo.getStackInfo('demo','demo',vnf_res_id))

if __name__=='__main__':
        app.run(host = '192.168.0.9',port = 8193)
