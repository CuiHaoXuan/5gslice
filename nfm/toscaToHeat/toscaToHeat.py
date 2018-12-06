#usr/bin/python #coding=utf-8

import yaml
import os
import logging
import json
from collections import OrderedDict


global TOSCA
global HOT
global rootLogIn
# tempTOSCA stores the whole vnfd file
global tempTOSCA 
tempTOSCA = {}
TOSCA = {}
HOT = {}
rootLogIn = {'ubuntu': "#!/bin/sh\ncp -f /home/ubuntu/.ssh/authorized_keys /root/.ssh/\npasswd root<<EOF\npassword\npassword\nEOF\n"}

# use this cmd to deploy ftp 
ftp_cmd = "#!/bin/sh\ncp -f /home/ubuntu/.ssh/authorized_keys /root/.ssh/\npasswd root<<EOF\npassword\npassword\nEOF\napt-get install -y vsftpd\n service vsftpd restart\nmkdir /home/uftp\nuseradd -d /home/uftp -s /bin/bash uftp\n passwd uftp<<EOF\nuftp\nuftp\nEOF\nsed -i '$a write_enable=YES' /etc/vsftpd.conf\nsed -i '$a userlist_deny=NO' /etc/vsftpd.conf\n sed -i '$a userlist_enable=YES' /etc/vsftpd.conf\nsed -i '$a userlist_file=/etc/allowed_users' /etc/vsftpd.conf\nsed -i '$a seccomp_sandbox=NO' /etc/vsftpd.conf\ncd /etc/\necho \"uftp\">> allowed_users\nchmod -R 777 /home/uftp\nchown ftp:root /home/uftp\nservice vsftpd restart\n"

# use this cmd to deploy apache
apache_cmd = "#!/bin/sh\ncp -f /home/ubuntu/.ssh/authorized_keys /root/.ssh/\npasswd root<<EOF\npassword\npassword\nEOF\napt-get install -y apache2\nsed -i '$a ServerName localhost' /etc/apache2/apache2.conf\nservice apache2 restart\nsed -i 's/PermitRootLogin without-password/PermitRootLogin yes/g' /etc/ssh/sshd_config\nsed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config\nservice ssh restart\n"

defaultHeatTemplateVersion = "2016-10-14"


# put heat_template_version to hot template 
def transferVersion():
    global HOT
    global TOSCA
    HOT['heat_template_version'] = defaultHeatTemplateVersion

def transferDescription():
    if 'description' in tempTOSCA:
        HOT['description'] = tempTOSCA['description']
    if 'metadata' in tempTOSCA:
        if('id' in tempTOSCA['metadata']):
            HOT['description'] =  HOT['description'] + " ; " + "metadata:id is : " + str(tempTOSCA['metadata']['id'])
        if 'vendor' in tempTOSCA['metadata']:
            HOT['description'] =  HOT['description'] + " ; " + "metadata:vendor is : " + tempTOSCA['metadata']['vendor']
        if 'version' in tempTOSCA['metadata']:
            HOT['description'] =  HOT['description'] + " ; " + "metadata:version is : " + str(tempTOSCA['metadata']['version'])

def transferResources():
    HOT['resources'] = {}
    transferVdu()
    transferCP()
    transferInternalVL()


def transferArtifacts(key):
    if 'artifacts' not in TOSCA[key]:
        print "interfaces not in TOSCA[" +tosca_key + " ]"
        return None
    pack_type = TOSCA[key]['artifacts']['pack_type']
    root_dir = TOSCA[key]['artifacts']['root_dir']
    file_addr = TOSCA[key]['artifacts']['get_file']['addr']
    ftp_user = TOSCA[key]['artifacts']['get_file']['user']
    ftp_password = TOSCA[key]['artifacts']['get_file']['password']

    if "centOS" in HOT['resources'][key]['properties']['image']:
        cmd = rootLogIn['centOS']
        cmd = cmd + "yum -y install curl\n"
    else:
        cmd = rootLogIn['ubuntu']
        cmd = cmd + "apt-get install curl\n"
    ftp_cmd = "curl -u " + ftp_user + ':' + ftp_password + ' -o ' + root_dir + ' ' + file_addr + '\n'
    cd_root_dir = "cd " + root_dir + '\n'
    if pack_type == 'gzip':
        unzip = "tar -zxvf " + root_dir + '\n'
    elif pack_type == 'tar':
        unzip = "tar -xf " + root_dir + '\n'
    cmd = cmd + ftp_cmd + cd_root_dir + unzip
    return cmd

