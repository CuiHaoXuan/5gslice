#   The class of the csar context generation job unit


import os
from collections import OrderedDict

from common.util import get_class_func_name, CONTEXT_NAMESPACE_CSAR, \
                        unpack, cata_upload, del_dir_or_file, \
                        CSAR_STATUS_UPLOADING, CSAR_STATUS_UPLOADED
from common.yaml_util import yaml_ordered_load as yaml_load
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-14'  
__version__ = 1.0


class CsarContextGenerateJob(JobUnit):
    
    '''
    this job is used to generate and store csar context.
    this job get inputs as follows:
        'csar_id': the csar id
        'csar_upload_dir': the upload dir of the csar
    the works done by this job are:
        unpack the csar pack
        read the meta data from the unpack csar files
        upload the csar files
        generate and store the csar context
    '''
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(CsarContextGenerateJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        try:
            self.event = self.task_unit.get_triggered_event()
            self.csar_id = params.get('csar_id', None)
            csar_local_path = self.event.get_event_data().get('csarLocalPath', None)
            self.unpack_csar_dir = unpack(csar_local_path)
            self.csar_upload_dir = params.get('csar_upload_dir', None)
            self._read_csar_meta()
            self._store_csar_context()
            self._upload_csar()
            del_dir_or_file(self.unpack_csar_dir)
            self._update_csar_context()
            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self._execution_exception(Exception, e)

    def _read_csar_meta(self):
        
        '''
        read the part of the csar meta data

        '''
        f = file(os.path.join(self.unpack_csar_dir, 'Metadata', 'metadata.yaml'), 'r')
        meta = yaml_load(f)
        self.meta_data = OrderedDict()
        self.meta_data.update(meta.get('nsFlavorInfo', None))
        loc = self.meta_data
        event_d = self.event.get_event_data()
        loc['nsComboId'], loc['subNsNodeId'] = event_d['nsComboId'], event_d['subNsNodeId']
        loc['tenantId'], loc['tradeId'] = event_d['tenantId'], event_d['tradeId']
        f.close()

    def _upload_csar(self):

        '''
        upload the unpack csar files to the catalogue

        '''
        sch = self.task_unit.task_scheduler
        ip_addr = sch.get_catalogue_serv_ip()
        t_port = sch.get_catalogue_serv_port()
        pro = sch.get_catalogue_serv_proto()
        usr = sch.get_catalogue_serv_username()
        passwd = sch.get_catalogue_serv_password()
	print 'ftp:' + self.unpack_csar_dir 
	print 'f:' + self.csar_upload_dir
        cata_upload(ip_addr, t_port, pro, usr, passwd, 
                             self.unpack_csar_dir, self.csar_upload_dir)
    
    def _store_csar_context(self):

        '''
        store the csar context to the context store,
        the csar context consists of:
            nsFlavorId: 
            nsTypeId: 
            version: 
            vendor: 
            description: 
            nsComboId:
            subNsNodeId:
            tenantId: 
            tradeId: 
            catalogueDir:
            status:

        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        csar_ctx = OrderedDict()
        csar_ctx.update(self.meta_data)
        csar_ctx.update({'catalogueDir': self.csar_upload_dir})
        csar_ctx.update({'status': CSAR_STATUS_UPLOADING})
        ctx_store.add_context_item(csar_ctx, CONTEXT_NAMESPACE_CSAR, 
                                   self.csar_id, item_id_n='csarId')

    def _update_csar_context(self):

        '''
        change the csar status to uploaded

        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_CSAR, self.csar_id)
        ctx_h.get_context_item()['status'] = CSAR_STATUS_UPLOADED
        print 'ctx_store'
	print ctx_store.root_context
        ctx_h.process_finish()
        
