#   The class of the task scheduler


from threading import Lock as lock
import threadpool

from common.util import get_class_func_name, TASK_THREADPOOL_SIZE, TASK_SHARED_THREADPOOL_SIZE
from event_matcher import EventMatcher
from event_listener import EventListener, EXPIRE_NEVER, EXPIRE_ONCE
from event_generator import EventGenerator
from global_id_generator import GlobalIdGenerator
from task_unit import TaskUnit


__author__ = 'chenxin'    
__date__ = '2017-3-31'  
__version__ = 1.0

INIT_TYPE_METHOD = 'INIT_TYPE_METHOD'
INIT_TYPE_SEQ = 'INIT_TYPE_SEQ'

class TaskScheduler(object):
    
    def __init__(self, conf_ctx, 
                       ctx_store, 
                       init_type=INIT_TYPE_METHOD,
                       init_job_seq=None, 
                       event_listener_list_syn=True, 
                       other_info={}):
        
        '''
        shcedule the task according to the events,
        providing event listener registry interface, 
        and maintaining the event generator, the event listener list, 
        the global id generator and the context store
        params:
            ctx_store: the context store current task scheduler using
            conf_ctx: a context containing the configure data for this task scheduler, consists of:
                'job_unit_sequences':
                    (job_unit_sequence_name): job_unit_sequence
                'processed_event_types':
                    (event_type_name): event type description
                'global_event_producers':
                    (event_producer_name): event producer description
            init_type: indicating how to initiate this task scheduler,
                       by using a initiating job unit sequence or the initiating method
            event_listener_list_syn: indicating whether the event listener list need to by multi-thread protected
            other_info: the other info given in the configure file injected by the configurer
        '''
        self.event_listener_list = [] # event listener list
        self.event_listener_list_mutex = None
        if event_listener_list_syn:
            self.event_listener_list_mutex = lock() # the mutex for event listener list operations

        self.context_store = ctx_store # context store
        self.global_id_generator = GlobalIdGenerator() # global id generator
        self.event_generator = EventGenerator(self.event_listener_list,
                                              self.event_listener_list_mutex, 
                                              self.global_id_generator) # event generator

        
        self.config_context = conf_ctx

        self.task_thread_pool = threadpool.ThreadPool(TASK_THREADPOOL_SIZE)
        self.task_thread_pool_mutex = lock()

        self.task_shared_thread_pool = threadpool.ThreadPool(TASK_SHARED_THREADPOOL_SIZE)
        self.task_shared_thread_pool_mutex = lock()
        
        self.init_job_unit_sequence = init_job_seq

        self.other_info = other_info

        self._init(init_type)

    def _start_new_task(self, job_unit_seq, event=None):
        # tp = threadpool.ThreadPool(THREADPOOL_SIZE)
        TaskUnit(self, job_unit_seq, event, \
                                 self.task_shared_thread_pool, \
                                 self.task_shared_thread_pool_mutex).start_process()
    
    def _process_event_by_task(self, **params):
        
        '''
        process event by creating a new task or invoking an old task
        the params dict should at least contain:
            'event': the triggered event
            'listener': the matched event listener
        either of the following key/values should be containted:
            'job_unit_sequence': the job unit sequence, new task will be created when this is contained
            'task_unit': the relevent task unit object, the object's 'continue_process' method will be called
        
        '''
        try:
            event = params['event']
            listener = params['listener']
            mutex = self.task_thread_pool_mutex
            if listener.expire == 1:
                self._remove_event_listener(listener)
            if 'job_unit_sequence' in params.keys():
                seq = params['job_unit_sequence']
                if mutex.acquire():
                    req = threadpool.makeRequests(self._start_new_task, [([seq, event], None)])
                    self.task_thread_pool.putRequest(req[0])
                    mutex.release()
            elif 'task_unit' in params.keys():
                if mutex.acquire():
                    req = threadpool.makeRequests(params['task_unit'].continue_process, [([event, listener], None)])
                    self.task_thread_pool.putRequest(req[0])
                    mutex.release()
            else:
                raise Exception('Either a job unit sequence for new task or a task object to continue is required')
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
    
    
    def task_event_listener_register(self, event_type, 
                                      target_e_data, 
                                      target_keys_list,
                                      target_e_meta, 
                                      target_e_meta_keys,
                                      process_params={},
                                      job_unit_sequence=None, 
                                      task_unit=None, 
                                      expire=EXPIRE_NEVER, 
                                      timeout_handler=None, 
                                      timeout=None):
        '''
        the method used to register a event listener by a task unit.
        params:
            event_type: event type of the registered
            target_e_data: target event data used to construct event matcher
            target_keys_list: target keys list to construct event matcher
            target_e_meta: target event meta used to construct event matcher
            target_e_meta_keys: target meta keys list to construct event matcher
            process_params: a dict contained the params the 'process_event' method used
            job_unit_sequence: the job unit sequence used when the listened event trigger a task creationg
            task_unit: the task unit to be awaked when the listend event trigger a continuing process of a task
            expire: the expire value for the listener
            timeout_handler: the callback method called when the event listener timeout
            timeout: the timeout value for the listener
        return:
            global event listener id
        '''
        ext_params = {}
        try:
            if job_unit_sequence:
                ext_params['job_unit_sequence'] = job_unit_sequence
            elif task_unit:
                ext_params['task_unit'] = task_unit
            else:
                raise Exception('either a job unit sequence for new task or a task object to continue is required')
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        ext_params.update(process_params)
        return self._event_listener_register(event_type, 
                                             target_e_data, 
                                             target_keys_list,
                                             target_e_meta, 
                                             target_e_meta_keys, 
                                             self._process_event_by_task, 
                                             ext_params, 
                                             expire, 
                                             timeout_handler, 
                                             timeout)

    def _event_listener_register(self, event_type, 
                                      target_e_data, 
                                      target_keys_list,
                                      target_e_meta, 
                                      target_e_meta_keys,
                                      process_handler, 
                                      process_params={}, 
                                      expire=EXPIRE_NEVER, 
                                      timeout_handler=None, 
                                      timeout=None):
        '''
        the method used to register a event listener,
        called by the scheduler itself.
        params:
            event_type: event type of the registered
            target_e_data: target event data used to construct event matcher
            target_keys_list: target keys list to construct event matcher
            target_e_meta: target event meta used to construct event matcher
            target_e_meta_keys: target meta keys list to construct event matcher
            process_handler: handle the event when the listener is matched
            process_params: a dict contained the params the 'process_event' method used
            job_unit_sequence: the job unit sequence used when the listened event trigger a task creationg
            task_unit: the task unit to be awaked when the listend event trigger a continuing process of a task
            expire: the expire value for the listener
            timeout_handler: the callback method called when the event listener timeout
            timeout: the timeout value for the listener
        return:
            global event listener id
        '''
        matcher = EventMatcher(target_e_data, target_keys_list, target_e_meta, target_e_meta_keys)
        listener_id = self.global_id_generator.get_event_listener_id(event_type, str(target_e_data), str(target_e_meta))
        listener = EventListener(listener_id, event_type, matcher, expire, timeout)
        listener.set_match_handler(process_handler, **process_params)
        #listener.start_timer()
        self._add_event_listener(listener)
        # for debug
        print '#### TaskScheduler: add a event listener with type: %s, and target data: %s' % (event_type, target_e_data)
        return listener_id
    
    def _init(self, init_t):

        '''
        init the task scheduler according to the initiation type,
        i.e. init with a init job unit sequence or the logics in this method
        params:
            init_t: init type for this task scheduler
        '''
        try:
            if init_t == INIT_TYPE_SEQ:
                if not self.init_job_unit_sequence:
                    raise Exception('init job unit sequence is required')
                seq = self.init_job_unit_sequence
                self._start_new_task(seq)
            elif init_t == INIT_TYPE_METHOD:
                self._init_method()
            else:
                raise Exception('unknown task scheduler init type')
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
    
    def _init_method(self):

        '''
        init method called when the init type is INIT_TYPE_METHOD.
        derived task scheduler classes could override this method,
        initiation like static event listener registry, pre-defined
        context creation could be done in this method
        
        '''
        pass
    
    def _add_event_listener(self, listener):
        
        '''
        add the event listener to the listener list

        '''
        try:
            mutex = self.event_listener_list_mutex
            def list_access(): 
                if mutex:
                    if mutex.acquire():
                        return True
                else:
                    return True
            def access_finish():
                if mutex:
                    mutex.release()
            if list_access():   
                try:
                    self.event_listener_list.append(listener)
                except Exception, e:
                    print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
                    access_finish()
                else:
                    access_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)

    def _remove_event_listener(self, listener):
        
        '''
        remove the event listener from the listener list

        '''
        try:
            mutex = self.event_listener_list_mutex
            def list_access(): 
                if mutex:
                    if mutex.acquire():
                        return True
                else:
                    return True
            def access_finish():
                if mutex:
                    mutex.release()
            if list_access():   
                try:
                    i = self.event_listener_list.index(listener)
                    self.event_listener_list.pop(i)
                except Exception, e:
                    print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
                    access_finish()
                else:
                    access_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)

    
    def get_job_unit_sequence(self, seq_name):
        return self.config_context['job_unit_sequences'].get(seq_name, None)

    def get_event_type(self, type_name):
        return self.config_context['processed_event_types'].get(type_name, None)

    def get_event_producer(self, producer_name):
        return self.config_context['global_event_producers'].get(producer_name, None)
