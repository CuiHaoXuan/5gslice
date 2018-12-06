#   The class of the local csar upload request accept job unit


import os

from common.util import get_class_func_name
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-14'  
__version__ = 1.0



class LocalCsarUploadAcceptJob(JobUnit):
    
    '''
    this job is used to accept a local csar upload request.
    the works done by this job are:
        allocate the csar id
        allocate the upload dir
        return the csar id and the upload dir
    this job output parameters as follows:
        csar_id: csar id
        csar_upload_dir: the target upload dir of the csar
    '''
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(LocalCsarUploadAcceptJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        try:
            self.event = self.task_unit.get_triggered_event()
            self._alloc_csar_id()
            self._alloc_csar_upload_dir()
            r_data = {'status': 'request accepted', 'csarUploadDir': self.csar_upload_dir, 'allocCsarId': self.csar_id}
	    print r_data
            out_para = {'csar_upload_dir': self.csar_upload_dir}
            out_para.update({'csar_id': self.csar_id})
            self.event.set_return_data_syn(r_data)
            self._output_params(**out_para)
            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self.event.set_return_data_asyn({'status': 'request failed'})
            self._execution_exception(Exception, e)

    def _alloc_csar_id(self):
        
        '''
        allocate the csar id according to the csar name, tenant id and the trade id

        '''
        event_d = self.event.get_event_data()
        id_gen = self.task_unit.task_scheduler.global_id_generator
        self.csar_id = id_gen.get_context_item_id_without_env(event_d['csarName'], 
                                                  event_d['tenantId'], 
                                                  event_d['tradeId'])
    
    def _alloc_csar_upload_dir(self):
        
        '''
        allocate the csar upload dir in the catalogue

        '''
        csar_parent_d = self.task_unit.task_scheduler.get_catalogue_serv_dir()\
                                                     .get('csarPacks', '')
        self.csar_upload_dir = os.path.join(csar_parent_d, self.csar_id, 
                                           self.event.get_event_data()['csarName'].replace('.tar.gz', ''), '')
