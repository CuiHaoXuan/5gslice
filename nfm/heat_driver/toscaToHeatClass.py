import yaml
import os
import logging
import json
from collections import OrderedDict

class toscaToHOT:

    test_mode = True #just for test, cmd choose from apache_cmd and ftp_cmd

    root_logIn = {'ubuntu': "#!/bin/sh\ncp -f /home/ubuntu/.ssh/authorized_keys /root/.ssh/\npasswd root<<EOF\npassword\npassword\nEOF\n"}
    test_cmd = {    \
            'VDU_WEB-NODE': "#!/bin/sh\ncp -f /home/ubuntu/.ssh/authorized_keys /root/.ssh/\npasswd root<<EOF\npassword\npassword\nEOF\napt-get install -y apache2\nsed -i '$a ServerName localhost' /etc/apache2/apache2.conf\nservice apache2 restart\nsed -i 's/PermitRootLogin without-password/PermitRootLogin yes/g' /etc/ssh/sshd_config\nsed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config\nservice ssh restart\n",  \
            'VDU_FTP-NODE' : "#!/bin/sh\ncp -f /home/ubuntu/.ssh/authorized_keys /root/.ssh/\npasswd root<<EOF\npassword\npassword\nEOF\napt-get install -y vsftpd\n service vsftpd restart\nmkdir /home/uftp\nuseradd -d /home/uftp -s /bin/bash uftp\n passwd uftp<<EOF\nuftp\nuftp\nEOF\nsed -i '$a write_enable=YES' /etc/vsftpd.conf\nsed -i '$a userlist_deny=NO' /etc/vsftpd.conf\n sed -i '$a userlist_enable=YES' /etc/vsftpd.conf\nsed -i '$a userlist_file=/etc/allowed_users' /etc/vsftpd.conf\nsed -i '$a seccomp_sandbox=NO' /etc/vsftpd.conf\ncd /etc/\necho \"uftp\">> allowed_users\nchmod -R 777 /home/uftp\nchown ftp:root /home/uftp\nservice vsftpd restart\n"  \
            }
    default_heat_template_version = "2016-10-14"

    whole_vdu_dict = {}

    node_templates = {}

    substitution_mappings = {}

    HOT = {}

    stack_name = 'default'

    default_image = {
            'ubuntu':'ubuntu14.04',
            'Ubuntu':'ubuntu14.04',
            'centOS':'centOS06'
            }

    #read VNFD from tosca_file_path,and store data in dict 'whole_vdu_dict' 

    def yamlToDict(self, tosca_file_path):

        self.whole_vdu_dict = yaml.load(open(tosca_file_path))
        #completeness check
      #  print self.whole_vdu_dict
        if 'topology_template' not in self.whole_vdu_dict:
            print "ERROR: VNFD is not complete: topology_template is not defined in the VNFD"
            return 'error happened'
        
        if 'substitution_mappings' not in self.whole_vdu_dict['topology_template']:
            print "WARNING: VNFD is not complete: substitution_mappings is not defined in the VNFD"
            return 'error happened'

        if 'node_templates' not in  self.whole_vdu_dict['topology_template']:
            print "ERROR: VNFD is not complete: node_templates is not defined in the VNFD"
            return 'error_happened'

        self.node_templates =  self.whole_vdu_dict['topology_template']['node_templates']
        
        self.substitution_mappings = self.whole_vdu_dict['topology_template']['substitution_mappings']
        
        self.HOT['template'] = {}

    def createStackName(self, stack_name):
        self.stack_name = stack_name
        self.HOT['stack_name'] = self.stack_name
    
    def createVersion(self):
        self.HOT['template']['heat_template_version'] = self.default_heat_template_version 

    def transferDescription(self):
        if 'description' in self.whole_vdu_dict:
            description = self.whole_vdu_dict['description']
        if 'metadata' in self.whole_vdu_dict:
            if('id' in self.whole_vdu_dict['metadata']):
                description =  description + " ; " + "metadata:id is : " \
                        + str(self.whole_vdu_dict['metadata']['id'])
            if 'vendor' in self.whole_vdu_dict['metadata']:
                description =  description + " ; " + "metadata:vendor is : "\
                        + self.whole_vdu_dict['metadata']['vendor']
            if 'version' in self.whole_vdu_dict['metadata']:
                description =  description + " ; " + "metadata:version is : " \
                        + str(self.whole_vdu_dict['metadata']['version'])
            self.HOT['template']['description'] = description

    #create VDU_{vdu_id}

    def transferVdu(self):
        for vdu_name in self.node_templates:
            if 'type' not in self.node_templates[vdu_name]:
                continue
            if 'tosca.nodes.nfv.VDU' not in self.node_templates[vdu_name]['type']:
                continue
            if 'properties' not in self.node_templates[vdu_name]:
                print "ERROR: VNFD is not complete: ", vdu_name,"-properties is not defined in the VNFD"
                return 'error_happened'
            if 'os_type' not in self.node_templates[vdu_name]['properties']:
                print "ERROR: VNFD is not complete: ", vdu_name,"-properties-os_type is not defined in the VNFD"
                return 'error_happened'
            if self.node_templates[vdu_name]['properties']['os_type'] not in self.default_image:
                print "ERROR: ", vdu_name,"-properties -os_type is not correct"
                return 'error_happened'
            if 'flavor_type' not in self.node_templates[vdu_name]['properties']:
                print "ERROR: VNFD is not complete: ", vdu_name,"-properties-flavor_type is not defined in the VNFD"
                return 'error_happened'
            
            vdu_type = self.node_templates[vdu_name]['type']
            vdu_ostype = self.node_templates[vdu_name]['properties']['os_type']
            vdu_flavor = self.node_templates[vdu_name]['properties']['flavor_type']
            vdu_image = self.default_image[ vdu_ostype ]     
            if self.test_mode == True:
                cmd = self.test_cmd[vdu_name]
            else:
                cmd = self.root_login + self.transferArtifacts(vdu_name) + self.transferInterfaces(vdu_name)

            vdu = {}
            vdu = {                          \
                    'type':vdu_type,         \
                    'properties':{           \
                        'name': vdu_name,    \
                        'flavor':vdu_flavor, \
                        'image':vdu_image,   \
                        'key_name':'mykey',  \
                        'user_data': cmd,    \
                        }                    \
                    }
            if vdu_name in self.HOT:
                vdu['properties']['networks'] = self.HOT['template'][vdu_name]['properties']['networks']

            self.HOT['template']['resources'][vdu_name] = vdu
        return 'succeed'           
      
    #create VDU_{vdu_id}:properties:networks

    def createVduNetworks(self, start_point_name, cp_network):
        if start_point_name not in self.HOT['template']['resources']:
            self.HOT['template']['resources'][start_point_name] = {}
        if 'properties' not in self.HOT['template']['resources'][start_point_name]:
            self.HOT['template']['resources'][start_point_name]['properties'] = {}
        start_point_networks = []
        portName = "CP_" + start_point_name[4:]
        if cp_network == 'private':
            start_point_networks.append({'port':{'get_resource': portName + "_private"} })

        elif cp_network == 'public':
            start_point_networks.append({'port':{'get_resource': portName + "_public_private"} })

        self.HOT['template']['resources'][start_point_name]['properties']['networks'] = start_point_networks
        

    #for private_port, create router_interface_private
    #for public port, create parameter, router and router interface

    def createRouterInterface(self, cp_network):
        if cp_network == 'private':
            self.createRouterInterfacePrivate()
        elif cp_network == 'public':
            self.createParamNet()
            self.createRouter()
            self.createRouterInterfacePrivate()
    
    #cp_name: endpoint name
    #cp_network: 'public' or 'private'
    
    def createPort(self, cp_name , cp_network):
        
        portName =  self.node_templates[cp_name]['requirements']['virtualbinding']
        if 'virtualLink' in self.node_templates[cp_name]['requirements']:
            virtualLink = self.node_templates[cp_name]['requirements']['virtualLink']
            CpIdPrivate = portName + '_private'
            if CpIdPrivate not in self.HOT['resources']:
                self.createCpIdPrivate(CpIdPrivate)
        else:

            CpPortName = 'CP_' + portName[4:] + "_public_ip"
            CpIdPrivatePublic = 'CP_' + portName[4:] + "_public_private"
            if CpPortName not in self.HOT['template']['resources']:
                self.createCpPublicIp(CpPortName)
            if(CpIdPrivatePublic not in self.HOT['template']['resources']):
                self.createCpIdPrivate(CpIdPrivatePublic)

    def transferCP(self):
        for cp_name in self.node_templates:
            if 'type' not in self.node_templates[cp_name]:
                continue
            if "tosca.nodes.nfv.CP" not in self.node_templates[cp_name]['type']:
                continue
            if 'virtualLink' in self.node_templates[cp_name]['requirements']:#private_network
                cp_network = 'private'
            else : cp_network = 'public'
 
            start_point_name = self.node_templates[cp_name]['requirements']['virtualbinding']
            self.createVduNetworks(start_point_name, cp_network)
            self.createRouterInterface(cp_network) 
            self.createPort(cp_name, cp_network) 
     

    def transferResources(self):
        self.HOT['template']['resources'] = {}
        self.transferVdu()
        self.transferCP()
        self.transferInternalVL()


    def transferArtifacts(self,key):
        if 'artifacts' not in self.node_templates[key]:
            print "interfaces not in TOSCA[" +tosca_key + " ]"
            return None
        pack_type = self.node_templates[key]['artifacts']['pack_type']
        root_dir = self.node_templates[key]['artifacts']['root_dir']
        file_addr = self.node_templates[key]['artifacts']['get_file']['addr']
        ftp_user = self.node_templates[key]['artifacts']['get_file']['user']
        ftp_password = self.node_templates[key]['artifacts']['get_file']['password']

        if "centOS" in self.HOT['resources'][key]['properties']['image']:
            cmd = self.rootLogIn['centOS']
            cmd = cmd + "yum -y install curl\n"
        else:
            cmd = self.rootLogIn['ubuntu']
            cmd = cmd + "apt-get install curl\n"
        ftp_cmd = "curl -u " + ftp_user + ':' + ftp_password + ' -o ' + self.root_dir + ' ' + file_addr + '\n'
        cd_root_dir = "cd " + self.root_dir + '\n'
        if pack_type == 'gzip':
            unzip = "tar -zxvf " + self.root_dir + '\n'
        elif pack_type == 'tar':
            unzip = "tar -xf " + self.root_dir + '\n'
        cmd = cmd + ftp_cmd + cd_root_dir + unzip
        return cmd

    def transferInterfaces(self,tosca_key):
        if 'interfaces' not in self.node_templates[tosca_key]:
            print "interfaces not in TOSCA[" +tosca_key + " ]"
            return None
        interfaceList = self.node_templates[tosca_key]['interfaces']['customized']
        if interfaceList:
            for interface in interfaceList:
                interfaceID = interface['interface_id']
                interfaceFormat = interface['format']
                scriptPath = interface['script_path']
                cmd = "cd " + scriptPath + '\n'
                cmd  = cmd + interfaceFormat + '\n'
        return cmd



    def createRouterInterfacePrivate(self):
        
        if 'router_interface_private'  in self.HOT['template']['resources']:
            return
        self.HOT['template']['resources']['router_interface_private'] = {  \
                'type': "OS::Neutron::RouterInterface", \
                'properties':{ \
                    'router':{'get_resource':'router'},\
                    'subnet':{'get_resource':'internal_VL_private'}\
                    }\
                }

    def createCpPublicIp(self,vnfcNodeId):
        port_ip = vnfcNodeId
        resource = vnfcNodeId + "_public_private"
        self.HOT['template']['resources'][port_ip] = {\
                'type':"OS::Neutron::FloatingIP", \
                'properties':{ \
                    'floating_network':{'get_param':'public_net'}, \
                    'port_id':{'get_resource':resource}\
                    }\
                }

    def createCpIdPrivate(self,CpId):
        key = CpId
        temp = {}
        temp['properties'] = {}
        temp['properties']['fixed_ips'] = []
        temp['type'] = "OS::Neutron::Port"
        temp['properties']['name'] = key
        temp['properties']['network'] = {'get_resource':'internal_Net_private'}
        temp['properties']['fixed_ips'].append( {'subnet': {'get_resource':'internal_VL_private'}} )
        self.HOT['template']['resources'][key] = temp

     def createRouter(self):
        self.HOT['template']['resources']['router'] = {}
        self.HOT['template']['resources']['router']['properties'] = {}
        self.HOT['template']['resources']['router']['type'] = "OS::Neutron::Router"
        self.HOT['template']['resources']['router']['properties']['name'] = "vnfNodeId_router"
        self.HOT['template']['resources']['router']['properties']['external_gateway_info'] = {}
        self.HOT['template']['resources']['router']['properties']['external_gateway_info']['network'] =  {'get_param':'public_net'}
                  
    def createParamNet(self):
        if 'parameters' not in self.HOT:
            self.HOT['template']['parameters'] = {}
            self.HOT['template']['parameters']['public_net'] = {}
            self.HOT['template']['parameters']['public_net']['type'] = "string"
            self.HOT['template']['parameters']['public_net']['default'] = "ab771c81-68b2-4274-9a68-672f7b08e53d"




    def transferInternalVL(self):
        self.HOT['template']['resources']['internal_Net_private'] = { \
                'type': "OS::Neutron::Net",\
                'properties':{'name':'internal_Net_private'}\
                }
        dns_nameservers = []
        allocation_pools = []

        dns_nameservers.append("8.8.8.8")
        allocation_pools.append( {'start':"10.0.0.100",'end':"10.0.0.120"})

        self.HOT['template']['resources']['internal_VL_private'] = { \
                'type': "OS::Neutron::Subnet",\
                'properties': {\
                    'allocation_pools': allocation_pools,\
                    'dns_nameservers': dns_nameservers,\
                    'name':'internal_VL_private',\
                    'network_id':{'get_resource':"internal_Net_private"},\
                    'cidr':"10.0.0.0/24",\
                    'ip_version':'4'\
                    }\
                }


    def toscaToJsonFile(self,stack_name, tosca_file_name, hot_file_name):
    
        self.yamlToDict(tosca_file_name)
        self.createStackName(stack_name)
        self.transferVersion()
        self.transferDescription()
        self.transferResources()
        json.dump(di,open(hot_file_name, 'w+'))

    def toscaToJson(self, stack_name, tosca_file_name):
        self.yamlToDict(tosca_file_name)
        self.createStackName(stack_name)
        self.createVersion()
        self.transferDescription()
        self.transferResources()
        return json.dumps(self.HOT)

if __name__== '__main__':
  
    tosca_file_name = "WEB-FTP-NODE-vnfd.yaml"
    hot_file_name = "test.json"
    stack_name = "teststack_large"
    tosca_to_hot = toscaToHOT()
    print tosca_to_hot.toscaToJson(stack_name, tosca_file_name)
