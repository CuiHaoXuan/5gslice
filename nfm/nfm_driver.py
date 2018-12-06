from flask import Flask
from flask import render_template
from flask import request

import json
import commands
import datetime
import threading
import os
import sys
import urllib2
from api.api_gateway import api_gateway

app = Flask(__name__)

API = api_gateway()
  
  
    
class nfm_driver:

    OpJobs = {}
    interfaces = {}

    def addInterface(self, slice_id, vnf, vnfc, interface):
        if slice_id not in self.interfaces:
            self.interfaces[slice_id] = {}
        if vnf not in self.interfaces[slice_id]:
            self.interfaces[slice_id][vnf] = {}
        if vnfc not in self.interfaces[slice_id][vnf]:
            self.interfaces[slice_id][vnf][vnfc] = {}
        interface_scope = interface[ 'scope' ]
        interface_id = interface[ 'interface_id' ]
        interface_format = interface[ 'format' ]
        interface_path = interface[ 'path' ]
        if interface_scope not in self.interfaces[slice_id][vnf][vnfc]:
            self.interfaces[slice_id][vnf][vnfc][interface_scope] = {}
        self.interfaces[slice_id][vnf][vnfc][interface_scope][interface_id] = { \
                'interface_format': interface_format, \
                'interface_path': interface_path \
                }

    def addOpJob(self,slice_id, task_id, op_job_id ):
        if slice_id not in OpJobs:
            OpJobs[slice_id] = {}
        if task_id not in ObJobs[slice_id]:
            OpJobs[slice_id][task_id] = {}
        if op_job_id not in ObJobs[slice_id][task_id]:
            OpJobs[slice_id][task_id][op_job_id] = "excuting"

    def getOpJob_id(self):
        now = datetime.datetime.now().microsecond
        return str(now)
   
    def deployment(self, sender, response_interface, task_id, opjob_id, interface_list):
     
        response = {}
        errors = []
        result = 'succeed'
        for slice_id in interface_list:
            for vnf in interface_list[slice_id]:
                for vnfc in interface_list[slice_id][vnf]:
                    for interface_id in interface_list[slice_id][vnf][vnfc]:
                        formatt = interface_list[slice_id][vnf][vnfc][interface_id]['interface_format']
                        path = interface_list[slice_id][vnf][vnfc][interface_id]['interface_path']
                     
                        vnfc_flag = str(vnf) + '_' + str(vnfc)
                        cmd = "ansible " + vnfc_flag + " -m command " +" -a "+ r'"' +  formatt + ' chdir=' + path + r'"'
                        print "debug cmd is : ", cmd
                        (status, output) = commands.getstatusoutput(cmd)
                        if status != 0:
                            result = 'failed'
                            errors.append({'slice_id':slice_id, 'vnf_id':vnf, 'vnfc_id':vnfc, 'interface_id':interface_id, 'error_info':output})
                        print "status is ",status, "output is ",output
        response = { \
                'task_id':task_id, \
                'opJob_id':opjob_id, \
                'result':result \
                }
        if result == 'failed':
            response['errors'] = errors
        #url_info = {'module':sender, 'interface':response_interface}
        #url = API.getUrl(url_info)
        #print "DEBUG: url is : ", url
        #data_urlencode = json.JSONEncoder().encode(response)
        #request = urllib2.Request(url, data_urlencode)
        #urllib2.urlopen(request) 


    def execCommand(self, response_interface,  opjob_id, interface):
        errors = []
        result = 'succeed'
        response = {}
        interface_list = []
        detail = []
        detail_item = {}
        print "DEBUG : exec a command : interface is ", interface
        
        slice_id = interface['slice_id']
        task_id = interface['task_id']
        vnf_node_id = interface['vnf_node_id']
        vnfc_node_id = interface['vnfc_node_id']
        scope = interface['scope']
        sender = interface['sender']

        if 'interface_id' not in interface:
	    print "DEBUG : interface_id not in interface"
            for int_id in self.interfaces[slice_id][vnf_node_id][vnfc_node_id][scope]:
		print "DEBUG : interface_list.append(init_id)"
		interface_list.append(int_id)
        else:
            interface_list.append( interface['interface_id'] )

        for interface_id in interface_list:
            formatt = self.interfaces[slice_id][vnf_node_id][vnfc_node_id][scope][interface_id]['interface_format']
            path = self.interfaces[slice_id][vnf_node_id][vnfc_node_id][scope][interface_id]['interface_path']
            vnfc_flag = str(vnf_node_id) + '_' + str(vnfc_node_id)
            cmd = "ansible " + vnfc_flag + " -m command " +" -a "+ r'"' +  formatt + ' chdir=' + path + r'"'
            print "##########debug##########"
            print cmd
            (status, output) = commands.getstatusoutput(cmd)
            if status != 0:
                result = 'failed'
                errors.append({'slice_id':task_id, 'vnf_id':vnf_node_id, 'vnfc_id':vnfc_node_id, 'interface_id':interface_id, 'error_info':output  })
            print "status is ",status, "output is ",output
        detail_item = { \
            'task_id':task_id, \
            'opJob_id':opjob_id, \
            'result':result \
            }
        if result == 'failed':
            detail_item['errors'] = errors
        detail.append(detail_item)
        response = {"opJob_id":opjob_id, "detail":detail}
        url_info = {'module':sender, 'interface':response_interface}
        url = API.getUrl(url_info)
        print "url is ", url
        
        #data_urlencode = json.JSONEncoder().encode(response)
        #request = urllib2.Request(url, data_urlencode)
	#urllib2.urlopen(request)
        return



    def execCommands(self, sender, response_interface, task_id, opjob_id, interface_list):
        errors = []
        result = 'succeed'
        response = {}
	detail = []
        for slice_id in interface_list:
            for vnf in interface_list[slice_id]:
                for vnfc in interface_list[slice_id][vnf]:
                    
                    sorted( interface_list[slice_id][vnf][vnfc].iteritems(), key = lambda asd:asd[0], reverse = False) 
                    for interface_id in interface_list[slice_id][vnf][vnfc]:
                        
                        print "DEBUG : exec a command : interface_id is ", interface_id
                        scope = interface_list[slice_id][vnf][vnfc][interface_id]['scope']
                        formatt = self.interfaces[slice_id][vnf][vnfc][scope][interface_id]['interface_format']
                        path = self.interfaces[slice_id][vnf][vnfc][scope][interface_id]['interface_path']
                        vnfc_flag = str(vnf) + '_' + str(vnfc)
                        cmd = "ansible " + vnfc_flag + " -m command " +" -a "+ r'"' +  formatt + ' chdir=' + path + r'"'
                        print '##########debug########'
                        print 'cmd is : ', cmd
                        (status, output) = commands.getstatusoutput(cmd)
                        if status != 0:
                            result = 'failed'
                            errors.append({'slice_id':task_id, 'vnf_id':vnf, 'vnfc_id':vnfc, 'interface_id':interface_id, 'error_info':output  })
                        print "status is ",status, "output is ",output
        detail_item = { \
                'task_id':task_id, \
                'opJob_id':opjob_id, \
                'result':result \
                }
        if result == 'failed':
            detail_item['errors'] = errors
        detail.append(detail_item)
        response = {"opJob_id":opjob_id, "detail":detail}
        url_info = {'module':sender, 'interface':response_interface}
        url = API.getUrl(url_info)
        print "url is ", url
        #url = "http://127.0.0.1:5000/nfm/v1/nfm_driver/file_deployment/response/json"
        
        #data_urlencode = json.JSONEncoder().encode(response)
        #request = urllib2.Request(url, data_urlencode)
	#urllib2.urlopen(request)
        return

