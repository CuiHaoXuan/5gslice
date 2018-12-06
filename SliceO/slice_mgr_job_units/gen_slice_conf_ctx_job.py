#   The class of the slice configuration context generation job unit


import os
from collections import OrderedDict
from copy import deepcopy

from common.util import get_class_func_name, cata_download, del_dir_or_file, \
                            SLICE_STATUS_RES_INISTANTIATING, CONTEXT_NAMESPACE_SLICE
from common.yaml_util import yaml_ordered_load as yaml_load, yaml_ordered_dump as yaml_dump
from tools.vnfd_tools import VnfdTool
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-17'  
__version__ = 1.0



class SliceConfCtxGenerateJob(JobUnit):
    
    '''
    this job is used to generate the slice configuration context.
    this job get inputs:
        slice_id:
    the works done by this job are:
        insert management agent host, vdu management cp and networks in to vnfd contents
        generate and store the slice configuration context, consists with:
            configInfo:
                (vnfNodeId):
                    mgmtAgentHostInfo:
                        vduId:
                        mgmtEndPointInfo:
                            cpId:
                            rtPrivateIp:
                            rtPublicIp:
                            rtUsername:
                            rtPassword:
                    vnfcMgmtInfo:
                        (vnfcNodeId):
                            vduId:
                            mgmtEndPointInfo:
                                cpId:
                                rtPrivateIpList:
                                rtUsernameList:
                                rtPasswordList:
                            configPropertyInfo:
                                using the similar achitecture in the metadata 
                                by adding a 'rtValue' section indicating the runtime value of the property
                            interfaceInfo:
                                using the similar achitecture in the metadata
                                by adding a 'rtFormat' section indicating the runtime format of the interface execution

    '''
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(SliceConfCtxGenerateJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        
        try:
            self.slice_id = params['slice_id']
            self._gen_conf_ctx()
            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self._execution_exception(Exception, e)
        

    
    
    def _gen_conf_ctx(self):

        '''
        generate configuration context, including:
            insert management resources into vnfds
            create the configuration context and runtime info
            derive the property and interface info from the metadata, 
            and add the runtime info

        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE, self.slice_id)
        slice_ctx = ctx_h.get_context_item()
        
        #   create configuration context from metadata
        ctx_loc = slice_ctx.setdefault('configInfo', OrderedDict())
        res_ctx_loc = slice_ctx['resourceInfo']['nsResInfo']['vnfResInfo']

        for vnf_nid, vnf_res_v in res_ctx_loc.items():
            #   insert management agent host resources into the vnfd
            vnfd = vnf_res_v['vnfdContent']
            vnfd_t = VnfdTool(vnfd)
            vnfd_t.add_mgmt_agent_res()

            #   add vnf managemnt agent host info into configuration context
            vnf_loc = ctx_loc.setdefault(vnf_nid, OrderedDict())
            loc = vnf_loc.setdefault('mgmtAgentHostInfo', OrderedDict())
            loc['vduId'] = vnfd_t.mgmt_agent_vdu_id
            loc = loc.setdefault('mgmtEndPointInfo', OrderedDict())
            loc['cpId'] = vnfd_t.mgmt_agent_cp_id
            loc['rtPrivateIp'], loc['rtPublicIp'], loc['rtUsername'], loc['rtPassword'] = \
                                                None, None, None, None

            
            vnfc_ctx_loc = vnf_loc.setdefault('vnfcMgmtInfo', OrderedDict())
            for vnfc_nid, vnfc_res_v in vnf_res_v['vnfcResInfo'].items():
                
                #   insert management cp resources for each vnfc node into the vnfd
                vdu_id = vnfc_res_v['vduId']
                mgmt_cp_id = vnfd_t.add_vnfc_mgmt_cp_res(vnfc_nid, vdu_id)
                vnfc_loc = vnfc_ctx_loc.setdefault(vnfc_nid, OrderedDict())
                vnfc_loc['vduId'] = vdu_id
                loc = vnfc_loc.setdefault('mgmtEndPointInfo', OrderedDict())
                loc['cpId'] = mgmt_cp_id
                loc['rtPrivateIpList'] = []
                loc['rtUsernameList'] = []
                loc['rtPasswordList'] = []

                #   derive configurable properties info from the metadata
                loc = vnfc_loc.setdefault('configPropertyInfo', OrderedDict())
                para_ctx = slice_ctx['metadata']['parameterInfo']
                para_ctx = para_ctx.get(vnf_nid, OrderedDict())
                para_ctx = para_ctx.get(vnfc_nid, OrderedDict())
                loc.update(deepcopy(para_ctx))
                for k, v in loc.get('dependentParas', OrderedDict()).items():
                    v['rtValue'] = None
                for k, v in loc.get('independentParas', OrderedDict()).items():
                    v['rtValue'] = None

                #   derive interfaces info from the metadata
                loc = vnfc_loc.setdefault('interfaceInfo', OrderedDict())
                if_ctx = slice_ctx['metadata']['vnfcConfigInfo']
                if_ctx = if_ctx.get(vnf_nid, OrderedDict())
                if_ctx = if_ctx.get(vnfc_nid, OrderedDict())
                loc.update(deepcopy(if_ctx))
                for k, v in loc.items():
                    v['rtFormat'] = None
        
        print '#### GenSliceConfCtxJob: generate slice configuration context with slice id: ' + self.slice_id
        #   print yaml_dump(slice_ctx['configInfo'], default_flow_style=False)
        ctx_h.process_finish()
    
