#   The class of the vnf resource deployment job unit


import os
import time
from collections import OrderedDict
from copy import deepcopy

from common.util import get_class_func_name, CONTEXT_NAMESPACE_SLICE_RES, \
                                          SERVICE_VNF_RES_DEPLOY, SERVICE_VNF_RES_ACQUIRE, \
                                          SLICE_RES_STATUS_COMPLETE, SLICE_RES_STATUS_FAIL, \
                                          VNF_RES_STATUS_DEPLOYING, VNF_RES_STATUS_COMPLETE, VNF_RES_STATUS_FAIL
from common.yaml_util import yaml_ordered_dump as yaml_dump
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-24'  
__version__ = 1.0



class VnfResDeployJob(JobUnit):
    
    '''
    this job is used to request the heat driver to deploy the resource of each vnf.
    this job get inputs:
        slice_res_id:
    the works done by this job are:
        send a vnf resource deployment request to remote service for each vnf
        periodically check the remote service whether the deployment completes

    '''
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(VnfResDeployJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        
        try:
            print "#########3DEBUG#########3", params
            self.slice_res_id = params['slice_res_id']
            self._send_vnfs_res_deploy_req()
            print '_send_vnfs_res_deploy_req'
            self._wait_vnfs_res_deploy()
            print '_wait_vnfs_res_deploy'
            self._update_slice_res_ctx()
            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self._execution_exception(Exception, e)
        

    
    
    def _send_vnfs_res_deploy_req(self):

        '''
        send vnfs resource deployment request to the remote service, including:
            read the slice resource context
            generate request data for each vnf node
            send request to the remote service, 
            and recorde the returned vnf_res_id to the resource context

        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE_RES, self.slice_res_id)
        vnf_res = ctx_h.get_context_item()['vnfResInfo']
        req_data = {}
        for vnf_nid, v in vnf_res.items():
            loc = req_data.setdefault(vnf_nid, {})
            loc['req_data'] = {}
            loc['req_data']['sliceResId'] = self.slice_res_id
            loc['req_data']['vnfNodeId'] = vnf_nid
            loc['req_data']['vnfdContent'] = v['vnfdContent']
            loc['req_data']['dcResId'] = v['dcResId']
            loc['vim_driver'] = v['vimDriverId']
        
        print "############DEBUG##########"
        print loc
        ctx_h.process_finish()
        print '###########DEBUG##########'
        print "ctx_h.process_finish()"
        resp = {}
        for vnf_nid, v in req_data.items():
            print '#############DEBUG###########'
            #print v['vim_driver'], v[req_data]
            resp[vnf_nid] = self.task_unit.task_scheduler.\
                         req_remote_serv(v['vim_driver'], SERVICE_VNF_RES_DEPLOY, v['req_data'])
            print "!!!!!!!!!!!!!!!!!!!DEBUG : VNF_NID : ",vnf_nid, ' : ' , resp[vnf_nid] 
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE_RES, self.slice_res_id)
        vnf_res = ctx_h.get_context_item()['vnfResInfo']
	print "================this is the vnf_res =================="
	print vnf_res
        for vnf_nid, v in resp.items():
            if 'deploying' == v.get('vnfResStatus', None):
                vnf_res[vnf_nid]['vnfResId'] = v['vnfResId']
                vnf_res[vnf_nid]['vnfResStatus'] = v['vnfResStatus']
            else:
                raise Exception('#### VnfResDeployJob: vnf of %s resource deployment request failed' % vnf_nid)
        ctx_h.process_finish()

    def _wait_vnfs_res_deploy(self):

        '''
        periordically check the remote service until all the vnf resource deployments complete

        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE_RES, self.slice_res_id)
        vnf_res = ctx_h.get_context_item()['vnfResInfo']
        url_para = {}
        vim_driver = {}
        vnf_res_status = {}
        for vnf_nid, v in vnf_res.items():
            url_para[vnf_nid] = {'vnf_res_id': v['vnfResId']}
            vnf_res_status[vnf_nid] = v['vnfResStatus']
            vim_driver[vnf_nid] = v['vimDriverId']
        ctx_h.process_finish()
        self.vnf_deploy_resp = {}
        while 'deploying' in vnf_res_status.values():
            time.sleep(5)
            for vnf_nid, v in url_para.items():
                self.vnf_deploy_resp[vnf_nid] = self.task_unit.task_scheduler.\
                         req_remote_serv(vim_driver[vnf_nid], SERVICE_VNF_RES_ACQUIRE, {}, **v)
                res_status = self.vnf_deploy_resp[vnf_nid].get('vnfResStatus')
                vnf_res_status[vnf_nid] = res_status
                if res_status == 'failed':
                    ctx_store = self.task_unit.task_scheduler.context_store
                    ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE_RES, self.slice_res_id)
                    slice_res_ctx = ctx_h.get_context_item()
                    slice_res_ctx['sliceResGlobalStatus'] = 'failed' 
                    ctx_h.process_finish()
                    raise Exception('#### VnfResDeployJob: vnf of %s resource deployment request failed' % vnf_nid)
        
        print '#### VnfResDeployJob: vnf resource deployments complete: '
        print yaml_dump(self.vnf_deploy_resp, default_flow_style=False)

    def _update_slice_res_ctx(self):

        '''
        update the slice resource context by the return data of the vim driver

        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE_RES, self.slice_res_id)
        slice_res_ctx = ctx_h.get_context_item()
        vnf_res = slice_res_ctx['vnfResInfo']
        slice_res_ctx['sliceResGlobalStatus'] = 'completed'
        for vnf_nid, v in vnf_res.items():
            r_data = self.vnf_deploy_resp[vnf_nid]
            v['vnfResStatus'] = 'completed' 
            v['relatedVimInfo']['vimType'] = \
                          r_data.get('relatedVimInfo', {}).get('vimType', None)
            v['relatedVimInfo']['vimMgrEndPoint'] = \
                          r_data.get('relatedVimInfo', {}).get('vimMgrEndPoint', None)
            cp_res = v['cpInfo']
            for cp_info in cp_res.values():
                pri_info = cp_info['privateIpInfo']
                if 'relatedOutputId' in pri_info.keys():
                    val = r_data['outputInfo'].get(pri_info['relatedOutputId'], {})\
                                         .get('value', None)
                    if val:
                        if isinstance(val, list):
                            pri_info['ipList'] = val
                        else:
                            pri_info['ipList'].append(val)

                pub_info = cp_info['publicIpInfo']
                if 'relatedOutputId' in pub_info.keys():
                    val = r_data['outputInfo'].get(pub_info['relatedOutputId'], {})\
                                         .get('value', None)
                    if val:
                        if isinstance(val, list):
                            pub_info['ipList'] = val
                        else:
                            pub_info['ipList'].append(val)
            sp_res = v['spInfo']
            for sp_info in sp_res.values():
                if 'relatedOutputId' in sp_info.keys():
                    val = r_data['outputInfo'].get(sp_info['relatedOutputId'], {})\
                                         .get('value', None)
                    if val:
                        sp_info['triggerUrl'] = val
                     
        print '#### VnfResDeployJob: slice resource deployment completes, and the resource context updated with slice resource id: ' + self.slice_res_id
        print yaml_dump(slice_res_ctx, default_flow_style=False)

        ctx_h.process_finish()
    