class SSH:
    record = {}

    def __init__(self, path):
        self.ssh_file_path = path
        self.ssh_file = open( self.ssh_file_path, 'a+' )

    def readSSHConfig(self):
        self.ssh_file.seek(0,0)
        lines = self.ssh_file.readlines()
        #print "self.record is : ", lines
        for line in lines:
            new_line = line.split(' ')
            #print new_line
            first_word = new_line[0]
            if first_word == 'Host':
                host_name = new_line[1][:-1]
                self.record[host_name] = host_name
        print "self.record is : ", self.record

    def writeHost(self, host_name, user, HostName = None, proxy = None, port = 22, IdentityFile = "~/.ssh/id_rsa"):
        if host_name in self.record:
            return
        self.ssh_file.write("Host " + host_name + '\n')
        if HostName != None:
            self.ssh_file.write("\tHostName " + HostName + '\n')
        self.ssh_file.write("\tUser " + user + '\n')
        self.ssh_file.write("\tPort " + str(port) + '\n')
        self.ssh_file.write("\tIdentityFile " + IdentityFile + '\n')
        if(proxy != None):
            self.ssh_file.write("\tProxyCommand ssh " + proxy +" -W %h:%p \n")
        self.record[host_name] = host_name
    
    def __del__(self):
        self.ssh_file.close()
