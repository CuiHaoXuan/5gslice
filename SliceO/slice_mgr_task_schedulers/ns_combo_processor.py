#   The class of the ns combo processor task scheduler


import os
import urllib2
from collections import OrderedDict
from copy import deepcopy

from common.util import get_class_func_name, \
                        CONTEXT_NAMESPACE_NS_COMBO, EVENT_PRODUCER_LOCAL_REST, \
                        EVENT_TYPE_LOCAL_NS_COMBO_UPLOAD, EVENT_TYPE_NS_COMBO_ONBOARDING, \
                        EVENT_TYPE_NS_COMBO_INSTANTIATION, EVENT_TYPE_NS_COMBO_INFO_ACQ, \
                        JOB_SEQ_LOCAL_NS_COMBO_UPLOAD, JOB_SEQ_NS_COMBO_ONBOARDING, \
                        JOB_SEQ_NS_COMBO_INSTANTIATION, \
                        LOCAL_SERVICE_CSAR_UPLOAD, LOCAL_SERVICE_CSAR_ONBOARDING, \
                        LOCAL_SERVICE_SUBSLICE_INSTANTIATION
from common.yaml_util import json_ordered_loads as json_loads, json_ordered_dumps as json_dumps
from event_framework.task_scheduler import TaskScheduler, INIT_TYPE_METHOD, INIT_TYPE_SEQ
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-6-1'  
__version__ = 1.0


