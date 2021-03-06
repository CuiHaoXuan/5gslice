#   The class of the slice processor task scheduler


import os
import urllib2
from collections import OrderedDict
from copy import deepcopy

from common.util import get_class_func_name, \
                        CONTEXT_NAMESPACE_SLICE, EVENT_PRODUCER_LOCAL_REST, \
                        EVENT_TYPE_SLICE_INSTANTIATION, EVENT_TYPE_SLICE_INFO_ACQ, \
                        JOB_SEQ_SLICE_INSTANTIATION, COMPONENT_NAME_PLAN_ENGINE
from common.yaml_util import json_ordered_loads as json_loads, json_ordered_dumps as json_dumps
from event_framework.task_scheduler import TaskScheduler, INIT_TYPE_METHOD, INIT_TYPE_SEQ
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-16'  
__version__ = 1.0


class SliceProcessorScheduler(TaskScheduler):
    
    '''
    this task scheduler responds to handle the slice processing events,
    such as slice instantiation, slice information acquiring, and etc.
    this task scheduler should share a common context store instance 
    with the csar processor scheduler

    '''
    
    def __init__(self, conf_ctx, 
                       ctx_store, 
                       init_type=INIT_TYPE_METHOD,
                       init_job_seq=None, 
                       event_listener_list_syn=True, 
                       other_info={}):
        
        super(SliceProcessorScheduler, self).__init__(conf_ctx, 
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
        self._register_slice_instantiation_request_listener()
        self._register_slice_info_acquiry_listener()
        
    
    def _register_slice_instantiation_request_listener(self):

        '''
        register a event listener handling the slice instantiation request,
        the slice instantiation request event is matched only by meta info:
            event_type: 'slice_instantiation_request'
            event_producer: 'local_rest_api'
        the event will be handled by trigger a processing of:
            job_unit_sequence: 'slice_instantiation_job_seq'

        '''
        e_type = self.get_event_type(EVENT_TYPE_SLICE_INSTANTIATION)
        e_producer = self.get_event_producer(EVENT_PRODUCER_LOCAL_REST)
        t_e_data = {}
        t_keys_list = []
        t_e_meta = {META_EVENT_TYPE: e_type, META_EVENT_PRODUCER: e_producer}
        t_meta_keys = [META_EVENT_TYPE, META_EVENT_PRODUCER]
        job_seq = self.get_job_unit_sequence(JOB_SEQ_SLICE_INSTANTIATION)
        self.task_event_listener_register(event_type=e_type, 
                                          target_e_data=t_e_data, 
                                          target_keys_list=t_keys_list,
                                          target_e_meta=t_e_meta, 
                                          target_e_meta_keys=t_meta_keys,
                                          job_unit_sequence=job_seq)
    
    
    def _register_slice_info_acquiry_listener(self):

        '''
        register a event listener handling the slice info acquiry,
        the slice info acquiry event is matched only by meta info:
            event_type: 'slice_info_acquire'
            event_producer: 'local_rest_api'
        the event will be handled by '_slice_info_acquire_handler'

        '''
        e_type = self.get_event_type(EVENT_TYPE_SLICE_INFO_ACQ)
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
                                      self._slice_info_acquire_handler)
    
    def _slice_info_acquire_handler(self, **params):

        '''
        handler handling both the acquiries of all slices information
        and of a specified slice info by slice_id
        
        '''
        event = params['event']
        slice_id = event.get_event_data().get('slice_id', None)
        ctx_store = self.context_store
        if slice_id:
            h = ctx_store.get_context_item_process_handler(
                                            CONTEXT_NAMESPACE_SLICE, slice_id)
            ctx = h.get_context_item()
            r_data = self._gen_slice_info(slice_id, ctx)
            event.set_return_data_asyn(r_data)
            h.process_finish()
            return
        ctx_handlers = ctx_store.get_context_namespace_process_handler(CONTEXT_NAMESPACE_SLICE)
        r_data = []
        for h in ctx_handlers:
            ctx = h.get_context_item()
            slice_id = ctx['sliceId']
            r_data.append(self._gen_slice_info(slice_id, ctx))
            h.process_finish()
        event.set_return_data_asyn(r_data)

    
    def _gen_slice_info(self, slice_id, ctx):

        '''
        generate and return slice info according to slice id and the ctx

        '''
        r_data = OrderedDict()
        r_data['sliceId'] = ctx['sliceId']
        r_data['status'] = ctx['status']
        r_data['relatedCsarId'] = ctx['relatedCsarId']
        r_data['csarCataDir'] = ctx['csarCataDir']
        r_data['metadata'] = OrderedDict()
        r_data['resourceInfo'] = deepcopy(ctx['resourceInfo'])
        res = r_data['resourceInfo']['nsResInfo']
        res.pop('nsdContent')
        for k, v in res['vnfResInfo'].items():
            v.pop('vnfdContent')
        r_data = r_data['metadata']
        meta_ctx = ctx['metadata']
        r_data['nsFlavorInfo'] = meta_ctx['nsFlavorInfo']
        r_data['tenantInfo'] = meta_ctx['tenantInfo']
        r_data['slaInfo'] = meta_ctx['slaInfo']
        r_data['topologyInfo'] = meta_ctx['topoloyInfo']

        return r_data
    
    
    def get_catalogue_serv_ip(self):
        
        '''
        get the catalogue service ip address
        
        '''
        remote_servs =  self.other_info.get('remoteServices', {})
        cata_serv = remote_servs.get('catalogue', {})
        return cata_serv.get('ip', None)

    def get_catalogue_serv_port(self):
        
        '''
        get the catalogue service ip address
        
        '''
        remote_servs =  self.other_info.get('remoteServices', {})
        cata_serv = remote_servs.get('catalogue', {})
        return cata_serv.get('port', None)

    def get_catalogue_serv_username(self):
        
        '''
        get the catalogue service username
        
        '''
        remote_servs =  self.other_info.get('remoteServices', {})
        cata_serv = remote_servs.get('catalogue', {})
        return cata_serv.get('username', None)

    def get_catalogue_serv_password(self):
        
        '''
        get the catalogue service password
        
        '''
        remote_servs =  self.other_info.get('remoteServices', {})
        cata_serv = remote_servs.get('catalogue', {})
        return cata_serv.get('password', None)

    def get_catalogue_serv_proto(self):
        
        '''
        get the catalogue service transport protocal
        
        '''
        remote_servs =  self.other_info.get('remoteServices', {})
        cata_serv = remote_servs.get('catalogue', {})
        return cata_serv.get('protocal', None)

    def get_catalogue_serv_dir(self):
        
        '''
        get the catalogue service dir architecture info
        
        '''
        remote_servs =  self.other_info.get('remoteServices', {})
        cata_serv = remote_servs.get('catalogue', {})
        return cata_serv.get('catalogueDir', {})

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
        if comp_name == COMPONENT_NAME_PLAN_ENGINE:
            headers = {}
        if serv_method == 'POST':
            params = json_dumps(req_data) 
            headers.update({"Content-type":"application/json"})
        req = urllib2.Request(serv_url, params, headers)    
        ddata = json_loads(urllib2.urlopen(req).read())    
        return ddata

    def req_remote_serv_with_headers(self, comp_name, serv_name, req_data, headers_dict, **url_para):

        '''
        make a request with the customized headers

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
        headers.update(headers_dict)
        if serv_method == 'POST':
            params = json_dumps(req_data) 
            headers.update({"Content-type":"application/json"})
        req = urllib2.Request(serv_url, params, headers)    
        ddata = json_loads(urllib2.urlopen(req).read())    
        return ddata

