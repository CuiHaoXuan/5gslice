#   The class of the context process handler


__author__ = 'chenxin'    
__date__ = '2017-4-1'  
__version__ = 1.0


class ContextProcessHandler(object):
    
    
    def __init__(self, ctx_item, mutex, store_if):
        '''
        a handler used to process the context item in the context store
        params:
            ctx_item: the context item to be handled
            mutex: the mutex of the processed context item
            store_if: a interface used to store the context changes persistently

        '''
        self.context_item = ctx_item 
        self.mutex = mutex
        self.persistent_store = store_if
        if mutex:
            self.mutex.acquire()

    def get_context_item(self):        
        return self.context_item

    def process_finish(self, store_flag=False):

        '''
        interface called to notify the finish of the process
        each handler user should call this interface
        after finishing the context item processing
        params:
            store_flag: indicating whether store the context item changes persistenly

        '''
        if store_flag:
            self.persistent_store()
        if self.mutex:
            self.mutex.release()