class NsComboProcessorScheduler(TaskScheduler):
    
    '''
    this task scheduler responds to handle the ns combo processing events,
    such as ns combo instantiation, ns combo information acquiring, and etc.
    this task scheduler should share a common context store instance 
    with the csar processor scheduler and the slice processor scheduler

    '''
    
    def __init__(self, conf_ctx, 
                       ctx_store, 
                       init_type=INIT_TYPE_METHOD,
                       init_job_seq=None, 
                       event_listener_list_syn=True, 
                       other_info={}):
        
        super(NsComboProcessorScheduler, self).__init__(conf_ctx, 
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
        self._register_local_ns_combo_upload_request_listener()
        self._register_ns_combo_onboarding_request_listener()
        self._register_ns_combo_instantiation_request_listener()
        self._register_ns_combo_info_acquiry_listener()
        
    
    def _register_local_ns_combo_upload_request_listener(self):

        '''
        register a event listener handling the local ns combo upload request,
        the ns combo upload request event is matched only by meta info:
            event_type: 'local_ns_combo_upload_request'
            event_producer: 'local_rest_api'
        the event will be handled by trigger a processing of:
            job_unit_sequence: 'local_ns_combo_upload_job_seq'

        '''
        e_type = self.get_event_type(EVENT_TYPE_LOCAL_NS_COMBO_UPLOAD)
        e_producer = self.get_event_producer(EVENT_PRODUCER_LOCAL_REST)
        t_e_data = {}
        t_keys_list = []
        t_e_meta = {META_EVENT_TYPE: e_type, META_EVENT_PRODUCER: e_producer}
        t_meta_keys = [META_EVENT_TYPE, META_EVENT_PRODUCER]
        job_seq = self.get_job_unit_sequence(JOB_SEQ_LOCAL_NS_COMBO_UPLOAD)
        self.task_event_listener_register(event_type=e_type, 
                                          target_e_data=t_e_data, 
                                          target_keys_list=t_keys_list,
                                          target_e_meta=t_e_meta, 
                                          target_e_meta_keys=t_meta_keys,
                                          job_unit_sequence=job_seq)
    
    def _register_ns_combo_onboarding_request_listener(self):

        '''
        register a event listener handling the ns combo onboarding request,
        the ns combo onboarding request event is matched only by meta info:
            event_type: 'ns_combo_onboarding_request'
            event_producer: 'local_rest_api'
        the event will be handled by trigger a processing of:
            job_unit_sequence: 'ns_combo_onboarding_job_seq'

        '''
        e_type = self.get_event_type(EVENT_TYPE_NS_COMBO_ONBOARDING)
        e_producer = self.get_event_producer(EVENT_PRODUCER_LOCAL_REST)
        t_e_data = {}
        t_keys_list = []
        t_e_meta = {META_EVENT_TYPE: e_type, META_EVENT_PRODUCER: e_producer}
        t_meta_keys = [META_EVENT_TYPE, META_EVENT_PRODUCER]
        job_seq = self.get_job_unit_sequence(JOB_SEQ_NS_COMBO_ONBOARDING)
        self.task_event_listener_register(event_type=e_type, 
                                          target_e_data=t_e_data, 
                                          target_keys_list=t_keys_list,
                                          target_e_meta=t_e_meta, 
                                          target_e_meta_keys=t_meta_keys,
                                          job_unit_sequence=job_seq)
    
    def _register_ns_combo_instantiation_request_listener(self):

        '''
        register a event listener handling the ns combo instantiation request,
        the ns combo instantiation request event is matched only by meta info:
            event_type: 'ns_combo_instantiation_request'
            event_producer: 'local_rest_api'
        the event will be handled by trigger a processing of:
            job_unit_sequence: 'ns_combo_instantiation_job_seq'

        '''
        e_type = self.get_event_type(EVENT_TYPE_NS_COMBO_INSTANTIATION)
        e_producer = self.get_event_producer(EVENT_PRODUCER_LOCAL_REST)
        t_e_data = {}
        t_keys_list = []
        t_e_meta = {META_EVENT_TYPE: e_type, META_EVENT_PRODUCER: e_producer}
        t_meta_keys = [META_EVENT_TYPE, META_EVENT_PRODUCER]
        job_seq = self.get_job_unit_sequence(JOB_SEQ_NS_COMBO_INSTANTIATION)
        self.task_event_listener_register(event_type=e_type, 
                                          target_e_data=t_e_data, 
                                          target_keys_list=t_keys_list,
                                          target_e_meta=t_e_meta, 
                                          target_e_meta_keys=t_meta_keys,
                                          job_unit_sequence=job_seq)
    
    
    def _register_ns_combo_info_acquiry_listener(self):

        '''
        register a event listener handling the ns combo info acquiry,
        the ns combo info acquiry event is matched only by meta info:
            event_type: 'ns_combo_info_acquire'
            event_producer: 'local_rest_api'
        the event will be handled by '_ns_combo_info_acquire_handler'

        '''
        e_type = self.get_event_type(EVENT_TYPE_NS_COMBO_INFO_ACQ)
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
                                      self._ns_combo_info_acquire_handler)
    
    def _ns_combo_info_acquire_handler(self, **params):

        '''
        handler handling both the acquiries of all ns combos information
        and of a specified ns combo info by ns_combo_id
        
        '''
        event = params['event']
        ns_combo_id = event.get_event_data().get('ns_combo_id', None)
        ctx_store = self.context_store
        if ns_combo_id:
            h = ctx_store.get_context_item_process_handler(
                                            CONTEXT_NAMESPACE_NS_COMBO, ns_combo_id)
            event.set_return_data_asyn(h.get_context_item())
            h.process_finish()
            return
        ctx_handlers = ctx_store.get_context_namespace_process_handler(CONTEXT_NAMESPACE_NS_COMBO)
        r_data = []
        for h in ctx_handlers:
            r_data.append(h.get_context_item())
            h.process_finish()
        event.set_return_data_asyn(r_data)
    
    def req_local_serv(self, serv_name, req_data, **url_para):

        '''
        request a local service indicated by the service name
        with the request data and the url parameters, and return the response data

        '''
        if not req_data:
            req_data = {}
        serv_info = self.other_info.get('localService', {})
        local_ip = serv_info['ip']
        local_port = serv_info['port']
        serv_info = serv_info['services']
        serv_info = serv_info.get(serv_name, {})
        serv_method = serv_info['method']
        serv_url = 'http://' + local_ip + ':' + str(local_port)
        serv_url = serv_url + serv_info['url']
        for k, v in url_para.items():
            serv_url = serv_url.replace('<' + k + '>', v)
          
	print "serv_url in req_local_serv"
	print serv_url
        params = None
        headers = {"Accept": "application/json"}
        if serv_method == 'POST':
            params = json_dumps(req_data) 
            headers.update({"Content-type":"application/json"})
        req = urllib2.Request(serv_url, params, headers)    
        ddata = json_loads(urllib2.urlopen(req).read())    
        return ddata
    
    def req_csar_upload_serv(self, csar_n, ns_combo_id, sub_ns_nid, tenant_id, trade_id, desc, csar_p):

        '''
        request the csar upload service of the local service,
        and return the respond data

        '''
        r_data = OrderedDict()
        r_data['csarName'], r_data['nsComboId'], r_data['subNsNodeId'], r_data['tenantId'], r_data['tradeId'], \
                    r_data['description'], r_data['csarLocalPath'] = \
        csar_n, ns_combo_id, sub_ns_nid, tenant_id, trade_id, desc, csar_p
        return self.req_local_serv(LOCAL_SERVICE_CSAR_UPLOAD, r_data)

    
    def req_csar_onboarding_serv(self, csar_id):

        '''
        request the csar onboarding service of the local service,
        and return the respond data

        '''
        return self.req_local_serv(LOCAL_SERVICE_CSAR_ONBOARDING, None, csar_id=csar_id)

    def req_subslice_instantiation_serv(self, sub_slice_id):

        '''
        request the subslice instantiation service of the local service,
        and return the respond data

        '''
        return self.req_local_serv(LOCAL_SERVICE_SUBSLICE_INSTANTIATION, None, sub_slice_id=sub_slice_id)
    
    def req_remote_serv(self, comp_name, serv_name, req_data, **url_para):

        '''
        request a remote service indicated by the service component name and service name
        with the request data and the url parameters, and return the response data

        '''
        if not req_data:
            req_data = {}
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
        ddata = json_loads(urllib2.urlopen(req).read())    
        return ddata

