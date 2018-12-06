#   The class of the slice resource context generation job unit


import os
from copy import deepcopy
from collections import OrderedDict

from common.util import get_class_func_name, cata_download, del_dir_or_file, \
                            SLICE_STATUS_RES_INISTANTIATING, CONTEXT_NAMESPACE_SLICE, CONTEXT_NAMESPACE_NS_COMBO
from common.yaml_util import yaml_ordered_load as yaml_load, yaml_ordered_dump as yaml_dump
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-4-16'  
__version__ = 1.0



class SliceResCtxGenerateJob(JobUnit):
    
    '''
    this job is used to generate the slice resource context when slice instantiation is requested.
    the works done by this job are:
        download the nsd and vnfd files from the catalogue and read
        generate and store the slice resource context, consists with:
            resourceInfo:
                sliceResId: the id of the slice in the e2e res mgr component
                nsResInfo:
                    nsdContent:
                    vnfResInfo:
                        (vnfNodeId):
                            datacenterId:
                            rtVimType:
                            rtVimMgrEndPoint:
                            nsdVnfNodeId:
                            vnfdContent:
                            vnfcResInfo:
                                (vnfcNodeId):
                                    vduId:
                                    rtVmNum:
                                    vnfcEndPointResInfo:
                                        (vnfcEndPointId):
                                            cpId:
                                            rtPrivateIpList:
                                            rtPublicIpList:
                            vnfEndPointResInfo:
                                (vnfEndPointId):
                                    relatedCpId:
                                    relatedVduId:
                                    rtPublicIpList:
                            vnfScalingPolicyInfo:
                                (vnfSpId):
                                    vnfdSpId:
                                    targetVnfcNodeIdList:
                                    targetVduIdList:
                                    rtTriggerUrl:
                    
    Note that currently support the datacenter resource processing, and the resource context
    is derived from the resource info in the meta by adding runtime info such as vmList, privateIpList, 
    and etc.
    this job output:
        'slice_id': the id of the slice been processed
    '''
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(SliceResCtxGenerateJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        try:
            self.event = self.task_unit.get_triggered_event()
            self.slice_id = self.event.get_event_data().get('slice_id', None)
            self._update_slice_instantiating()
            r_data = {'status': 'request accepted'}
            self.event.set_return_data_syn(r_data)

            sch = self.task_unit.task_scheduler
            self.cata_ip = sch.get_catalogue_serv_ip()
            self.cata_port = sch.get_catalogue_serv_port()
            self.cata_proto = sch.get_catalogue_serv_proto()
            self.cata_usr = sch.get_catalogue_serv_username()
            self.cata_passwd = sch.get_catalogue_serv_password()

            self._gen_local_download_tmp_dir()
            self._gen_res_ctx()
            self._output_params(**{'slice_id': self.slice_id})
            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self.event.set_return_data_asyn({'status': 'request failed'})
            self._execution_exception(Exception, e)
    
    def _update_slice_instantiating(self):

        '''
        change the slice status to resource instantiating in the context

        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE, self.slice_id)
        ctx_h.get_context_item()['status'] = SLICE_STATUS_RES_INISTANTIATING
        self.csar_cata_dir = ctx_h.get_context_item()['csarCataDir']
        ctx_h.process_finish()
 
    
    def _gen_local_download_tmp_dir(self):

        '''
        generate a tmp local dir to put the download defnition files

        '''
        if not os.path.exists('def_download_tmp'):
            os.mkdir('def_download_tmp')
        cur_dir = os.path.abspath(os.getcwd())
        os.chdir('def_download_tmp')
        if os.path.exists(self.slice_id):
            os.system('rm -r ' + self.slice_id)
        os.mkdir(self.slice_id)
        self.def_local_dir = os.path.abspath(self.slice_id)
        os.chdir(cur_dir)
    
    def _gen_res_ctx(self):

        '''
        generate resource context, including:
            create context from datacenter resource info in the metadata
            download nsd and vnfd file and read
            add runtime info in the resource context

        '''
        ctx_store = self.task_unit.task_scheduler.context_store

        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE, self.slice_id)
        ns_combo_id = ctx_h.get_context_item()['nsComboId']
        ctx_h.process_finish()
        
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_NS_COMBO, ns_combo_id)
        vnf_loc_info = ctx_h.get_context_item().get('locationInfo', {}).get('vnfLocations', {})
        ctx_h.process_finish()

        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE, self.slice_id)
        slice_ctx = ctx_h.get_context_item()
        meta_res = slice_ctx['metadata'].pop('resourceInfo')
        
        #   create datacenter resource context from metadata
        ctx_loc = slice_ctx.setdefault('resourceInfo', OrderedDict())
        ctx_loc.update(meta_res)
        ctx_loc['sliceResId'] = None

        #   download and read the nsd file, add nsd content to resource context
        nsd_cata_path = os.path.join(self.csar_cata_dir, slice_ctx['metadata']['nsdInfo']['csarFilePath'])
        nsd_local_path = os.path.join(self.def_local_dir, 'nsd.yaml')
        os.mknod(nsd_local_path)
        cata_download(self.cata_ip, self.cata_port, self.cata_proto, self.cata_usr, self.cata_passwd, 
                             nsd_local_path, nsd_cata_path)
        f = file(nsd_local_path, 'rb')
        ctx_loc['nsResInfo']['nsdContent'] = yaml_load(f)
        f.close()
        del_dir_or_file(nsd_local_path)

        #   download and read the vnfd files, add vnfd content and other runtime information to resource context
        ctx_loc = ctx_loc['nsResInfo'].setdefault('vnfResInfo', OrderedDict())
        for vnf_nid, v in slice_ctx['metadata']['vnfdInfo'].items():
            vnfd_cata_path = os.path.join(self.csar_cata_dir, v['csarFilePath'])
            vnfd_local_path = os.path.join(self.def_local_dir, vnf_nid + '_vnfd.yaml')
            os.mknod(vnfd_local_path)
            cata_download(self.cata_ip, self.cata_port, self.cata_proto, self.cata_usr, self.cata_passwd, 
                             vnfd_local_path, vnfd_cata_path)
            ctx_vnf_loc = ctx_loc.setdefault(vnf_nid, OrderedDict())
            f = file(vnfd_local_path, 'rb')
            ctx_vnf_loc['vnfdContent'] = yaml_load(f)
            f.close()
            ctx_vnf_loc['datacenterId'] = self._select_dc_for_vnf_node(slice_ctx['subNsNodeId'], vnf_nid, vnf_loc_info)
            print "#####DEBUG: ctx_vnf_loc: ", ctx_vnf_loc['vnfdContent']
            ctx_vnf_loc['rtVimType'] = None
            ctx_vnf_loc['rtVimMgrEndPoint'] = None
            vnfd_node_loc = ctx_vnf_loc['vnfdContent']['topology_template']['node_templates']
            for vnfc_nid, vnfc_v in ctx_vnf_loc['vnfcResInfo'].items():
                vnfc_v['rtVmNum'] = 0
                
                #   add the vnfc image location in the catalogue to the vnfd
                image_cata_path = os.path.join(slice_ctx['csarCataDir'], \
                                               slice_ctx['metadata']['deploymentArtifactInfo']\
                                                        [vnf_nid][vnfc_nid]['imageInfo']['csarFilePath'])
                vnfd_node_loc[vnfc_v['vduId']]['properties']['image_location'] = \
                                     self.cata_proto + '://' + self.cata_ip + ':' + \
                                     str(self.cata_port) + '/' + image_cata_path
                for vnfc_epid, ep_v in vnfc_v['vnfcEndPointResInfo'].items():
                    ep_v['rtPrivateIpList'] = []
                    ep_v['rtPublicIpList'] = []
            for vnf_epid, ep_v in ctx_vnf_loc['vnfEndPointResInfo'].items():
                ep_v['rtPublicIpList'] = []
            for sp_id, v in ctx_vnf_loc.get('vnfScalingPolicyInfo', {}).items():
                v['rtTriggerUrl'] = None
            del_dir_or_file(vnfd_local_path)
        
        print '#### GenSliceResCtxJob: generate slice resource context with slice id: ' + self.slice_id
        #   print yaml_dump(slice_ctx['resourceInfo'], default_flow_style=False)
        ctx_h.process_finish()
        
    def _select_dc_for_vnf_node(self, sub_ns_nid, vnf_nid, vnf_loc_info):

        '''
        select the datacenter resource for a vnf node deployment

        '''
        print "##########debug#########"
        print "_select_dc_for_vnf_node : ", sub_ns_nid, vnf_nid
        return vnf_loc_info.get(sub_ns_nid, {}).get(vnf_nid, {}).get('locatorName', None)  
