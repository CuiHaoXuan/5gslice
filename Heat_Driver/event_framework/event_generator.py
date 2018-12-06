#   The class of the event generator

import threadpool

from common.util import get_class_func_name
from event import EventClass



__author__ = 'chenxin'    
__date__ = '2017-3-31'  
__version__ = 1.0

THREADPOOL_SIZE = 20

class EventGenerator(object):
    
    TEST_EVENT = 'test event type'
    
    def __init__(self, e_listener_list,
                       e_listener_list_mutex, 
                       id_generator):
        '''
        params:
            e_listener_list: event listener list
            e_listener_list_mutex: event listener list mutex
            id_generator: global identifier generator instance
        '''
        self.event_listener_list = e_listener_list
        self.event_listener_list_mutex = e_listener_list_mutex
        self.id_generator = id_generator
        self.thread_pool = threadpool.ThreadPool(THREADPOOL_SIZE)

    def get_event(self, event_type, event_producer, event_data={}):
        
        '''
        trigger the current event via event listener
        params:
            event_type: event type
            event_producer: event producer
            event_data: event data      
        '''
        try:
            event_id = self.id_generator.get_event_id(event_type, event_producer, event_data)
            return EventClass(event_id, event_type, event_producer, 
                              self.event_listener_list, 
                              self.event_listener_list_mutex,
                              self.thread_pool, 
                              event_data)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            return None