#   The class of the job unit

from common.util import get_class_func_name
from event_listener import EXPIRE_ONCE


__author__ = 'chenxin'    
__date__ = '2017-4-8'  
__version__ = 1.0

STATUS_PROCESSING = 'job processing'
STATUS_COMPELET = 'job complete'
STATUS_FAIL = 'job fail'
STATUS_ABORT = 'job abort'


class JobUnit(object):
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        self.task_unit = task_unit
        self.job_name = job_n
        self.job_status = STATUS_PROCESSING
        self.job_finish_info = 'normal'

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        pass
    
    def _set_job_status(self, job_st):

        '''
        set the job status

        '''
        self.job_status = job_st
    
    def _set_job_finish_info(self, f_info):

        '''
        set the job info when job finishes

        '''
        self.job_finish_info = f_info
    
    def get_job_status(self):

        '''
        get the job status

        '''
        return self.job_status
    
    def get_job_finish_info(self):

        '''
        get the job info when job finishes

        '''
        return self.job_finish_info
    
    def _execution_finish(self, job_st=STATUS_COMPELET, f_info='normal'):

        '''
        job unit should always call this function whenever the execution finishes

        '''
        self._set_job_status(job_st)
        self._set_job_finish_info(f_info)
        self.task_unit.on_job_finishing(self)

    def _execution_exception(self, e_type, e_info):

        '''
        job unit should always call this function whenever a exception occurs during the execution
        parameters:
            e_type: exception type
            e_info: exception info

        '''
        self._execution_finish(STATUS_FAIL, 'job exception, ' + str(e_type) + ':' + str(e_info))

    def _sequence_abort(self, a_info):

        '''
        job unit should always call this function when the job want to abort the whole sequence
        parameters:
            a_info: reason to abort

        '''
        self._execution_finish(STATUS_ABORT, str(a_info))
    
    def _output_params(self, **params):

        '''
        call this method to ouput parameters to the task unit
        params:
            params: the the added parameters shoud be input as 'para_name=para_value'
        '''
        self.task_unit.add_output_params(self.job_name, **params)
    
    def _event_listener_register(self, event_type, 
                                       target_e_data, 
                                       target_keys_list,
                                       target_e_meta, 
                                       target_e_meta_keys,
                                       process_handler=None, 
                                       process_params={}, 
                                       job_unit_sequence=None, 
                                       expire=EXPIRE_ONCE, 
                                       timeout_handler=None, 
                                       timeout=None):
        '''
        the method used to register a event listener,
        called by job unit.
        params:
            event_type: event type of the registered
            target_e_data: target event data used to construct event matcher
            target_keys_list: target keys list to construct event matcher
            target_e_meta: target event meta used to construct event matcher
            target_e_meta_keys: target meta keys list to construct event matcher
            process_handler: the handler used to process the event when this listener is matched
            process_params: a dict contained the params the 'p_handler' method used
            job_unit_sequence: the job unit sequence used when the listened event trigger a task creationg
            expire: the expire value for the listener
            timeout_handler: the callback method called when the event listener timeout
            timeout: the timeout value for the listener
        '''
        try:
            if not process_handler and not job_unit_sequence:
                raise Exception('either a job unit sequence or a processing handler is required')
            self.task_unit.event_listener_register(event_type, 
                                                   target_e_data, 
                                                   target_keys_list,
                                                   target_e_meta, 
                                                   target_e_meta_keys,
                                                   process_handler, 
                                                   process_params, 
                                                   job_unit_sequence, 
                                                   expire, 
                                                   timeout_handler, 
                                                   timeout)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self._execution_exception(Exception, e)
