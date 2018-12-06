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

class stackinformation:
    def __init__(self):
        self.stackinfo = {}
        self.NovaUrl = 'http://192.168.0.21:8774/v2.1/61d4169122f64c09a9eb9dd6154c6a6d/servers/detail'
        self.HeatUrl = 'http://192.168.0.21:8004/v1/61d4169122f64c09a9eb9dd6154c6a6d/stacks/'
        self.KeystoneUrl = 'http://192.168.0.21:35357/v2.0/tokens'

    def getStackInfo(self, tenant_name, password, stack_name):
        return self.__getStackOutputs(tenant_name, password, stack_name)

    def __getTokenId(self, tenant_name, password):
        ret = {}
        body = {'auth': {"tenantName": tenant_name, 'passwordCredentials': {'username': tenant_name, 'password': password}}}
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
                        ips['privateIp'] = {
                            'network': 'private',
                            'MAC': addr['OS-EXT-IPS-MAC:mac_addr'],
                            'IP': addr['addr'],
                            'version': addr['version']
                        }
                    else:
                        ips['publicIp'] = {
                            'network': 'provider',
                            'MAC': addr['OS-EXT-IPS-MAC:mac_addr'],
                            'IP': addr['addr'],
                            'version': addr['version']
                        }
            else:
                ips['privateIp'] = {
                    'network' : 'private',
                    'MAC' : addr_dict[network][0]['OS-EXT-IPS-MAC:mac_addr'],
                    'IP' : addr_dict[network][0]['addr'],
                    'version' : addr_dict[network][0]['version']
                }
        return ips

    def __getServersIP(self,info,stack_name):
        servers = {}
        url = self.NovaUrl
        http_req = urllib2.Request(url)
        http_req.add_header('X-Auth-Token', info['token_id'])
        http_req.add_header('Content-type', 'application/json')
        try:
            r_data = eval(urllib2.urlopen(http_req).read())
            r_data = r_data['servers']
            for k in r_data:
                flag = 0
                for address in k['addresses'].keys():
                    if address.find(stack_name) != -1:
                        flag = 1
                if flag:
                    serverName = k['name']
                    if serverName in servers.keys():
                        servers[serverName][k['id']] = {
                            'name': serverName,
                            'State': k['OS-EXT-STS:vm_state'],
                            'LaunchTime': k['OS-SRV-USG:launched_at'],
                            'IP': self.__ProcessIP(k['addresses'])
                        }
                    else:
                        servers[serverName] = {
                            k['id']: {
                                'name': serverName,
                                'State': k['OS-EXT-STS:vm_state'],
                                'LaunchTime': k['OS-SRV-USG:launched_at'],
                                'IP': self.__ProcessIP(k['addresses'])
                            }
                        }
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
                # before refs is vnfc_nid
                key = i['output_key'][:-5]
                self.stackinfo['outputs'][key + '_ASG'] = {}
                asg_list.append(key)
        return asg_list

    def __getStackOutputs(self,tenant_name,password,stack_name):
        self.stackinfo['outputs']={}
        info = self.__getTokenId(tenant_name, password)
        if info == None:
            print 'Error : Autentication failure'
            return
        servers = self.__getServersIP(info,stack_name)
        if servers == none :
            print 'Error : Get servers information error'
            return
        url = self.HeatUrl + stack_name
        http_req = urllib2.Request(url)
        http_req.add_header('X-Auth-Token', info['token_id'])
        http_req.add_header('Content-type', 'application/json')
        try:
            r_data = eval(urllib2.urlopen(http_req).read())
            outputs_list = r_data['stack']['outputs']
            self.stackinfo['outputs']['stack_status']= r_data['stack']['stack_status']
            if self.stackinfo['outputs']['stack_status'] == 'CREATE_IN_PROGRESS':
                return self.stackinfo['outputs']
            asg_list = self.__initASGs(outputs_list)
            for item in outputs_list:
                if item['output_key'].find('_refs') != -1:
                    key = item['output_key'][:-5]
                    self.stackinfo['outputs'][key + '_ASG']['servers'] = servers[key]
                else:
                    flag = 0
                    for asg in asg_list:
                        if item['output_key'].find(asg) != -1 and item['output_key'].find('IPs') == -1:
                            self.stackinfo['outputs'][asg + '_ASG'][item['output_key']] = item['output_value']
                            flag = 1
                            break
                    if flag == 0:
                        for k, v in item['output_value'].items():
                            self.stackinfo['outputs'][item['output_key']] = {
                                'privateIp' : v[0],
                                'publicIp' :  v[1]
                            }
                            break
            return self.stackinfo['outputs']
        except urllib2.URLError as e:
            if hasattr(e, 'code'):
                print 'get outputs error! Error code : ', e.code
            elif hasattr(e, 'reason'):
                print 'Reason : ', e.reason
            return None


if __name__  == '__main__' :
    stackinfo = stackinformation()
    result = stackinfo.getStackInfo('demo', 'demo', 'MME-HSS-VNF01')
    print result
