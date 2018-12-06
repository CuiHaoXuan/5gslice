#   The class of the add test data job unit


from common.util import get_class_func_name
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-10'  
__version__ = 1.0



class AddTestDataJob(JobUnit):
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(AddTestDataJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        try:
            print 'add test data job'
            print 'get input %s: %s' % (params.keys()[0], params[params.keys()[0]])
            print 'get input %s: %s' % (params.keys()[1], params[params.keys()[1]])
            self._register_event_listener()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)

    def _register_event_listener(self):
        
        '''
        setup a event listener processing the event that adding a test data
        the event attributes are:
            event type: 'add_test_data_event'
            event producer: 'test_data_producer'
            key event data:
                'context_namespace': 'test data'
        this event will be handled by the '_add_test_data' method
        '''
        t_event_producer = self.task_unit.task_scheduler.get_event_producer('test_data_producer')
        t_event_t = self.task_unit.task_scheduler.get_event_type('add_test_data_event')
        t_e_data = {'context_namespace': 'test data'}
        t_keys_list = ['context_namespace']
        t_e_meta = {META_EVENT_TYPE: t_event_t, META_EVENT_PRODUCER: t_event_producer}
        t_e_meta_keys = [META_EVENT_TYPE, META_EVENT_PRODUCER]

        self._event_listener_register(t_event_t, 
                                      t_e_data, 
                                      t_keys_list,
                                      t_e_meta, 
                                      t_e_meta_keys,
                                      process_handler=self._add_test_data)
    
    def _add_test_data(self, **params):

        '''
        add a test data to the context store

        '''
        event = params['event']
        ctx_ns = event.get_event_data()['context_namespace']
        t_data = event.get_event_data()['data']
        ctx_store = self.task_unit.task_scheduler.context_store
        item_id = self.task_unit.task_scheduler.global_id_generator\
                                               .get_context_item_id_without_env([ctx_ns, str(t_data)])
        ctx_store.add_context_item(t_data, ctx_ns, item_id, 'test_data_item_id')
        event.set_return_data_syn({'status': 'success'})
        self._execution_finish()
