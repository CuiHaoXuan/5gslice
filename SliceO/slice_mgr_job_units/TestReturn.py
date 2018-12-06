import os
import json
import yaml

fd_scaling = open('/home/whj/scaling.yaml', 'r')
fd_monitor = open('/home/whj/monitor.yaml', 'r')
raw_scaling = json.dump(yaml.load(fd_scaling))
raw_monitor = json.dump(yaml.load(fd_monitor))['monitorOptions']
ns_monitor = {}
ns_scaling_policy = {}
for vnf_nid, vnf_value in vnf_res_ctx.items():
    vnf_monitor = ns_monitor.setdefault(vnf_nid, {})
    vnf_monitor['Info'] = {
        'vnfNodeId': vnf_nid
    }
    vnf_scaling = vnf_value['vnfScalingPolicyInfo']
    vnf_monitor['VnfcNodes'] = []
    vnf_scaling_police = ns_scaling_policy.setdefault(vnf_nid, {})
    for vnfc_nid, vnfc_value in vnf_value['vnfcResInfo'].items():
        vnfc_scaling_policy = vnf_scaling_police.setdefault(vnfc_nid, {})
        for policy_key, policy_value in vnf_scaling:
            if policy_value['targetVnfcNodeIdList'][0] == vnfc_nid:
                if policy_key.endswith('out'):
                    vnfc_scaling_policy['out'] = policy_value['rtTriggerUrl']
                elif policy_key.endswith('in'):
                    vnfc_scaling_policy['in'] = policy_value['rtTriggerUrl']
        ip_list = []
        for end_point in vnfc_value['vnfcEndPointResInfo'].values():
            ip_list = end_point['rtPrivateIpList']
            break
        vnfc_info = {
            'vnfcNodeId': vnfc_nid,
            'ip': ip_list[0],
            'scaleIn': vnfc_scaling_policy['in'],
            'scaleOut': vnfc_scaling_policy['out']
        }
        vnf_monitor['VnfcNodes'].append(vnfc_info)
    mgmt_host = vnf_conf_ctx[vnf_nid]['mgmtAgentHostInfo']
    mgmt_id = mgmt_host['vduId']
    mgmt_public_ip = mgmt_host['mgmtEndPointInfo']['rtPublicIp']
    vnf_monitor['MgmtNode'] = {
        'vnfcNodeId': mgmt_id,
        'ip': mgmt_public_ip
    }
    vnf_monitor['MonitorOptions'] = []
    for monitor_option in monitor_options:
        for key, value in monitor_option.items():
            params = value['parameters']
            param = params[0]
            for v in param.values():
                target_vnf_node = v['target'][0]
                if vnf_nid == target_vnf_node:
                    vnf_monitor['MonitorOptions'].append(monitor_option)
print "====================watch me : ns monitor =================\n"
print ns_monitor