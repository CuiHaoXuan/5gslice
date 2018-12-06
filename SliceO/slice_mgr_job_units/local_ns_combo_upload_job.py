#   The class of the local ns combo upload job unit


import os
import time
from collections import OrderedDict

from common.util import get_class_func_name, CONTEXT_NAMESPACE_NS_COMBO, \
                        unpack, del_dir_or_file
from common.yaml_util import yaml_ordered_load as yaml_load
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-6-1'  
__version__ = 1.0


class LocalNsComboUploadJob(JobUnit):
    
    '''
    this job is used to upload the ns combo pack and generate the ns combo context.
    the works done by this job are:
        unpack the ns combo pack
        read the meta data from the unpack ns combo files
        call the csar upload service to upload the csars of each subslice
        generate and store the ns combo context
    '''
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(LocalNsComboUploadJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        try:
            self.event = self.task_unit.get_triggered_event()
            self._alloc_ns_combo_id()
            r_data = {'status': 'request accepted', 'allocNsComboId': self.ns_combo_id}
            self.event.set_return_data_syn(r_data)
            pack_local_path = self.event.get_event_data().get('packLocalPath', None)
            self.unpack_dir = unpack(pack_local_path)
            self._read_ns_combo_meta()
            self._store_ns_combo_context()
            self._upload_csars()
            time.sleep(3) # waiting for the csar uploadings
            del_dir_or_file(self.unpack_dir)
            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self._execution_exception(Exception, e)

    def _alloc_ns_combo_id(self):
        
        '''
        allocate the ns combo id according to the ns combo pack name, tenant id and the trade id

        '''
        event_d = self.event.get_event_data()
        id_gen = self.task_unit.task_scheduler.global_id_generator
        self.ns_combo_id = id_gen.get_context_item_id_without_env(event_d['nsComboPackName'], 
                                                  event_d['tenantId'], 
                                                  event_d['tradeId'])
    

    def _read_ns_combo_meta(self):

        '''
        read the ns combo meta data

        '''
        f = file(os.path.join(self.unpack_dir, 'metadata.yaml'), 'r')
        self.meta = yaml_load(f)
        self.sub_slice_csar_pack_info = self.meta.pop('subNsCsarInfo')
        f.close()

    def _store_ns_combo_context(self):

        '''
        store the ns combo context to the context store,
        the ns combo context consists of:
            flavorInfo:
                ...
            subscriberInfo:
                ...
            slaInfo:
                ...
            locationInfo:
                ...
            topologyInfo:
                ...
            policies:
                ...
            subSliceInfo:
                (subNsNodeId):
                    relatedCsarId:
                    relatedSubSliceId:

        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        ns_combo_ctx = OrderedDict()
        ns_combo_ctx.update(self.meta)
        loc = ns_combo_ctx.setdefault('subSliceInfo', OrderedDict())
        for k in self.sub_slice_csar_pack_info.keys():
            loc[k] = OrderedDict()
        ctx_store.add_context_item(ns_combo_ctx, CONTEXT_NAMESPACE_NS_COMBO,
                                   self.ns_combo_id, item_id_n='nsComboId')

    def _upload_csars(self):

        '''
        upload the csar pack of each sub slice to the catalogue, 
        update the sub slice csar info of the ns combo context 

        '''
        event_d = self.event.get_event_data()
        sch = self.task_unit.task_scheduler
        ctx_store = sch.context_store
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_NS_COMBO, self.ns_combo_id)
        ctx_sub_slice = ctx_h.get_context_item()['subSliceInfo'] 
        for k, v in self.sub_slice_csar_pack_info.items():
	    print "v is "
	    print v
            ctx_sub_slice[k]['relatedCsarId'] = \
                          sch.req_csar_upload_serv(v['csarPackName'], self.ns_combo_id, k, event_d['tenantId'], 
                                                   event_d['tradeId'], 'csar of ' + k, 
                                                   os.path.join(self.unpack_dir, v['csarPackName'])).get('allocCsarId', None)
	    print ctx_sub_slice[k]['relatedCsarId']
	print "hello in upload finish"
        ctx_h.process_finish()
        