'''
record = {
    vnf_id = {
        vnfc_id = {
         .....
         }
        }
    }
'''

class AnsibleConfig():
    record = {}

    def __init__(self, path):
	'''
	this is the ansible_hosts
	'''
        self.ansible_file_path = path
        self.ansible_hosts_file = open(self.ansible_file_path, 'a+')

    def readAnsibleConfig(self):
	'''
	read the ansible_hosts
	and each vnf is a group which has a group name
	'''
        lines = self.ansible_hosts_file.readlines()
        for line in lines:
	    #delete the \n 
            new_line = line[:-1].split(' ')
            if len(new_line) == 1 : #group name
                group_name = new_line[0]       
                self.record[group_name] = {}
            else :
                host_item = {}
                vnfc_name = new_line[0]
                for item in new_line[1:]:
                    print item
                    name = item.split('=')[0]
                    value = item.split('=')[1]
                    host_item[name] = value
                self.record[group_name][vnfc_name] = host_item
                
    def writeHost(self, vnf, vnfc, ansible_ssh_host, ansible_ssh_pass, ansible_ssh_user = 'root'):
        self.ansible_hosts_file.seek(0,0)
        if (vnf in self.record) and (vnfc in self.record[vnf]):
            print self.record[vnf][vnfc]
            if (ansible_ssh_host == self.record[vnf][vnfc]['ansible_ssh_host']) \
                    and (ansible_ssh_user == self.record[vnf][vnfc]['ansible_ssh_user']) \
                    and (ansible_ssh_pass == self.record[vnf][vnfc]['ansible_ssh_pass']):
                print "write a vnfc to /root/.ssh/config failed, there is a repetitive record: " + str(self.record[vnf][vnfc])
                return
        for eachline in self.ansible_hosts_file:
            if eachline[:-1] != vnf:
                #print "each_line and vnf", eachline[:-1], ' ', vnf
                continue
            self.ansible_hosts_file.write(vnfc + " ansible_ssh_host=" + ansible_ssh_host + " ansible_ssh_user=" + ansible_ssh_user + " ansible_ssh_pass=" + ansible_ssh_pass + '\n')
            self.ansible_hosts_file.flush()

       
    def writeVnf(self, vnf):
	'''
	???don't need to add the []
	'''
        if vnf in self.record:
            return
        self.record[vnf] = {}
        self.ansible_hosts_file.write(vnf + '\n')
        self.ansible_hosts_file.flush()
         
        

    def __del__(self):
        self.ansible_hosts_file.close()


