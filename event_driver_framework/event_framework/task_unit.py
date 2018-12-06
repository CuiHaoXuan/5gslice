#   The class of the task unit


import threadpool
from threading import Lock as lock

from common.util import get_class_func_name
from event_listener import EXPIRE_ONCE
from job_unit import JobUnit, STATUS_FAIL


__author__ = 'chenxin'    
__date__ = '2017-4-6'  
__version__ = 1.0


THREADPOOL_SIZE = 5



class TaskUnit(object):
    
    def __init__(self, task_sch, job_unit_seq, event=None, thread_pool=None, thread_pool_mutex=None, **params):
        
        '''
        task unit responding to execute a job unit sequence
        params:
            task_sch: the task scheduler instance this task unit belongs to
            job_unit_seq: job unit sequence for this task unit
            event: the event trigger the creation of this task unit
            thread_pool: the thread pool for the task unit to execute jobs
            thread_pool_mutex: the mutex for the tread pool
            params: other parameters may used for extension
        '''
        self.task_scheduler = task_sch
        self.origin_job_unit_sequence = job_unit_seq
        self.remain_job_unit_name_sequence = job_unit_seq.get_copy_job_unit_name_sequence()
        self.remain_params_mapping_sequence = job_unit_seq.get_copy_param_mapping_sequence()
        self.triggered_event = event
        
        self.thread_pool = thread_pool
        self.thread_pool_mutex = thread_pool_mutex
        if not thread_pool:
            self.thread_pool = threadpool.ThreadPool(THREADPOOL_SIZE)
        if not thread_pool_mutex:
            self.thread_pool_mutex = lock()

        self.event_listener_info = {}
        self.event_listener_info_mutex = lock()

        self.current_job_unit_list = [] # the job unit instance list of current phase
        self.current_job_unit_list_mutex = lock()

        self.output_params = {}
        '''
        a dict to store the parameters output by the job unit
        the dict consists with:
            phase:
                job_name:
                    para_name:
        '''
        self.output_params_mutex = lock()

    def _update_current_phase(self):

        '''
        update the remain sequence by pop the heads of the remain job unit name sequence, 
        and the remain mapping parameters, and set the heads to the current phase to process.
        this method is called at the begining of each job unit sequence phase

        '''
        self.current_job_units = self.remain_job_unit_name_sequence.pop(0)
        self.current_param_mappings = self.remain_params_mapping_sequence.pop(0)
        self.current_phase = self.current_job_units['phase']
        self.output_params[self.current_phase] = {}
    
    def _get_current_input_params(self, job_name):

        '''
        get the input parameters for a job unit of current phase
        according to the parameter mappings of current phase

        '''
        try:
            params = {}
            mappings = self.current_param_mappings['mappings'].get(job_name, None)
            if not mappings:
                return params
            for para_name, v in mappings.items():
                para_value = self.output_params[v['phase']]\
                                               [v['jobUnit']]\
                                               [v['para']]
                params[para_name] = para_value
            return params
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
    
    def _process_current_phase(self):

        '''
        process the job units of current phase, using the relevent mapping parameters

        '''
        try:
            if len(self.current_job_unit_list) > 0:
                raise Exception('The last phase has not finished')
            tp = self.thread_pool
            reqs = []
            for n in self.current_job_units['jobUnits']:
                job_unit_cls = self.origin_job_unit_sequence.get_job_unit_class(n)
                job_unit = job_unit_cls(self, n)
                self.current_job_unit_list.append(job_unit)
                inputs = self._get_current_input_params(n)
                reqs = reqs + threadpool.makeRequests(job_unit.execute_job, [(None, inputs)])
            map(tp.putRequest, reqs)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
    
    def _phase_shift(self):
        
        if len(self.remain_job_unit_name_sequence) > 0:
            self._update_current_phase()
            self._process_current_phase()
        else:
            pass
    
    def get_triggered_event(self):
        return self.triggered_event
    
    def add_output_params(self, job_n, **params):

        '''
        called by the job unit instance to add output parameters
        params:
            job_n: the job unit name
            params: the added parameters shoud be input as 'para_name=para_value'
        '''
        try:
            mutex = self.output_params_mutex
            if mutex.acquire():
                loac = self.output_params[self.current_phase]
                if job_n not in loac.keys():
                    loac[job_n] = {}
                loac = loac[job_n]
                for n, v in params.items():
                    loac[n] = v
                mutex.release()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            mutex.release()
    
    def start_process(self):
        
        '''
        start to process the job unit sequence
        this method is always called by the 'process_event' method in task scheduler
        when a event comes
        
        '''
        try:
            mutex = self.thread_pool_mutex
            tp = self.thread_pool
            while len(self.remain_job_unit_name_sequence) > 0:
                if mutex.acquire():
                    tp.wait()
                    if len(self.current_job_unit_list) == 0:
                        self._phase_shift()
                    mutex.release()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)

    def continue_process(self, event, listener):

        '''
        this method is called when the task is invoked by the task scheduler
        params:
            event: the event triggering the invoking of the task
            listener: the event listener matched by the event

        '''
        
        try:
            l_id = listener.get_listener_id()
            mutex = self.event_listener_info_mutex
            if mutex.acquire():
                l_info = self.event_listener_info[l_id]
                if l_info['expire'] == 1:
                    self.event_listener_info.pop(l_id)
                mutex.release()
            tp = self.thread_pool
            ext_params = {'event': event}
            ext_params.update(l_info['params'])
            mutex = self.thread_pool_mutex
            if mutex.acquire():
                req = threadpool.makeRequests(l_info['handler'], [(None, ext_params)])
                tp.putRequest(req[0])
                mutex.release()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            mutex.release()
    
    def event_listener_register(self, e_type, 
                                      t_e_data, 
                                      t_keys_list,
                                      t_e_meta, 
                                      t_e_meta_keys, 
                                      p_handler=None, 
                                      p_params={}, 
                                      job_unit_seq=None, 
                                      expi=EXPIRE_ONCE, 
                                      timeout_h=None, 
                                      timeout=None):
        '''
        the method used to register a event listener,
        called by job unit.
        params:
            e_type: event type of the registered
            t_e_data: target event data used to construct event matcher
            t_keys_list: target keys list to construct event matcher
            t_e_meta: target event meta used to construct event matcher
            t_e_meta_keys: target meta keys list to construct event matcher
            p_handler: the handler used to process the event when this listener is matched
            p_params: a dict contained the params the 'p_handler' method used
            job_unit_seq: the job unit sequence used when the listened event trigger a task creationg
            expi: the expire value for the listener
            timeout_h: the callback method called when the event listener timeout
            timeout: the timeout value for the listener
        '''
        try:
            if not job_unit_seq:
                if not p_handler:
                    raise Exception('either a job unit sequence or a processing handler is required') 
                listener_id = self.task_scheduler.task_event_listener_register(e_type, 
                                                                               t_e_data, 
                                                                               t_keys_list,
                                                                               t_e_meta, 
                                                                               t_e_meta_keys,
                                                                               p_params,
                                                                               None, 
                                                                               self, 
                                                                               expi, 
                                                                               timeout_h, 
                                                                               timeout)
            else:
                listener_id = self.task_scheduler.task_event_listener_register(e_type, 
                                                                               t_e_data, 
                                                                               t_keys_list,
                                                                               t_e_meta, 
                                                                               t_e_meta_keys,
                                                                               p_params,
                                                                               job_unit_seq, 
                                                                               None, 
                                                                               expi, 
                                                                               timeout_h, 
                                                                               timeout)
            if p_handler:
                mutex = self.event_listener_info_mutex
                if mutex.acquire():
                    new_info = {listener_id: {'handler': p_handler, 'expire': expi, 'params': p_params}}
                    self.event_listener_info.update(new_info)
                    mutex.release()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
    
    def on_job_finishing(self, job_unit):

        '''
        called by the job unit when the job unit finish itself
        params:
            job_unit: the job unit instance
        '''
        try:
            mutex = self.current_job_unit_list_mutex
            if mutex.acquire():
                if job_unit.get_job_status() == STATUS_FAIL:
                    self.current_job_unit_list = []
                    raise Exception('job: %s fail due to %s, job sequence processing abort' % \
                                          (job_unit.job_name, job_unit.get_finish_info()))
                i = self.current_job_unit_list.index(job_unit)
                self.current_job_unit_list.pop(i)
                mutex.release()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            mutex.release()
