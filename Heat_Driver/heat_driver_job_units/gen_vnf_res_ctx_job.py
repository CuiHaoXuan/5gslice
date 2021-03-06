#   The class of the vnf resource context generation job unit


import os
from copy import deepcopy
from collections import OrderedDict

from common.util import get_class_func_name, cata_download, del_dir_or_file, \
                            VNF_RES_STATUS_DEPLOYING, CONTEXT_NAMESPACE_VNF_RES, \
                            PREFIX_VDU, PREFIX_CP, PREFIX_INTERNAL_VL, \
                            SUFFIX_PRIVATE_IP, SUFFIX_PUBLIC_IP
from common.yaml_util import json_ordered_loads as json_loads, json_ordered_dumps as json_dumps
from ex.openstackclient.os_res_client import OsRestClient as OS_C
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-24'  
__version__ = 1.0



class VnfResCtxGenerateJob(JobUnit):
    
    '''
    this job is used to generate the vnf resource context when vnf resource deploy is requested.
    the works done by this job are:
        allocate a vnf resource id and return
        translate the vnfd to the heat template
        generate and store the vnf resource context, consists with:
            vnfResId:
            relatedSliceResId:
            vnfResStatus:
            dcResId:
            vnfdContent:
            heatTemplate:
            heatStackId:
            relatedVimInfo:
                vimType:
                vimMgrEndPoint:
            outputInfo:
                (vnfdOutputId):
                    heatOutputId:
                    value:
                    
    this job output:
        'vnf_res_id': the id of the vnf resource been processed
    '''
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(VnfResCtxGenerateJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        try:
            self.event = self.task_unit.get_triggered_event()
            self._alloc_vnf_res_id()
            self._init_vnf_res_ctx()
            r_data = {'status': 'request accepted'}
            r_data.update({'vnfResId': self.vnf_res_id})
            self.event.set_return_data_syn(r_data)

            self._enrich_slice_res_ctx()
            self._output_params(**{'slice_res_id': self.slice_res_id})
            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self.event.set_return_data_asyn({'status': 'request failed'})
            self._execution_exception(Exception, e)
    
    def _alloc_vnf_res_id(self):

        '''
        allocate the vnf resource id 

        '''
        id_gen = self.task_unit.task_scheduler.global_id_generator
        slice_res_id = self.event.get_event_data().get('sliceResId', None)
        vnf_nid = self.event.get_event_data().get('vnfNodeId', None)
        self.vnf_res_id = id_gen.get_context_item_id_without_env(slice_res_id, vnf_nid)
    
    def _init_vnf_res_ctx(self):

        '''
        init the vnf resource context according to the data
        contained in the vnf resource deploy request

        '''
        vnf_res_ctx = OrderedDict()
        event_d = self.event.get_event_data()
        vnf_res_ctx['vnfResId'] = self.vnf_res_id
        vnf_res_ctx['relatedSliceResId'] = event_d['sliceResId']
        vnf_res_ctx['dcResId'] = event_d['dcResId']
        vnf_res_ctx['vnfResStatus'] = VNF_RES_STATUS_DEPLOYING
        vnf_res_ctx['vnfdContent'] = event_d['vnfdContent']
        vnf_res_ctx['heatTemplate'] = None
        vnf_res_ctx['heatStackId'] = None
        vim_loc = vnf_res_ctx.setdefault('relatedVimInfo', OrderedDict())
        vim_info = self.task_unit.task_scheduler.get_vim_info_by_dc_res_id(vnf_res_ctx['dcResId'])
        vim_loc['vimType'] = vim_info['vimType']
        vim_loc['vimMgrEndPoint'] = vim_info['endpoint']
        vim_loc['outputInfo'] = OrderedDict()
        
        ctx_store = self.task_unit.task_scheduler.context_store
        ctx_store.add_context_item(vnf_res_ctx, CONTEXT_NAMESPACE_VNF_RES, 
                                   self.vnf_res_id, item_id_n='vnfResId')
 
    
    def _enrich_vnf_res_ctx(self):

        '''
        enrich vnf resource context, including:
            translating vnfd to heat template
            generate mappings between vnfd ouputs and heat outputs
        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_VNF_RES, self.vnf_res_id)
        vnf_res_ctx = ctx_h.get_context_item()
        output_ctx = vnf_res_ctx['outputInfo']
        
        vnfd = vnf_res_ctx['vnfdContent']
        heat_tpl = OrderedDict()
        ddddddd
        
        print '#### GenE2ESliceResCtxJob: the finished slice resource context: '
        print yaml_dump(slice_res_ctx, default_flow_style=False)
        ctx_h.process_finish()
        
    
    def _gen_vdu_login_info(self, **params):

        '''
        generate the vdu login information
        return:
            (username, password)

        '''
        return ('5gslm', 'iaa')
    
