import os
import json
import uuid
import urllib2
import re
import yaml
import copy

true = 'True'
false = 'False'
null = 'null'
none = 'none'
NULL = 'null'

class stackinfo:
	def __init__(self):
		self.stackinfo = {}
		self.NovaUrl = 'http://10.10.26.179:8774/v2.1/8cee947f1a244124b58e1425c0b8e3c5/servers/detail'
		self.HeatUrl = 'http://10.10.26.179:8004/v1/8cee947f1a244124b58e1425c0b8e3c5/stacks/'
		self.KeystoneUrl = 'http://10.10.26.179:35357/v2.0/tokens'

	def getStackInfo(self,tenant_name,password,stack_name):
		return self.__getStackOutputs(tenant_name,password,stack_name)


        def __getTokenId(self, tenant_name, password):
        	ret = {}
        	body = {'auth' : {"tenantName" : tenant_name, 'passwordCredentials' : {'username':tenant_name, 'password': password}}}
       		body_urlencode = json.JSONEncoder().encode(body)
        	http_req = urllib2.Request(self.KeystoneUrl, body_urlencode)
        	http_req.add_header('Content-type', 'application/json')
        	try:
            		r_data = eval(urllib2.urlopen(http_req).read())
            		token_id = r_data['access']['token']['id']
            		tenant_id = r_data['access']['token']['tenant']['id']
            		ret['token_id'] = token_id
            		ret['tenant_id'] = tenant_id
            		return ret
        	except urllib2.URLError as e:
            		if hasattr(e, 'code'):
                		print 'get tenant_id error! Error code : ', e.code
            		elif hasattr(e, 'reason'):
                		print 'Reason : ', e.reason
            		return None

	def __ProcessIP(self,addr_dict):
		ips = {}
		for network in addr_dict.keys() :
			if len(addr_dict[network]) != 1 :
				for addr in addr_dict[network] :
					if addr['OS-EXT-IPS:type'] == 'fixed':
                                		ips['private'] = {
                                        		'network' : 'private',
                                        		'MAC' : addr['OS-EXT-IPS-MAC:mac_addr'],
                                        		'IP' : addr['addr'],
                                        		'version' : addr['version']
						}
					else:
						ips['provider'] = {
							'network' : 'provider',
                                                        'MAC' : addr['OS-EXT-IPS-MAC:mac_addr'],
                                                        'IP' : addr['addr'],
                                                        'version' : addr['version']
						}
			else:
				ips['private'] = {
					'network' : 'private',
					'MAC' : addr_dict[network][0]['OS-EXT-IPS-MAC:mac_addr'],
					'IP' : addr_dict[network][0]['addr'],
					'version' : addr_dict[network][0]['version']			
				}
		return ips	
			
	def __getServersIP(self,info):
		servers = {}
		url = self.NovaUrl
        	http_req = urllib2.Request(url)
        	http_req.add_header('X-Auth-Token', info['token_id'])
		http_req.add_header('Content-type', 'application/json')
		try:
			r_data = eval(urllib2.urlopen(http_req).read())
			r_data = r_data['servers']
			for  k in r_data:
				if k['name'].find('st-') == 0 :
					match = re.match(r'st-(.*?)-(.*?)-.*-(.*)',k['name'])
					serverName = match.group(2) + '-' + match.group(3)	
					server = {}
					server['hostId'] = k['hostId']
					server['Id'] = k['id']
					server['State'] = k['OS-EXT-STS:vm_state']
					server['LaunchTime'] = k['OS-SRV-USG:launched_at']
					server['IP'] = self.__ProcessIP(k['addresses'])
					servers[serverName] = server
			return servers
		except urllib2.URLError as e:
            		if hasattr(e, 'code'):
                		print 'get ip error! Error code : ', e.code
            		elif hasattr(e, 'reason'):
                		print 'Reason : ', e.reason
			return None
		

	def __initASGs(self,outputs_list):
		asg_list = []
		for i in outputs_list:
			if ( i['output_key'].find('_refs') != -1) and (i['output_value'] != null) :
				key = i['output_key'][:-5]
				self.stackinfo['outputs'][key + 'ASG'] = {}
				asg_list.append(key)
		return asg_list
			
		
		
    	def __getStackOutputs(self,tenant_name,password,stack_name):
		self.stackinfo['outputs']={}
        	info = self.__getTokenId(tenant_name , password)
        	if(info == None):
            		print 'Error : Autentication failure'
            		return
		servers = self.__getServersIP(info)
		if servers == none :
			print 'Error : Get servers information error'
			return
		url = self.HeatUrl + stack_name
        	http_req = urllib2.Request(url)
        	http_req.add_header('X-Auth-Token', info['token_id'])
		http_req.add_header('Content-type', 'application/json')
        	try:
            		r_data = eval( urllib2.urlopen(http_req).read() )
            		outputs_list = r_data['stack']['outputs']
			asg_list = self.__initASGs(outputs_list)
            		for item in outputs_list :
				if not (item['output_value'] == null ):
					if ( item['output_key'].find('_refs') != -1) :
						key = item['output_key'][:-5]
						output_servers = {}
						for i in  item['output_value'].keys():
							for server in servers.keys() :
								if server.find(i) != -1 :
									output_servers[server] = servers[server]	
						self.stackinfo['outputs'][key + 'ASG']['servers'] = output_servers
					else:
						for asg in asg_list :
							if item['output_key'].find(asg) != -1 :
								self.stackinfo['outputs'][asg + 'ASG'][item['output_key']] = item['output_value']
								break
			tmp = yaml.dump(self.stackinfo['outputs'])
			return tmp	
        	except urllib2.URLError as e:
            		if hasattr(e, 'code'):
                		print 'get outputs error! Error code : ', e.code
            		elif hasattr(e, 'reason'):
                		print 'Reason : ', e.reason
           		return None

'''
if __name__  == '__main__' :
	stackinfo = stackinfo()
	result = stackinfo.getStackOutputs('demo','demo','stack6')
'''
