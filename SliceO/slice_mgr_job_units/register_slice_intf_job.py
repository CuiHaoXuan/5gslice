#   The class of the slice configuration interface register job unit


import os
import time
from collections import OrderedDict

from common.util import get_class_func_name, CONTEXT_NAMESPACE_SLICE, \
                                         COMPONENT_NAME_NF_MGR, SERVICE_SLICE_INTF_REGISTER, \
                                         SLICE_STATUS_CONF_INISTANTIATING
from common.yaml_util import yaml_ordered_dump as yaml_dump
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-6-14'  
__version__ = 1.0



class SliceIntfRegisterJob(JobUnit):
    
    '''
    this job is used to request the network function manager to register the slice configuration interface.
    this job get inputs:
        slice_id:
    the works done by this job are:
        send a slice configuration interface register request to remote service

    '''
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(SliceIntfRegisterJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        
        try:
            self.slice_id = params['slice_id']
            self._send_intf_register_req()
            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self._execution_exception(Exception, e)
        

    
    
    def _send_intf_register_req(self):

        '''
        send slice configuration interface register request to the remote service, including:
            read the slice config context
            generate request data
            send request to the remote service
        return the response

        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE, self.slice_id)
        ctx_h.get_context_item()['status'] = SLICE_STATUS_CONF_INISTANTIATING
        conf_ctx = ctx_h.get_context_item()['configInfo']
        req_data = {}
        req_data['sender'] = self.task_unit.task_scheduler.other_info.get('localService', {}).get('servType', None)
        req_data['deployment'] = []
        intf_info = {}
        req_data['deployment'].append(intf_info)
        intf_info['slice_id'] = self.slice_id
        intf_info['task_id'] = ctx_h.get_context_item()['nsComboId']
        intf_info['vnf_node_list'] = []
        for vnf_nid, vnf_conf_v in conf_ctx.items():

            #   print '#### SliceIntfRegisterJob: check the configure info of the vnf node: ' + vnf_nid

            vnf_info = {}
            intf_info['vnf_node_list'].append(vnf_info)
            vnf_info['vnf_node_id'] = vnf_nid
            loc = vnf_info.setdefault('config_agent_info', {})
            m_a_ep_info = vnf_conf_v['mgmtAgentHostInfo']['mgmtEndPointInfo']
            loc['agent_public_address'] = m_a_ep_info['rtPublicIp']
            loc['agent_mgmt_address'] = m_a_ep_info['rtPrivateIp']
            loc['agent_username'] = m_a_ep_info['rtUsername']
            loc['agent_password'] = m_a_ep_info['rtPassword']
            vnf_info['vnfc_node_list'] = []
            
            for vnfc_nid, vnfc_conf_v in vnf_conf_v['vnfcMgmtInfo'].items():
                
                #   print '#### SliceIntfRegisterJob: check the configure info of the vnfc node: ' + vnfc_nid
                
                vnfc_prop_info = vnfc_conf_v['configPropertyInfo']
                vnfc_info = {}
                vnf_info['vnfc_node_list'].append(vnfc_info)
                vnfc_info['vnfc_node_id'] = vnfc_nid
                m_vnfc_ep_info = vnfc_conf_v['mgmtEndPointInfo']
                #   for current version, each vnfc node is assumed that only one instance exists
                vnfc_info['mgmt_address'] = m_vnfc_ep_info['rtPrivateIpList'][0]
                vnfc_info['vnfc_node_user'] = m_vnfc_ep_info['rtUsernameList'][0]
                vnfc_info['vnfc_node_passwd'] = m_vnfc_ep_info['rtPasswordList'][0]
                vnfc_info['interface_list'] = []

                for if_id, if_v in vnfc_conf_v['interfaceInfo'].items():
                    if_info = {}
                    vnfc_info['interface_list'].append(if_info)
                    if_info['interface_id'] = if_id
                    if_info['scope'] = if_v['scope']
                    if_info['format'] = self._trans_if_format(if_v, vnfc_prop_info, vnfc_info['mgmt_address'])
                    if_info['path'] = if_v['deployFileAbsPath']
        
        ctx_h.process_finish()

        return self.task_unit.task_scheduler.\
                         req_remote_serv(COMPONENT_NAME_NF_MGR, SERVICE_SLICE_INTF_REGISTER, req_data)

    def _trans_if_format(self, if_ctx, vnfc_prop_ctx, vnfc_mgmt_addr):

        '''
        transform the interface format contained in the interface context (if_ctx)
        by replacing the relavent property expression with the runtime values
        depicted in the vnfc property context (vnfc_prop_ctx) according to the 
        vnfc managment address (vnfc_mgmt_addr)

        '''
        if_format, para_list = if_ctx['format'], if_ctx['involveParas']
        para_v_dict = {}
        for prop in para_list:
            if prop in vnfc_prop_ctx.get('independentParas', {}):
                para_v_dict[prop] = vnfc_prop_ctx['independentParas'][prop]['rtValue'][vnfc_mgmt_addr]
            elif prop in vnfc_prop_ctx.get('dependentParas', {}):
                para_v_dict[prop] = vnfc_prop_ctx['dependentParas'][prop]['rtValue'][vnfc_mgmt_addr]
                #   for current version, each vnfc node is assumed that only one instance exists
                if vnfc_prop_ctx['dependentParas'][prop]['dependency']['multiInstanceOption']:
                    para_v_dict[prop] = vnfc_prop_ctx['dependentParas'][prop]['rtValue'][vnfc_mgmt_addr][0]
        for prop, v in para_v_dict.items():
            #   print '#### SliceIntfRegisterJob: the replaced property: ' + prop + ', value: ' + v
            if_format = if_format.replace('{{' + prop + '}}', v)
        return if_format
