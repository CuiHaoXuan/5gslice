class vnf():
    def __init__(self, definition):
        self.node_type = 'vnf_node'
        self.requirements = definition['requirements']
    def check_requirements(self, req):
        for key in self.requirements:
            if key not in req:
		print 'ERROR : key is : ', key
                return "bad requirement"
        return "legal requirement"

class vdu():
    def __init__(self,definition):
        self.node_type = 'vdu_node'
        self.properties = definition['properties']
    def get_type(self, key):
        if key not in self.properties:
            return "bad key"
        _type = self.properties[key]['type']
        if _type == "string":
            return str
        elif _type == "int":
            return int
        else:
            return None
    
    @staticmethod
    def changeUserPasswd(username, passwd, ssh_config = "\n"):
		ssh_config = "#!/bin/sh\nsed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config\npasswd root <<EOF\n" + passwd + '\n' + passwd + '\n' + "EOF\nservice ssh restart\n"

		return ssh_config
		#return "#!/bin/sh\ncp -f /home/" +  username + "/.ssh/authorized_keys /root/.ssh/\nuseradd " + username + "\npasswd " + username +" <<EOF\n" + passwd + "\n" + passwd + "\n" + "EOF\n" + ssh_config + "EOF\n"

class tosca:

    default_net_id = "eced47fb-317b-42a1-bc55-beff769460b7"
    default_image_type = 'hss'
    '''
    outputInfo:{
        (outputVnfdId):{ 
            'outputVnfdId' :       
        }
    }
    '''
    def __init__(self, data ):
        self.tosca_data = data
	self.res_info = {'output' : {}}
        self.result_data = {}
        self.node_types = {}
        self.scaling_group = {}
   
    def __getNodeTypes(self):
        node_types_definition = self.tosca_data['node_types']
        #print 'node_types_definition is : ', node_types_definition
        for node_type_description in node_types_definition:
            derived_from = node_types_definition[node_type_description]['derived_from']
            n_type = derived_from.split('.')[-1]
	    #print 'DEBUG : ', n_type
            if n_type == "VNF":
                n_type_desc = vnf( node_types_definition[node_type_description] )
                n_id = node_type_description.split('.')[-1]
            elif n_type == "VDU":
                n_type_desc = vdu(node_types_definition[node_type_description])
                n_id = node_type_description.split('.')[-1]
            else:
                n_type_desc = None
            if n_type not in self.node_types:
                self.node_types[n_type] = {}
            self.node_types[n_type][n_id] = n_type_desc
    
    def __getNodeTypeDesc(self, n_type, n_id):
        if n_type not in self.node_types or n_id not in self.node_types[n_type]:
            print 'n_type not in self.node_types or n_id not in self.node_types[n_type]'
            return None
        else:
            return self.node_types[n_type][n_id]

    def getHeatStackName(self):
        return self.tosca_data['metadata']['id']

    def getResInfo(self):
        return self.res_info

    def __createParameter(self,net_id = default_net_id):
        self.result_data['parameter'] = {'NetID' : net_id}

    def __createStackName(self):
        stack_name = self.tosca_data['description']
        self.result_data['stack_name'] = stack_name + '01'
	self.res_info['stack_name'] = stack_name + '01'

    def __createTemplateVersion(self):
        if 'template' not in self.result_data:
            self.result_data['template'] = {}
        self.result_data['template']['heat_template_version'] = "2016-10-14"

    def __createTemplateDescription(self):
        metadata_id = self.tosca_data['metadata']['id']
        metadata_vendor = self.tosca_data['metadata']['vendor']
        metadata_version = self.tosca_data['metadata']['version']
        self.result_data['template']['description'] = "id is : " + str(metadata_id) + " vendor is : " + str(metadata_vendor) + " metadata_version is : " + str(metadata_version)

    def __createTemplateParameter(self):
        if 'template' not in self.result_data:
            self.result_data['template'] = {}
        if 'parameters' not in self.result_data['template']:
            self.result_data['template']['parameters'] = {}

        self.result_data['template']['parameters']['NetID'] = {\
                'default' : self.default_net_id, \
                'type' : 'string' \
                }

    def __createTemplateResourceRouter(self):
        substitution_mappings = self.tosca_data['topology_template']['substitution_mappings']
        n_type = substitution_mappings['node_type'].split('.')[-2]
        n_id = substitution_mappings['node_type'].split('.')[-1]
        req = substitution_mappings['requirements']
        print "1111111111111DEBUG!!!! req is : ", req
        print "222222222222DEBUG!!!! n_type is : ", n_type
        if n_type == 'VNF':
            node_type_desc = self.__getNodeTypeDesc(n_type, n_id)
            res = node_type_desc.check_requirements(req)
            print "222222222DEBUG!!! res is : ", res
            if res == "bad requirement":
                print "in __createTemplateResourceRouter : bad requirement"
                return
            for key in req:
                if 1: #key != 'virtualLink_{{mgmtAgent}}' and key != 'virtualLink_mgmtAgent':
                    cp = req[key].split(',')[0][1:]
                    print "!!!!!!!DEBUG , key is :  ",key
                    vdu_id = self.tosca_data['topology_template']['node_templates'][cp]['requirements']['virtualbinding']
                    vdu_id = vdu_id[ vdu_id.find('_')+1 :  ]
                    print "!!!!!!DEBUG, __createCPVduIdPublicIP : ",vdu_id
                    self.__createCPVduIdPublicPrivate(vdu_id)
                    self.__createCPVduIdPublicIP(vdu_id)

        if 'resources' not in self.result_data['template']:
            self.result_data['template']['resources'] = {}
        self.result_data['template']['resources']['router'] = {
                'type' : 'OS::Neutron::Router',
                'properties' : {
                    'name' : n_id + "_router",
                    'external_gateway_info' : {'network' : {'get_param' : 'NetID'}}
                    }
                }
    def __createCPVduIdPublicPrivate(self, vduId):
        port = 'CP_' + vduId + '_public_private'
        if 'resources' not in self.result_data['template']:
            self.result_data['template']['resources'] = {}
        self.result_data['template']['resources'][port] = {
                'type' : 'OS::Neutron::Port',
                'properties' : {
                    'name' : 'CP_' + vduId + '_public_private',
                    'network' : {'get_resource' : 'internal_VL_Net_private'},
                    'fixed_ips' : [{'subnet' : {'get_resource' : 'internal_VL_Sub_private'}}]
                    }
                }
    def __createCPVduIdPublicIP(self, vduId):
        key = 'CP_' + vduId + '_public_ip'
        port_id = 'CP_' + vduId + '_public_private'
        if 'resources' not in self.result_data['template']:
            self.result_data['template']['resources'] = {}
        self.result_data['template']['resources'][key] = {
                'type' : "OS::Neutron::FloatingIP",
                'properties' : {
                    'floating_network' : {'get_param' : 'NetID'},
                    'port_id' : {'get_resource' : port_id}
                    }
                }

    def __createTemplateVDU(self):
        nodes = self.tosca_data['topology_template']['node_templates']
        

        if 'resources' not in self.result_data['template']:
            self.result_data['template']['resources'] = {}

        for key in nodes:
            if 'type' not in nodes[key]:
                continue
            if 'tosca.nodes.nfv.VDU' in nodes[key]['type']:
                n_id = nodes[key]['type'].split()[-1]
                vim_type = nodes[key]['properties']['vim_type']
                vim_flavor = nodes[key]['properties']['flavor_type']
                if vim_flavor != 'm1.huge': #######!!!!!!!!!!!!!#
                    vim_flavor = 'm1.huge'
                if 'image_name' in nodes[key]['properties']:
                    image_type = nodes[key]['properties']['image_name']
		elif 'image_name' not in nodes[key]['properties']:
                    image_type = self.default_image_type

                
                #create vdu-networks:
                network_list = []
                vdu_id = key[key.find('_') + 1 :]
                network_list.append({'port' : {'get_resource' : 'CP_' + vdu_id + '_public_private'}})


                
                self.result_data['template']['resources'][key] = {
                        'type' : 'OS::Nova::Server',
                        'properties' : {
                            'name' : key,
                            'flavor' : vim_flavor,
                            'image' : image_type,
                            'key_name' : 'mykey',
                            'networks' : network_list
                            }
                        }
                '''
                if 'username' in nodes[key]['properties'] and 'password' in nodes[key]['properties']:
                    username = nodes[key]['properties']['username']
		    passwd = nodes[key]['properties']['password']
                    if username == 'ubuntu':
                        username = 'hss'
                        passwd = '123'
                    user_data = vdu.changeUserPasswd(username, passwd)#!!!!!!!!!!!for test  
                    self.result_data['template']['resources'][key]['properties']['user_data'] = user_data
                '''        
    def __createPrivatePort(self, binding_vdu_id, virtual_link):
        return
    
    def __createPublicPort(self, binding_vdu_id):
        key = 'CP_' + binding_vdu_id + '_public_private'
        fixed_ips = []
        fixed_ips.append( {'subnet' : {'get_resource' : 'internal_VL_Sub_private'}})
        self.result_data['template']['resources'][key] = {
                'type' : 'OS::Neutron::Port',
                'properties' : {
                    'name' : key,
                    'network' : {'get_resource' : 'internal_VL_Net_private'},
                    'fixed_ips' : fixed_ips
                    }
                }



    def __createTemplatePorts(self):
        nodes = self.tosca_data['topology_template']['node_templates']
        for key in nodes:
            if 'type' not in nodes[key]:
                continue
            if 'tosca.nodes.nfv.CP' in nodes[key]['type']:
                binding_node = nodes[key]['requirements']['virtualbinding']
                binding_vdu_id = binding_node[ binding_node.find("_") + 1 :]#VDU_ID
                if 'virtualLink' in nodes[key]['requirements']:
                    #port link to private network
                    virtual_link = nodes[key]['requirements']['virtualLink']
                    self.__createPrivatePort(binding_vdu_id, virtual_link)
                else:
                    self.__createPublicPort(binding_vdu_id)

    def __createTemplateVLNetPrivate(self):
        
        if 'resources' not in self.result_data['template']:
            self.result_data['template']['resources'] = {}
        dns_nameservers = []
        allocation_pools = []

        dns_nameservers.append("8.8.8.8")
        allocation_pools.append( {'start':"192.168.1.100",'end':"192.168.1.150"})

        self.result_data['template']['resources']['internal_VL_Net_private'] = { \
                'type': "OS::Neutron::Net",\
                'properties': {\
                    'name' : 'internal_VL_Net_private'\
                    }\
                }
        self.result_data['template']['resources']['internal_VL_Sub_private'] = { \
                'type' : "OS::Neutron::Subnet",\
                'properties' : {
                    'network_id':{'get_resource':"internal_VL_Net_private"},\
                    'dns_nameservers': dns_nameservers,\
                    'cidr':"172.168.10.0/24",\
                    'ip_version':'4'\
                    }\
                }

        self.result_data['template']['resources']['router_interface_public'] = {
                'type': "OS::Neutron::RouterInterface", \
                'properties':{ \
                    'router':{'get_resource':'router'},\
                    'subnet':{'get_resource':'internal_VL_Sub_private'}\
                    }\
                }

    def __createOutput(self):
        tosca_outputs = self.tosca_data['topology_template']['outputs']
        if 'outputs' not in self.result_data['template']:
            self.result_data['template']['outputs'] = {}
        for cp in tosca_outputs:
            attr = tosca_outputs[cp]['attr']
            node = tosca_outputs[cp]['node']
            get_attr = []
            
            if attr == 'private_ip':

		binding_vdu_id  = self.tosca_data['topology_template']['node_templates'][node]['requirements']['virtualbinding']
                if binding_vdu_id in self.scaling_group:
                    sp_id = self.scaling_group[binding_vdu_id]
                    key = 'refs_map' + sp_id
                    get_attr.append(sp_id)
                    get_attr.append('refs')
                    self.result_data['template']['outputs'][key] = {
                            'value' : {
                                'get_attr' : get_attr
                                }
                            }
		    self.res_info['output'][cp] = key
                else:
                    get_attr.append(binding_vdu_id)
                    get_attr.append('networks')
                    get_attr.append('internal_VL_Net_private')
                    get_attr.append(0)
                    self.result_data['template']['outputs'][cp] = {
                            'value' : {'get_attr' : get_attr}
                            }
		    self.res_info['output'][cp]  = cp

            elif attr == 'public_ip' :
                
		binding_vdu_id  = self.tosca_data['topology_template']['node_templates'][node]['requirements']['virtualbinding']
		get_attr.append(binding_vdu_id)
                get_attr.append('networks')
                get_attr.append('internal_VL_Net_private')
                get_attr.append(1)
                self.result_data['template']['outputs'][cp] = {
                            'value' : {'get_attr' : get_attr}
                            }
		self.res_info['output'][cp] = cp
            
            elif attr == 'alarm_url':
                get_attr.append(node + '_policy')
                get_attr.append('signal_url')
                key = node + '_scaling_url'
                self.result_data['template']['outputs'][key] = {
                        'value' : {
                            'get_attr' : get_attr
                            }
                        }
		self.res_info['output'][cp] = key



    def __createScalingPolicy(self):####'targets' only has one vdu 
        scaling_policies = self.tosca_data['topology_template']['policies']
        for sp in scaling_policies:
            increment = scaling_policies[sp]['properties']['increment']
            min_instances = scaling_policies[sp]['properties']['min_instances']
            max_instances = scaling_policies[sp]['properties']['max_instances']
            default_instances = scaling_policies[sp]['properties']['default_instances']
            vdu_id = scaling_policies[sp]['properties']['targets'][0]
            self.scaling_group[ vdu_id ] = sp
            vdu = self.result_data['template']['resources'][vdu_id]
            self.result_data[sp] = {
                    'type' : 'OS::Heat::AutoScalingGroup',
                    'properties' : {
                        'min_size' : min_instances,
                        'max_size' : max_instances,
                        'desired_capacity' : default_instances,
                        'resources' : {
                            'type' : vdu['type'],
                            'properties' : {
                               # 'vim_type' : vdu['properties']['vim_type'],
                                'flavor' : vdu['properties']['flavor'],
                                'image' :  vdu['properties']['image'],
                                'user_data' : vdu['properties']['user_data']
                                }
                            }
                        }
                    }



    def __createTemplate(self):
        self.__createTemplateVersion()
        self.__createTemplateDescription()
        self.__createTemplateParameter()
        self.__getNodeTypes()
        self.__createTemplateResourceRouter()
        self.__createTemplateVDU()
        self.__createTemplatePorts()
        self.__createTemplateVLNetPrivate()

    def toscaToJson(self, tosca_file_name = None):
        self.__createParameter()
        self.__createStackName()
        self.__createTemplate()
        self.__createScalingPolicy()#__createPolicy must be invoked before __createOutput
        self.__createOutput()
	return self.result_data



    
