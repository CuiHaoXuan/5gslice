#   The class of the clear test data job unit


from common.util import get_class_func_name
from event_framework.job_unit import JobUnit


__author__ = 'chenxin'    
__date__ = '2017-4-10'  
__version__ = 1.0



class ClearTestDataJob(JobUnit):
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(ClearTestDataJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        try:
            event = self.task_unit.get_triggered_event()
            ctx_store = self.task_unit.task_scheduler.context_store
            #print 'getting the namespaces in context store'
            ns_list = ctx_store.get_all_context_namespaces()
            #print 'got the namespaces in context store: %s', ns_list
            for ns in ns_list:
                #print 'getting the item id list under %s' % ns
                item_ids = ctx_store.get_context_item_ids(ns)
                #print 'the context item id list under %s is %s' % (ns, item_ids) 
                for i in item_ids:
                    ctx_store.del_context_item(ns, i)
            #print 'finish the context clearing'
            event.set_return_data_asyn({'status': 'success'})
            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