@app.route('/nfm_driver/ansible/v1/interface/deployment/json', methods = ['POST'])
def nfmDriverInterfaceDeployment():
    ssh = SSH("/root/.ssh/config")
    ansible = AnsibleConfig("/etc/ansible/hosts")
    ssh.readSSHConfig()
    ansible.readAnsibleConfig()
    driver = nfm_driver() 
    cmd_list = []
    data = eval( request.get_data() ) 
    deploy_list = {}

    sender = data['sender']
    response_interface = 'file_deployment_response'
    for deploy_command in data['deployment']:
        slice_id = deploy_command['slice_id']
        task_id = deploy_command['task_id']
        '''
        get vnf_node_id and create a list in /etc/ansible/hosts, then get vnfc_node_id, vnf_node_mgmt_ip, passwd, username, record them to the list
        '''
        vnf_node_list = deploy_command['vnf_node_list']
        '''
        178  to  203
        traversal the vnf_node_list, for every vnf_node, check if it did not exist in ansible.record,
        get agent information and write agent info to /etc/ansible/hosts and /root/.ssh/config
        '''
        for vnf_node in vnf_node_list:
            vnf_node_id = vnf_node['vnf_node_id']
            if vnf_node_id not in ansible.record:
                ansible.writeVnf(vnf_node_id)
            else:
                print "debug: vnf_node is already in the record : ",vnf_node_id
            vnfc_node_list = vnf_node['vnfc_node_list']

            agent_public_address = vnf_node['config_agent_info']['agent_public_address']
            agent_mgmt_address = vnf_node['config_agent_info']['agent_mgmt_address']
            agent_user = vnf_node['config_agent_info']['agent_username']
            agent_passwd = vnf_node['config_agent_info']['agent_password']
            if agent_user == 'ubuntu':
                agent_user = 'hss'
                agent_passwd = '123'
            agent_id = "agent_" + agent_public_address
            print "record host_info : ", agent_id, "into /root/.ssh/config"
            ansible.writeHost(vnf_node_id, agent_id, agent_public_address, agent_passwd, agent_user)
            copyRsa = "ansible "+ agent_id + " -m command -a " + r'"' + "ssh-copy-id -i /root/.ssh/id_rsa.pub " + agent_user + "@" + agent_public_address + r'"'
            #copyRsa = "ansible "+ agent_id + " -m command -a " + r'"' + "ls " + r'"'
            (status, output) = commands.getstatusoutput(copyRsa)
            ssh.writeHost(agent_id, agent_user, agent_public_address)
            print vnfc_node_list
            '''
            171 to 188
            traversal the vnfc_node_list, get vnfc infomation, write vnfc info into /etc/ansible/hosts and /root/.ssh/config
            '''
            for vnfc_node in vnfc_node_list:
                '''
                create host record and write to /etc/ansible/hosts
                '''
                vnfc_node_id = vnfc_node['vnfc_node_id']
                       
                mgmt_ip = vnfc_node['mgmt_address']
                vnfc_node_user = vnfc_node['vnfc_node_user']
                vnfc_node_passwd = vnfc_node['vnfc_node_passwd']
                    
		'''
		eg: vnfc_flag = SPGW-NODE_SPGW-NODE
		'''
                vnfc_flag = str(vnf_node_id) + '_' + str(vnfc_node_id)
                host_info = vnfc_flag + ' ' + "ansible_ssh_host=" + mgmt_ip + ' ' + 'ansible_ssh_user=' + vnfc_node_user + ' ' + 'ansible_ssh_pass=' + vnfc_node_passwd
                print "record host_info : ", host_info, "into /etc/ansible/hosts"
                ansible.writeHost(vnf_node_id, vnfc_flag, mgmt_ip, vnfc_node_passwd, vnfc_node_user)
                ssh.writeHost(mgmt_ip, vnfc_node_user, mgmt_ip)
                
                interface_list = vnfc_node ['interface_list']
                deploy_list = {}
                for interface in interface_list:
                    driver.addInterface(slice_id, vnf_node_id, vnfc_node_id, interface )                    
                    scope = interface['scope']
                    formatt = interface['format']
                    path = interface['path']
                    interface_id = interface ['interface_id']
                    if scope == 'deployment':
                        if slice_id not in deploy_list:
                            deploy_list[slice_id] = {}
                        if vnf_node_id not in deploy_list[slice_id]:
                            deploy_list[slice_id][vnf_node_id] = {}
                        if vnfc_node_id not in deploy_list[slice_id][vnf_node_id]:
                            deploy_list[slice_id][vnf_node_id][vnfc_node_id] = {}
                            deploy_list[slice_id][vnf_node_id][vnfc_node_id][interface_id] = {'interface_format':formatt, 'interface_path':path} 

        print deploy_list
        opjob_id = driver.getOpJob_id()
        t = threading.Thread(target=driver.deployment, args= [sender, response_interface, task_id, opjob_id, deploy_list,])
	t.start()
        response = {'task_id':task_id, 'opJob_id': opjob_id}
    return json.dumps(response), 202, {'Content-Type' : 'application/json'}

