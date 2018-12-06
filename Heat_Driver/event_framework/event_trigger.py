#   The class of the event trigger

import threadpool

from common.util import get_class_func_name


__author__ = 'chenxin'    
__date__ = '2017-3-31'  
__version__ = 1.0


class EventTrigger(object):
    
    def __init__(self, event, e_listener_list, e_listener_list_mutex, thread_pool):
        
        '''
        A trigger to trigger the event processing
        params:
            event: event
            e_listener_list: event listener list
            e_listener_list_mutex: event listener list mutex
            thread_pool: the thread pool for event triggering
        '''
        self.event = event
        self.event_listener_list = e_listener_list
        self.event_listener_list_mutex = e_listener_list_mutex
        self.thread_pool = thread_pool

    def trigger(self):
        
        '''
        trigger the current event via event listener
        
        '''
        try:
            reqs = []
            mutex = self.event_listener_list_mutex
            tp = self.thread_pool
            def list_access(): 
                if mutex:
                    if mutex.acquire():
                        return True
                else:
                    return True
            def access_finish():
                if mutex:
                    mutex.release()

            match_list = []
            if list_access():   
                try:
                    for l in self.event_listener_list:
                        if l.match(self.event):
                            match_list.append(l)
                except Exception, e:
                    print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
                    access_finish()
                else:
                    access_finish()
                    for l in match_list:
                        reqs = reqs + threadpool.makeRequests(l.process_event, [(None, None)])
                    map(tp.putRequest, reqs)
                    #tp.wait()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