def transferInterfaces(tosca_key):
    if 'interfaces' not in TOSCA[tosca_key]:
        print "interfaces not in TOSCA[" +tosca_key + " ]"
        return None
    interfaceList = TOSCA[tosca_key]['interfaces']['customized']
    if interfaceList:
        for interface in interfaceList:
            interfaceID = interface['interface_id']
            interfaceFormat = interface['format']
            scriptPath = interface['script_path']
            cmd = "cd " + scriptPath + '\n'
            cmd  = cmd + interfaceFormat + '\n'
    return cmd



def transferVdu():
    global HOT
    global TOSCA
    for key in TOSCA:
        if 'type' not in TOSCA[key]:
            continue
        if 'tosca.nodes.nfv.VDU' in TOSCA[key]['type']:
            print "detected a VDU"
            temp= {}
            temp['properties'] = {}
            temp['type'] = "OS::Nova::Server"
            temp['properties']['name'] = key
            if 'ubuntu' in TOSCA[key]['properties']['os_type']:
                temp['properties']['image'] = 'ubuntu14.04'
            temp['properties']['flavor'] = TOSCA[key]['properties']['flavor_type']
            temp['properties']['key_name'] = 'mykey'
            HOT['resources'][key] = temp
            if key == 'VDU_WEB-NODE':
                HOT['resources'][key]['properties']['user_data'] = apache_cmd#transferArtifacts(key) + transferInterfaces(key)
            if key == 'VDU_FTP-NODE':
                HOT['resources'][key]['properties']['user_data'] = ftp_cmd
def createRouterInterfacePrivate():
    global HOT
    temp = {}
    temp['properties'] = {}
    temp['type'] = "OS::Neutron::RouterInterface"
    temp['properties']['router'] = {'get_resource':'router'}
    temp['properties']['subnet'] = {'get_resource':'internal_VL_private'}
    HOT['resources']['router_interface_private'] = temp

def createCpPublicIp(vnfcNodeId):
    global HOT
    key = vnfcNodeId + "_public_ip"
    resource = vnfcNodeId + "_public_private"
    temp = {}
    temp['properties'] = {}
    temp['type'] = "OS::Neutron::FloatingIP"
    temp['properties']['floating_network'] = {'get_param':'public_net'}
    temp['properties']['port_id'] = {'get_resource':resource}
    HOT['resources'][key] = temp

def createCpIdPublicPrivate(CpIdPrivatePublic):
    global HOT
    key = CpIdPrivatePublic
    temp = {}
    temp['properties'] = {}
    temp['properties']['fixed_ips'] = []
    temp['type'] = "OS::Neutron::Port"
    temp['properties']['name'] = key
    temp['properties']['network'] = {'get_resource':'internal_Net_private'}
    temp['properties']['fixed_ips'].append( {'subnet': {'get_resource':'internal_VL_private'}} )
    HOT['resources'][key] = temp

def createCpIdPrivate(CpIdPrivate):
    global HOT
    key = CpIdPrivate
    temp = {}
    temp['properties'] = {}
    temp['properties']['fixed_ips'] = []
    temp['type'] = 'OS::Neutron::Port'
    temp['properties']['name'] = key
    temp['properties']['network'] = {'get_resource':'internal_Net_private'}
    temp['properties']['fixed_ips'].append( {'subnet': {'get_resource': 'internal_VL_private'} })
    HOT['resources'][key] = temp

def createRouterInterface():
    global HOT
    temp = {}
    temp['type'] = "OS::Neutron::RouterInterface"
    temp['properties'] = {}
    temp['properties']['router_id'] = {'get_resource':'router'}
    temp['properties']['subnet_id'] = {'get_resource': 'internal_VL_private'}
    HOT['resources']['router_interface'] = temp

def createRouter():
    HOT['resources']['router'] = {}
    HOT['resources']['router']['properties'] = {}
    HOT['resources']['router']['type'] = "OS::Neutron::Router"
    HOT['resources']['router']['properties']['name'] = "vnfNodeId_router"
    HOT['resources']['router']['properties']['external_gateway_info'] = {}
    HOT['resources']['router']['properties']['external_gateway_info']['network'] =  {'get_param':'public_net'}
                  
def createParamNet():
    if 'parameters' not in HOT:
        HOT['parameters'] = {}
        HOT['parameters']['public_net'] = {}
        HOT['parameters']['public_net']['type'] = "string"
        HOT['parameters']['public_net']['default'] = "ab771c81-68b2-4274-9a68-672f7b08e53d"

