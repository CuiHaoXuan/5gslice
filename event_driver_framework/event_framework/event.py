#   The class of the event

from threading import Lock as lock, Timer

from common.util import get_class_func_name
from event_trigger import EventTrigger


__author__ = 'chenxin'    
__date__ = '2017-3-30'  
__version__ = 1.0

NO_RETURN = {'error': 'no return data'}

# the meta keys and their values will be added into each event's data automatically
META_EVENT_ID = 'event_id'
META_EVENT_TYPE = 'event_type'
META_EVENT_PRODUCER = 'event_producer'


TIMEOUT = 60

class EventClass(object):
    
    def __init__(self, e_id, e_type, e_producer,
                       e_listener_list,
                       e_listener_list_mutex,
                       thread_pool,
                       e_data={}):
        '''
        params:
            e_id: event id
            e_type: event type
            e_producer: event producer
            e_listener_list: event listener list
            e_listener_list_mutex: event listener list mutex
            thread_pool: thread pool for event triggering
            e_data: data of event, e.g. rest api name and post data
        '''
        self.id = e_id
        self.type = e_type
        self.producer = e_producer
        self.meta = {'event_id': self.id,\
                     'event_type': self.type,\
                     'event_producer': self.producer}
        self.data = e_data
        self.trigger = EventTrigger(self, e_listener_list, e_listener_list_mutex, thread_pool)
        self.return_flag = False
        self.return_data = None
        self.return_data_mutex = lock()

    def trigger_event(self):
        
        '''
        trigger the current event via event listener
        
        '''
        self.trigger.trigger()
        while not self.return_flag:
            pass
        mutex = self.return_data_mutex
        if mutex.acquire():
            r_data = self.return_data
            mutex.release()
        return r_data

    def get_event_data(self):
        return self.data
    
    def get_event_meta(self):
        return self.meta
    
    def set_return_data_asyn(self, r_data):
        self.return_flag = True
        self.return_data = r_data

    def set_return_data_syn(self, r_data):
        mutex = self.return_data_mutex
        if mutex.acquire():
            self.return_flag = True
            self.return_data = r_data
            mutex.release()
            
