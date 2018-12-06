import re
import copy
import types
if __name__ == '__main__' :
    str1 = 'CP_{{SPGW-NODE}}_{{SPGW-PORTAL}}_privateIp'
    str2 = 'CP_mgmt_{{SPGW-NODE}}_privateIp'
    str3 = 'CP_{{SPGW-NODE}}_{{SPGW-PORTAL}}_publicIp'
    str4 = 'CP_mgmtAgent_privateIp'
    str5 = 'CP_mgmtAgent_publicIp'
    str6 = 'SP_SPGW_scale_out_url'
    str7 = 'SP_SPGW_scale_in_url'
    list = [str1, str2,str3,str4,str5,str6,str7]
    vnf = {}
    resp_dict = {'mgmtAgent_IPs': {'publicIp': '192.168.31.57', 'privateIp': '172.240.184.7'}, 'stack_status': 'CREATE_COMPLETE', 'SPGWASG': {'SPGW_SCALING_DOWN': 'http://controller:8004/v1/8cee947f1a244124b58e1425c0b8e3c5/stacks/stack2/228054e7-fced-4869-94cd-f894dc055cc0/resources/SPGW_SCALING_DOWN/signal', 'SPGW_asg_size': 1, 'SPGW_SCALING_UP': 'http://controller:8004/v1/8cee947f1a244124b58e1425c0b8e3c5/stacks/stack2/228054e7-fced-4869-94cd-f894dc055cc0/resources/SPGW_SCALING_UP/signal', 'servers': {'gp3gdatyzinw-kxphcowiyn6a': {'IP': {'publicIp': {'IP': '192.168.31.63', 'MAC': 'fa:16:3e:fd:75:bc', 'version': 4, 'network': 'provider'}, 'privateIp': {'IP': '172.240.184.4', 'MAC': 'fa:16:3e:fd:75:bc', 'version': 4, 'network': 'private'}}, 'State': 'active', 'hostId': '984e1e6d5d405009f899b35a001c05c63acbbcbce52c61e2bd41c394', 'LaunchTime': '2017-10-11T07:52:43.000000', 'Id': '442c4921-3239-4065-84b2-d2cacff4a12e'}}}}
    for i in list:
	match0 = re.match(r'SP_(.*)_scale_(.*)_url',i)
	if not type(match0) is types.NoneType :
	    print '===============%s=================='%(i)
	    print match0.group(1) + ';' + match0.group(2)
	    continue
	match1 = re.match(r'CP_{{(.*?)-NODE}}_{{(.*?)-PORTAL}}_(.*)',i)
	if not type(match1) is types.NoneType :
	    print '===============%s=================='%(i)
	    print match1.group(1) + ';' + match1.group(3)
            ips = []
            for server,info in resp_dict[match1.group(1)+'ASG']['servers'].items():
                tmp = {
                    'server' : server,
                    match1.group(3): info['IP'][match1.group(3)]['IP'],
                    'LaunchTime' :  info['LaunchTime']
                    }
                ips.append(tmp)
	    vnf['value'] = copy.deepcopy(ips)
	    continue
	match2 = re.match(r'CP_(.*)_{{(.*?)-NODE}}_(.*)',i)
	if not type(match2) is types.NoneType :
	    print '===============%s=================='%(i)
	    print match2.group(1) + ';' + match2.group(3)
	    continue
	match3 = re.match(r'CP_(.*)_(.*)',i)
	if not type(match3) is types.NoneType :
	    print '===============%s=================='%(i)
	    print match3.group(1) + ';' + match3.group(2)
	    continue
    print vnf
