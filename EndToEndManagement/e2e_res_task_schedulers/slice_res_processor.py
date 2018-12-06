#   The class of the slice resource processor task scheduler


import os
import urllib2
from copy import deepcopy

from common.util import get_class_func_name, \
                        CONTEXT_NAMESPACE_SLICE_RES, EVENT_PRODUCER_LOCAL_REST, \
                        EVENT_TYPE_SLICE_RES_DEPLOY, EVENT_TYPE_SLICE_RES_INFO_ACQ, \
                        JOB_SEQ_SLICE_RES_DEPLOY, SERV_TYPE_VIM_DRIVER
from common.yaml_util import json_ordered_loads as json_loads, json_ordered_dumps as json_dumps
from event_framework.task_scheduler import TaskScheduler, INIT_TYPE_METHOD, INIT_TYPE_SEQ
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-18'  
__version__ = 1.0


class SliceResProcessorScheduler(TaskScheduler):
    
    '''
    this task scheduler responds to handle the slice resource processing events,
    such as slice resource deploy, slice resource information acquiring, and etc.

    '''
    
    def __init__(self, conf_ctx, 
                       ctx_store, 
                       init_type=INIT_TYPE_METHOD,
                       init_job_seq=None, 
                       event_listener_list_syn=True, 
                       other_info={}):
        
        super(SliceResProcessorScheduler, self).__init__(conf_ctx, 
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
        self._register_slice_res_deploy_request_listener()
        self._register_slice_res_info_acquiry_listener()
        
    
    def _register_slice_res_deploy_request_listener(self):

        '''
        register a event listener handling the slice resource deploy request,
        the slice resource deploy request event is matched only by meta info:
            event_type: 'slice_res_deploy_request'
            event_producer: 'local_rest_api'
        the event will be handled by trigger a processing of:
            job_unit_sequence: 'slice_res_deploy_job_seq'

        '''
        e_type = self.get_event_type(EVENT_TYPE_SLICE_RES_DEPLOY)
        e_producer = self.get_event_producer(EVENT_PRODUCER_LOCAL_REST)
        t_e_data = {}
        t_keys_list = []
        t_e_meta = {META_EVENT_TYPE: e_type, META_EVENT_PRODUCER: e_producer}
        t_meta_keys = [META_EVENT_TYPE, META_EVENT_PRODUCER]
        job_seq = self.get_job_unit_sequence(JOB_SEQ_SLICE_RES_DEPLOY)
        self.task_event_listener_register(event_type=e_type, 
                                          target_e_data=t_e_data, 
                                          target_keys_list=t_keys_list,
                                          target_e_meta=t_e_meta, 
                                          target_e_meta_keys=t_meta_keys,
                                          job_unit_sequence=job_seq)
    
    
    def _register_slice_res_info_acquiry_listener(self):

        '''
        register a event listener handling the slice resource info acquiry,
        the slice resource info acquiry event is matched only by meta info:
            event_type: 'slice_res_info_acquire'
            event_producer: 'local_rest_api'
        the event will be handled by '_slice_res_info_acquire_handler'

        '''
        e_type = self.get_event_type(EVENT_TYPE_SLICE_RES_INFO_ACQ)
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
                                      self._slice_res_info_acquire_handler)
    
    def _slice_res_info_acquire_handler(self, **params):

        '''
        handler handling both the acquiries of all slices resource info
        and of a specified slice resource info by slice_res_id
        
        '''
        event = params['event']
        slice_res_id = event.get_event_data().get('slice_res_id', None)
        ctx_store = self.context_store
        if slice_res_id:
            h = ctx_store.get_context_item_process_handler(
                                            CONTEXT_NAMESPACE_SLICE_RES, slice_res_id)
            r_data = self._gen_slice_res_info(slice_res_id, h.get_context_item())
            event.set_return_data_asyn(r_data)
            h.process_finish()
            return
        ctx_handlers = ctx_store.get_context_namespace_process_handler(CONTEXT_NAMESPACE_SLICE_RES)
        r_data = []
        for h in ctx_handlers:
            ctx = h.get_context_item()
            slice_res_id = ctx['sliceResId']
            r_data.append(self._gen_slice_res_info(slice_res_id, ctx))
            h.process_finish()
        event.set_return_data_asyn(r_data)

    
    def _gen_slice_res_info(self, slice_res_id, ctx):

        r_data = deepcopy(ctx)
        r_data.pop('nsdContent')
        for k, v in r_data['vnfResInfo'].items():
            v.pop('vnfdContent')
        return dict(r_data)
    
    def get_vim_driver_by_dc_id(self, dc_id):

        '''
        return the corresponding vim driver's component name by datacenter resource id.
        the information should be included in the configuration yaml file

        '''
        vim_d_info = self.other_info.get('remoteServices', {})
        for k, v in vim_d_info.items():
            if v['servType'] == SERV_TYPE_VIM_DRIVER:
                if dc_id in v.get('datacenters', []):
                    return k
        return None

    def req_remote_serv(self, comp_name, serv_name, req_data, **url_para):

        '''
        request a remote service indicated by the service component name and service name
        with the request data and the url parameters, and return the response data

        '''
        serv_info = self.other_info.get('remoteServices', {})
        serv_info = serv_info.get(comp_name, {})
        comp_ip = serv_info['ip']
        comp_port = serv_info['port']
        serv_info = serv_info['services']
        serv_info = serv_info.get(serv_name, {})
        serv_method = serv_info['method']
        serv_url = 'http://' + comp_ip + ':' + str(comp_port)
        serv_url = serv_url + serv_info['url']
        for k, v in url_para.items():
            serv_url = serv_url.replace('<' + k + '>', v)
          
        params = None
        headers = {"Accept": "application/json"}
        if serv_method == 'POST':
            params = json_dumps(req_data) 
            headers.update({"Content-type":"application/json"})
        req = urllib2.Request(serv_url, params, headers)
        raw_data = urllib2.urlopen(req).read()
        #   print '!!!!!!!!!!!!!DEBUG: response data: ', raw_data, " type is : ", type(raw_data)
        ddata = eval(raw_data)    
        return ddata

