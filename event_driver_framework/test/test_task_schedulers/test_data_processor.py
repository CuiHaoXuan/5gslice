#   The class of the test data processor task scheduler


from common.util import get_class_func_name
from event_framework.task_scheduler import TaskScheduler
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-9'  
__version__ = 1.0


class TestDataProcessorScheduler(TaskScheduler):
    
    def __init__(self, conf_ctx, 
                       ctx_store, 
                       init_type='INIT_TYPE_METHOD',
                       init_job_seq=None, 
                       event_listener_list_syn=True):
        
        super(TestDataProcessorScheduler, self).__init__(conf_ctx, 
                                                         ctx_store, 
                                                         init_type,
                                                         init_job_seq, 
                                                         event_listener_list_syn)
    
    def _init_method(self):

        '''
        init method called when the init type is INIT_TYPE_METHOD.
        derived task scheduler classes could override this method,
        initiation like static event listener registry, pre-defined
        context creation could be done in this method
        
        '''
        # insert 2 test data items into the context store
        t_data = [{'name': 'test data item 1', 'data': 'hello'}, \
                  {'name': 'test data item 2', 'data': 'world'}]
        ctx_ns = ['test data', 'test data']
        item_id = map(self.global_id_generator.get_context_item_id_without_env, zip(ctx_ns, t_data))
        item_id_n = ['test_data_item_id', 'test_data_item_id']
        map(self.context_store.add_context_item, t_data, ctx_ns, item_id, item_id_n)

        '''
        setup a event listener processing the event that getting all the test data items
        the event attributes are:
            event type: 'get_test_data_event'
            event producer: 'test_data_consumer'
            key event data:
                'context_namespace': 'test data'
        the processing task unit will use the job unit sequence of 'process_test_data_seq'
        '''
        e_type = self.get_event_type('get_test_data_event')
        e_producer = self.get_event_producer('test_data_consumer')
        t_e_data = {'context_namespace': 'test data'}
        t_keys_list = ['context_namespace']
        t_e_meta = {META_EVENT_TYPE: e_type, META_EVENT_PRODUCER: e_producer}
        t_meta_keys = [META_EVENT_TYPE, META_EVENT_PRODUCER]
        job_seq = self.get_job_unit_sequence('process_test_data_seq')
        self.task_event_listener_register(event_type=e_type, 
                                          target_e_data=t_e_data, 
                                          target_keys_list=t_keys_list,
                                          target_e_meta=t_e_meta, 
                                          target_e_meta_keys=t_meta_keys,
                                          job_unit_sequence=job_seq)

        '''
        setup a event listener processing the event that clearing all the test data items
        the event attributes are:
            event type: 'clear_test_data_event'
            event producer: 'test_data_producer'
            key event data:
        the processing task unit will use the job unit sequence of 'clear_test_data_seq'
        '''
        e_type = self.get_event_type('clear_test_data_event')
        e_producer = self.get_event_producer('test_data_producer')
        t_e_data = {}
        t_keys_list = []
        t_e_meta = {META_EVENT_TYPE: e_type, META_EVENT_PRODUCER: e_producer}
        t_meta_keys = [META_EVENT_TYPE, META_EVENT_PRODUCER]
        job_seq = self.get_job_unit_sequence('clear_test_data_seq')
        self.task_event_listener_register(event_type=e_type, 
                                          target_e_data=t_e_data, 
                                          target_keys_list=t_keys_list,
                                          target_e_meta=t_e_meta, 
                                          target_e_meta_keys=t_meta_keys,
                                          job_unit_sequence=job_seq)
