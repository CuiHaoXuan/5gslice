#   The class of the slice instantiation plan executing job unit


import os
from collections import OrderedDict
import urllib2

from common.util import get_class_func_name, cata_download, del_dir_or_file, \
                            CONTEXT_NAMESPACE_SLICE, \
                            COMPONENT_NAME_PLAN_ENGINE, SERVICE_SLICE_INSTAN_PLAN_EXEC
from common.yaml_util import yaml_ordered_load as yaml_load, yaml_ordered_dump as yaml_dump
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-6-19'  
__version__ = 1.0



class SliceInstanPlanExecJob(JobUnit):
    
    '''
    this job is used to execute the registered instantiation plan.
    this job get inputs:
        slice_id:
    the works done by this job are:
        call the plan execution service to exec the registered instantiation plan

    '''
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(SliceInstanPlanExecJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        
        try:
            slice_id = params['slice_id']
            
            ctx_store = self.task_unit.task_scheduler.context_store
            ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE, slice_id)
            slice_ctx = ctx_h.get_context_item()
            ns_combo_id = slice_ctx['nsComboId']
            instan_plan_process_id = slice_ctx['planInfo']['instanPlan']['rtProcessId']
            req_data = {}
            req_data['processDefinitionId'] = instan_plan_process_id
            req_data['task_id'] = ns_combo_id
            self.task_unit.task_scheduler.\
                         req_remote_serv(COMPONENT_NAME_PLAN_ENGINE, SERVICE_SLICE_INSTAN_PLAN_EXEC, req_data)
            ctx_h.process_finish()

            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self._execution_exception(Exception, e) 