@app.route('/nfm_driver/ansible/v1/interface/invoking/json', methods = ['POST'])
def nfmDriverSingleInterfaceInvoking():
    driver = nfm_driver()
    data = eval( request.get_data() )
    print "#######DEBUG####: ",data
    response_interface = 'interface_invoking_response'
    opjob_id = driver.getOpJob_id()
    t = threading.Thread(target=driver.execCommand, args= [response_interface,opjob_id, data,])
    t.start()
    response = {'task_id':data['task_id'], 'opJob_id': opjob_id}
    return json.dumps(response), 202, {'Content-Type' : 'application/json'}


@app.route('/nfm_driver/ansible/v1/interfaces/invoking/json', methods = ['POST'])
def nfmDriverInterfaceInvoking():
    driver = nfm_driver() 
    data = eval( request.get_data() ) 
    deploy_list = {}
    
    sender = data['sender']
    response_interface = 'interface_invoking_response'
 
    print data
    for invoking_command in data['invoking_commands']:
        slice_id = invoking_command['slice_id']
        task_id = invoking_command['task_id']
        vnf_node_list = invoking_command['vnf_node_list']
        for vnf_node in vnf_node_list:
            vnf_node_id = vnf_node['vnf_node_id']
            vnfc_node_list = vnf_node['vnfc_node_list']
            for vnfc_node in vnfc_node_list:
                '''
                create host record and write to /etc/ansible/hosts
                '''
                vnfc_node_id = vnfc_node['vnfc_node_id']
                vnfc_flag = vnf_node_id + "_" + vnfc_node_id
                interface_list = vnfc_node ['interface_list']

                for interface in interface_list:
                    interface_id = interface['interface_id']
                    scope = interface['scope']
                    if slice_id not in deploy_list:
                        deploy_list[slice_id] = {}
                    if vnf_node_id not in deploy_list[slice_id]:
                        deploy_list[slice_id][vnf_node_id] = {}
                    if vnfc_node_id not in deploy_list[slice_id][vnf_node_id]:
                        deploy_list[slice_id][vnf_node_id][vnfc_node_id] = {}
                    deploy_list[slice_id][vnf_node_id][vnfc_node_id][interface_id] = {'scope':scope} 

        opjob_id = driver.getOpJob_id()
        t = threading.Thread(target=driver.execCommands, args= [sender, response_interface,task_id, opjob_id, deploy_list,])
	t.start()
        response = {'task_id':task_id, 'opJob_id': opjob_id}
    return json.dumps(response), 202, {'Content-Type' : 'application/json'}





if __name__ == '__main__':
    if os.geteuid():
        args = [sys.executable] + sys.argv
        os.execlp('su', 'su', '-c',' '.join(args))
    app.run(host = '0.0.0.0', port = 8888)