def transferCP():
    global HOT
    global TOSCA

    for key in TOSCA:
        if 'type' not in TOSCA[key]:
            continue
        if "tosca.nodes.nfv.CP" in TOSCA[key]['type']:
          #  HOT['resources'][key] = {}
    #        HOT['resources'][key]['properties'] = {}
    #        HOT['resources'][key]['properties']['fixed_ips'] = []
    #        HOT['resources'][key]['type'] = "OS::Neutron::Port"
    #        CP_vnfcNodeId = TOSCA[key]['requirements']['virtualbinding']
    #        HOT['resources'][key]['properties']['name'] = CP_vnfcNodeId + "_private"
    #        HOT['resources'][key]['properties']['network'] = {'get_resource':'internal_Net_private'}
    #        temp = {'get_resource':'internal_VL_private'}
 
    #        HOT['resources'][key]['properties']['fixed_ips'].append({'subnet':temp})
            #get VDU_(vnfcNodeId) port
            virtualBindingVduId = TOSCA[key]['requirements']['virtualbinding']
            if virtualBindingVduId not in HOT['resources']:
                HOT['resources'][virtualBindingVduId] = {}
            if 'properties' not in HOT['resources'][virtualBindingVduId]:
                HOT['resources'][virtualBindingVduId]['properties'] = {}
            HOT['resources'][virtualBindingVduId]['properties']['networks'] = []
            
            if 'virtualLink' in TOSCA[key]['requirements']:
                virtualLink = TOSCA[key]['requirements']['virtualLink']
                portName = "CP_" + virtualBindingVduId[4:]
                HOT['resources'][virtualBindingVduId]['properties']['networks'].append({'port':{'get_resource': portName + "_private"} })
                if 'router_interface_private' not in HOT['resources']:
                    createRouterInterfacePrivate();
                CpIdPrivate = portName + '_private'
                if CpIdPrivate not in HOT['resources']:
                    createCpIdPrivate(CpIdPrivate)
            else:
                ##create public network
                createParamNet()
                createRouter()
                createRouterInterface()

                portName = "CP_" + virtualBindingVduId[4:]
                HOT['resources'][virtualBindingVduId]['properties']['networks'].append({'port':{'get_resource': portName + "_public_private"}})

                CpPortName = portName + "_public_ip"
                CpIdPrivatePublic = portName + "_public_private"
                if CpPortName not in HOT['resources']:
                    createCpPublicIp(portName)
                if(CpIdPrivatePublic not in HOT['resources']):
                    createCpIdPublicPrivate(CpIdPrivatePublic)




def transferInternalVL():
    global HOT
    global TOSCA

    HOT['resources']['internal_Net_private'] = {}
    HOT['resources']['internal_Net_private']['properties'] = {}
    HOT['resources']['internal_VL_private'] = {}
    HOT['resources']['internal_VL_private']['properties'] = {}
    HOT['resources']['internal_VL_private']['properties']['allocation_pools'] = []
    HOT['resources']['internal_VL_private']['properties']['dns_nameservers'] = []
    HOT['resources']['internal_Net_private']['type'] = "OS::Neutron::Net"
    HOT['resources']['internal_Net_private']['properties']['name'] = "internal_Net_private"
    HOT['resources']['internal_VL_private']['type'] = "OS::Neutron::Subnet"
    HOT['resources']['internal_VL_private']['properties']['name'] = "internal_VL_private"
    HOT['resources']['internal_VL_private']['properties']['network_id'] = {'get_resource':'internal_Net_private'}
    HOT['resources']['internal_VL_private']['properties']['cidr'] = "10.0.0.0/24"
    HOT['resources']['internal_VL_private']['properties']['dns_nameservers'].append("8.8.8.8")
    HOT['resources']['internal_VL_private']['properties']['ip_version'] = "4"
    HOT['resources']['internal_VL_private']['properties']['allocation_pools'].append( {'start':"10.0.0.100",'end':"10.0.0.120"})

def createStackName(di,stackName):
    di['stack_name'] = stackName

def toscaToJsonFile(tosca_file_name, hot_file_name):
    global HOT
    global tempTOSCA
    global TOSCA
    
    stackName = "teststack_large"
    di = {}
    tempTOSCA = yaml.load(open(tosca_file_name))
    TOSCA = tempTOSCA['topology_template']['node_templates']
    transferVersion()
    transferDescription()
    transferResources()
    di['template'] = HOT
    di['stack_name'] = stackName
    json.dump(di,open(hot_file_name, 'w+'))
    #yaml.dump(di, open(hot_file_name, 'w+'), default_flow_style = False)

def toscaToJson(tosca_file_name):
    global HOT
    global tempTOSCA
    global TOSCA
    stackName = "teststack_large"
    di = {}
    tempTOSCA = yaml.load(open(tosca_file_name))
    TOSCA = tempTOSCA['topology_template']['node_templates']
    transferVersion()
    transferDescription()
    transferResources()
    di['template'] = HOT
    di['stack_name'] = stackName
    return json.dumps(di)

if __name__== '__main__':
  
    tosca_file_name = "WEB-FTP-NODE-vnfd.yaml"
    hot_file_name = "test.json"
    print toscaToJsonFile(tosca_file_name, hot_file_name)
