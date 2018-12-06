#   The class of the slice resource processor task scheduler


import os
from copy import deepcopy

from common.util import get_class_func_name, \
                        CONTEXT_NAMESPACE_VNF_RES, EVENT_PRODUCER_LOCAL_REST, \
                        EVENT_TYPE_VNF_RES_DEPLOY, EVENT_TYPE_VNF_RES_INFO_ACQ, \
                        JOB_SEQ_VNF_RES_DEPLOY, SERV_TYPE_VIM
from event_framework.task_scheduler import TaskScheduler, INIT_TYPE_METHOD, INIT_TYPE_SEQ
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-24'  
__version__ = 1.0


class VnfResProcessorScheduler(TaskScheduler):
    
    '''
    this task scheduler responds to handle the vnf resource processing events,
    such as vnf resource deploy, vnf resource information acquiring, and etc.

    '''
    
    def __init__(self, conf_ctx, 
                       ctx_store, 
                       init_type=INIT_TYPE_METHOD,
                       init_job_seq=None, 
                       event_listener_list_syn=True, 
                       other_info={}):
        
        super(VnfResProcessorScheduler, self).__init__(conf_ctx, 
                                                         ctx_store, 
                                                         init_type,
                                                         init_job_seq, 
                                                         event_listener_list_syn, 
                                                         other_info)
    
    def _init_method(self):

        '''
        init method called when the init type is INIT_TYPE_METHOD.
        derived task scheduler classes could override this method,
        initiation like static event listener registry, pre-defined
        context creation could be done in this method
        
        '''
        self._register_vnf_res_deploy_request_listener()
        self._register_vnf_res_info_acquiry_listener()
        
    
    def _register_vnf_res_deploy_request_listener(self):

        '''
        register a event listener handling the vnf resource deploy request,
        the vnf resource deploy request event is matched only by meta info:
            event_type: 'vnf_res_deploy_request'
            event_producer: 'local_rest_api'
        the event will be handled by trigger a processing of:
            job_unit_sequence: 'vnf_res_deploy_job_seq'

        '''
        e_type = self.get_event_type(EVENT_TYPE_VNF_RES_DEPLOY)
        e_producer = self.get_event_producer(EVENT_PRODUCER_LOCAL_REST)
        t_e_data = {}
        t_keys_list = []
        t_e_meta = {META_EVENT_TYPE: e_type, META_EVENT_PRODUCER: e_producer}
        t_meta_keys = [META_EVENT_TYPE, META_EVENT_PRODUCER]
        job_seq = self.get_job_unit_sequence(JOB_SEQ_VNF_RES_DEPLOY)
        self.task_event_listener_register(event_type=e_type, 
                                          target_e_data=t_e_data, 
                                          target_keys_list=t_keys_list,
                                          target_e_meta=t_e_meta, 
                                          target_e_meta_keys=t_meta_keys,
                                          job_unit_sequence=job_seq)
    
    
    def _register_vnf_res_info_acquiry_listener(self):

        '''
        register a event listener handling the vnf resource info acquiry,
        the vnf resource info acquiry event is matched only by meta info:
            event_type: 'vnf_res_info_acquire'
            event_producer: 'local_rest_api'
        the event will be handled by '_vnf_res_info_acquire_handler'

        '''
        e_type = self.get_event_type(EVENT_TYPE_VNF_RES_INFO_ACQ)
        e_producer = self.get_event_producer(EVENT_PRODUCER_LOCAL_REST)
        t_e_data = {}
        t_keys_list = []
        t_e_meta = {META_EVENT_TYPE: e_type, META_EVENT_PRODUCER: e_producer}
        t_meta_keys = [META_EVENT_TYPE, META_EVENT_PRODUCER]
        self._event_listener_register(e_type, 
                                      t_e_data, 
                                      t_keys_list,
                                      t_e_meta, 
                                      t_meta_keys,
                                      self._vnf_res_info_acquire_handler)
    
    def _vnf_res_info_acquire_handler(self, **params):

        '''
        handler handling both the acquiries of all vnfs resource info
        and of a specified vnf resource info by vnf_res_id
        
        '''
        event = params['event']
        vnf_res_id = event.get_event_data().get('vnf_res_id', None)
        ctx_store = self.context_store
        if vnf_res_id:
            h = ctx_store.get_context_item_process_handler(
                                            CONTEXT_NAMESPACE_VNF_RES, vnf_res_id)
            r_data = self._gen_vnf_res_info(h.get_context_item())
            event.set_return_data_asyn(r_data)
            h.process_finish()
            return
        ctx_handlers = ctx_store.get_context_namespace_process_handler(CONTEXT_NAMESPACE_VNF_RES)
        r_data = []
        for h in ctx_handlers:
            ctx = h.get_context_item()
            vnf_res_id = ctx['vnfResId']
            r_data.append(self._gen_vnf_res_info(vnf_res_id, ctx))
            h.process_finish()
        event.set_return_data_asyn(r_data)

    
    def _gen_vnf_res_info(self, ctx):

        r_data = deepcopy(ctx)
        r_data.pop('vnfdContent')
        r_data.pop('heatTemplate')
        return r_data

    
    def get_vim_info_by_dc_res_id(self, dc_res_id):

        '''
        return the vim info recorded in the configuration file
        according to the datacenter resource id

        '''
        vim_info = self.other_info.get('remoteServices', {})
        for k, v in vim_info.items():
            if v['servType'] == SERV_TYPE_VIM:
                if dc_res_id in v.get('datacenters', []):
                    return v
        return None
