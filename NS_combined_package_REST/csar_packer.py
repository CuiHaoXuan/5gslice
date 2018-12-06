#!/usr/bin/python

#   this script is used to pack a csar

import yaml
import logging
import os
import json
import platform
from collections import OrderedDict

from csar_model.csar_architect import CsarArchitect
from csar_model.csar_meta import CsarMeta
from csar_model.tosca_nsd import ToscaNsd
from csar_model.tosca_vnfd import ToscaVnfd

from helper.csar_helper import CsarHelper

from common.util.yaml_util import yaml_ordered_dump, json_ordered_load, yaml_ordered_load

#logging.basicConfig(filename='csarPacker.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
#log = logging.getLogger('csarPacker')

class CsarPacker(object):

    def __init__(self, design_files_dir, upload_user_dir, sub_ns_nid=None):
        
        MAIN_DIR = os.path.abspath(os.getcwd())
        DESIGN_FILES_DIR = os.path.abspath(design_files_dir)
        UPLOAD_USER_DIR = os.path.abspath(upload_user_dir)

        #   VNFC_ARTIFACTS_DIR = os.path.join(UPLOAD_USER_DIR, 'vnfc_artifacts', '')
        #   VNFC_IMAGES_DIR = os.path.join(UPLOAD_USER_DIR, 'vnfc_images', '')
        #   MONITOR_ARTIFACTS_DIR = os.path.join(UPLOAD_USER_DIR, 'monitor_file_packs', '')
        #   PLANS_DIR = os.path.join(UPLOAD_USER_DIR, 'plans', '')

        YAML_FILES = [f for f in os.listdir(DESIGN_FILES_DIR) if '.yaml' in f]
        for f in YAML_FILES:
            if '_ns_type' in f:
                NS_T_FILE = f
            if '_ns_flavor' in f and 'subscribe' in f:
                NS_F_SUB_FILE = f
            elif '_ns_flavor' in f:
                NS_F_FILE = f

        #  the full paths of ns_type and ns_flavor
        NS_TYPE_FILE = os.path.join(DESIGN_FILES_DIR, NS_T_FILE)
        NS_FLAVOR_FILE = os.path.join(DESIGN_FILES_DIR, NS_F_FILE)
        #   NS_FLAVOR_SUB_FILE = os.path.join(DESIGN_FILES_DIR, NS_F_SUB_FILE)


        VNFC_T_FILE_NAME_LIST = [f for f in YAML_FILES if '_vnfc_type' in f]
        VNF_T_FILE_NAME_LIST = [f for f in YAML_FILES if '_vnf_type' in f]
        VNFC_REL_TYPE_FILE_NAME_LIST = [f for f in YAML_FILES if '_vnfc_rel_type' in f]
        VNF_REL_TYPE_FILE_NAME_LIST = [f for f in YAML_FILES if '_vnf_rel_type' in f]

        # the full path of the vnfc_types, vnf_types, vnfc_ref and vnf_ref
        fun = lambda x: os.path.join(DESIGN_FILES_DIR, x)
        VNFC_TYPE_FILES_LIST = map(fun, VNFC_T_FILE_NAME_LIST)
        VNF_TYPE_FILES_LIST = map(fun, VNF_T_FILE_NAME_LIST)
        VNFC_REL_TYPE_FILES_LIST = map(fun, VNFC_REL_TYPE_FILE_NAME_LIST)
        VNF_REL_TYPE_FILES_LIST = map(fun, VNF_REL_TYPE_FILE_NAME_LIST)

        CSAR_PARENT_DIR = os.path.join(MAIN_DIR, 'csar_pack', '')
        if not os.path.exists(CSAR_PARENT_DIR):
            os.mkdir(CSAR_PARENT_DIR)

        #   self.ns_f_sub = self._gen_ns_flavor_sub(NS_FLAVOR_SUB_FILE)
        self.ns_f = self._gen_ns_flavor(NS_FLAVOR_FILE)
        self.ns_t = self._gen_ns_type(NS_TYPE_FILE)
        self.vnf_rel_t_list = self._gen_vnf_rel_type_list(VNF_REL_TYPE_FILES_LIST)
        self.vnf_t_list = self._gen_vnf_type_list(VNF_TYPE_FILES_LIST)
        self.vnfc_rel_t_list = self._gen_vnfc_rel_type_list(VNFC_REL_TYPE_FILES_LIST)
        self.vnfc_t_list = self._gen_vnfc_type_list(VNFC_TYPE_FILES_LIST)

        self.helper = CsarHelper(ns_f=self.ns_f, ns_t=self.ns_t,
                       vnf_r_list=self.vnf_rel_t_list, vnf_t_list=self.vnf_t_list,
                       vnfc_r_list=self.vnfc_rel_t_list, vnfc_t_list=self.vnfc_t_list)
        b_info = self.helper.get_basic_info()
        self.basic_info = b_info
        
        self.architect = CsarArchitect(CSAR_PARENT_DIR)
        if sub_ns_nid:
            self.architect.set_architect_framework(sub_ns_nid, b_info['nsFlavorId'], 
                                                   b_info['nsTypeId'])
        else:
            self.architect.set_architect_framework(b_info['nsFlavorId'], 
                                                   b_info['nsTypeId'])

        self.meta = CsarMeta(b_info['nsFlavorId'], b_info['nsTypeId'], 
                             b_info['version'], b_info['vendor'],
                             b_info['nsFlavorDesc'])
        #   extended to record the datacenter resource related information in the csar metadata
        self.meta_res = OrderedDict()
        self.meta_res['nsResInfo'] = OrderedDict()
        self.meta_res['nsResInfo']['vnfResInfo'] = OrderedDict()


    '''
    def _gen_ns_flavor_sub(self, ns_f_sub_f):
        f_p = ns_f_sub_f
        f = open(f_p, 'r')
        return yaml_ordered_load(f)
    '''

    def _gen_ns_flavor(self, ns_f_f):
        f_p = ns_f_f
        f = open(f_p, 'r')
        return yaml_ordered_load(f)

    def _gen_ns_type(self, ns_t_f):
        f_p = ns_t_f
	print ns_t_f
        f = open(f_p, 'r')
        return yaml_ordered_load(f)

    def _gen_vnf_rel_type_list(self, vnf_rel_t_f_list):
        f_p_list = vnf_rel_t_f_list
        f_list = map(lambda x: open(*x), zip(f_p_list, 'r' * len(f_p_list)))
        return map(yaml_ordered_load, f_list)

    def _gen_vnf_type_list(self, vnf_t_f_list):
        f_p_list = vnf_t_f_list
        f_list = map(lambda x: open(*x), zip(f_p_list, 'r' * len(f_p_list)))
        return map(yaml_ordered_load, f_list)

    def _gen_vnfc_rel_type_list(self, vnfc_rel_t_f_list):
        f_p_list = vnfc_rel_t_f_list
        f_list = map(lambda x: open(*x), zip(f_p_list, 'r' * len(f_p_list)))
        return map(yaml_ordered_load, f_list)

    def _gen_vnfc_type_list(self, vnfc_t_f_list):
        f_p_list = vnfc_t_f_list
        f_list = map(lambda x: open(*x), zip(f_p_list, 'r' * len(f_p_list)))
        return map(yaml_ordered_load, f_list)

    def gen_nsd_and_res_meta(self):

        '''
        generate the nsd and meta resource info for the csar

        '''
        b_info = self.basic_info
        nsd = ToscaNsd(b_info['nsTypeId'], b_info['nsFlavorId'], 
                       b_info['version'], b_info['vendor'],
                       b_info['nsFlavorDesc'])
        vnf_nid_list = self.helper.get_vnf_nid_list()
        map(nsd.add_import_vnfd, vnf_nid_list)
        
        ns_mat = self.ns_t

        #   add vnf node
        dc_res_loc = self.meta_res['nsResInfo']['vnfResInfo']
        for vnf_nid in vnf_nid_list:
            loc = dc_res_loc.setdefault(vnf_nid, OrderedDict())
            loc['nsdVnfNodeId'] = nsd.add_vnf_node(vnf_nid)
        
        #   handle ns endpoint for nsd
        for ep_id, v in ns_mat['EndPoints'].items():
            vnf_nid = v['vnfNodeId']
            vnf_epid = v['vnfEndPointId']
            nsd.add_cp_of_ns_ep(ep_id, vnf_nid, vnf_epid)
            nsd.add_vl(ep_id)
            #nsd.add_vnf_requirements(vnf_nid, vnf_epid, ep_id)

        #   handle vnf connection for nsd
        for conn_id, v in ns_mat['Connections'].items():
            nsd.add_vl(conn_id)
            vnf_rel_id = v['vnfRelationshipTypeId']
            vnf_nid_1 = v['endOne']['vnfNodeId']
            vnf_nid_2 = v['endTwo']['vnfNodeId']
            vnf_epid_1 = self.helper.vnf_nid_to_epid_by_relation_tid(
                                               vnf_rel_id, vnf_nid_1)
            vnf_epid_2 = self.helper.vnf_nid_to_epid_by_relation_tid(
                                               vnf_rel_id, vnf_nid_2)
            nsd.add_vnf_requirements(vnf_nid_1, vnf_epid_1, conn_id)
            nsd.add_vnf_requirements(vnf_nid_2, vnf_epid_2, conn_id)

        self.architect.add_nsd(b_info['nsTypeId'], 
                               b_info['nsFlavorId'], nsd.get_model())
    
    def gen_vnfd_and_res_meta(self):

        '''
        generate all the vnfds and the meta resource info

        '''
        vnf_nid_list = self.helper.get_vnf_nid_list()
        #   vnfc_deploy_f_mat = self.ns_f['VnfcDeploymentFlavors']
        dc_res_loc = self.meta_res['nsResInfo']['vnfResInfo']
        vnfc_f_mat = self.ns_f['VnfcDeploymentFlavors']
        for vnf_nid in vnf_nid_list:
            vnf_mat = self.helper.get_vnf_t_mat_by_vnf_nid(vnf_nid)
            vnf_info = vnf_mat['Info']
            vnfd = ToscaVnfd(vnf_nid, vnf_info['version'], vnf_info['vendor'], 
                             vnf_info['description'])           
         
            res_vnf_loc = dc_res_loc.setdefault(vnf_nid, OrderedDict())
            res_vnfc_loc = res_vnf_loc.setdefault('vnfcResInfo', OrderedDict())
            #   add vdu for vnfc node
            for vnfc_nid in vnf_mat['VnfcNodes'].keys():
                vnfc_mat = self.helper.get_vnfc_t_mat_by_vnf_nid_vnfc_nid(
                                                      vnf_nid, vnfc_nid)
                vnfc_f_loc = vnfc_f_mat[vnf_nid][vnfc_nid]
                vim_t = vnfc_f_loc['vimType']
                flavor_t = vnfc_f_loc['vmFlavor']
                os_t = vnfc_f_loc['osType']

                vnfc_image_info = vnfc_mat['DeploymentArtifact']\
                                         ['imageInfo']
                image_name = vnfc_image_info['image']
                local_image_path = vnfc_image_info['getFile']

                loc = res_vnfc_loc.setdefault(vnfc_nid, OrderedDict())
                loc['vduId'] = vnfd.add_vdu_node(vnfc_nid, vim_t, flavor_t, os_t, image_name)
            
            #   handle the vnfc connection for vnfd
            for conn_id, v in vnf_mat['Connections'].items():
                vnfc_nid_1 = v['endOne']['vnfcNodeId']
                vnfc_epid_1 = v['endOne']['vnfcEndPointId']
                vnfc_nid_2 = v['endTwo']['vnfcNodeId']
                vnfc_epid_2 = v['endTwo']['vnfcEndPointId']

                loc = res_vnfc_loc[vnfc_nid_1].setdefault('vnfcEndPointResInfo', OrderedDict())
                loc = loc.setdefault(vnfc_epid_1, OrderedDict())
                loc['cpId'] = vnfd.add_cp_in_connection(conn_id, vnfc_nid_1, vnfc_epid_1)

                loc = res_vnfc_loc[vnfc_nid_2].setdefault('vnfcEndPointResInfo', OrderedDict())
                loc = loc.setdefault(vnfc_epid_2, OrderedDict())
                loc['cpId'] = vnfd.add_cp_in_connection(conn_id, vnfc_nid_2, vnfc_epid_2)

                vnfd.add_vl_of_connection(conn_id)

            #   handle the vnf endpoint for vnfd
            for vnf_epid, v in vnf_mat['EndPoints'].items():
                vnfc_nid = v['vnfcNodeId']
                vnfc_epid = v['vnfcEndPointId']
                loc = res_vnf_loc.setdefault('vnfEndPointResInfo', OrderedDict())
                loc = loc.setdefault(vnf_epid, OrderedDict())
                loc['relatedCpId'], loc['relatedVduId'] = vnfd.add_cp_of_vnf_ep(vnf_epid, vnfc_nid, vnfc_epid)
                cp_id = loc['relatedCpId']
                loc = res_vnf_loc.setdefault('vnfcResInfo', OrderedDict())
                loc = loc.setdefault(vnfc_nid, OrderedDict())
                loc = loc.setdefault('vnfcEndPointResInfo', OrderedDict())
                loc = loc.setdefault(vnfc_epid, OrderedDict())
                loc['cpId'] = cp_id

            #   handle the vnf scaling policy for vnfd
            scale_mat = vnf_mat['ScalingInfo']
            for op_id, op_v in scale_mat['scalingOperations'].items():
                sp_mat = self.helper.get_scale_policy_mat_by_vnf_nid_and_scale_opid(vnf_nid, op_id)
                if sp_mat:
                    scale_g_mat = \
                           self.helper.get_vnf_t_scale_group_mat_by_vnf_nid_and_scale_opid(vnf_nid, op_id)
                    sp_target = res_vnfc_loc[scale_g_mat['target']]['vduId']
                    vnfd_spid = vnfd.add_scaling_policy(op_id, op_v['scalingStep'], sp_mat['cooldown'],
                                 scale_g_mat['min'], scale_g_mat['max'], scale_g_mat['defaultGroup'],
                                 sp_target)
                    loc = res_vnf_loc.setdefault('vnfScalingPolicyInfo', OrderedDict())
                    loc = loc.setdefault(op_id, OrderedDict())
                    loc['vnfdSpId'] = vnfd_spid
                    loc['targetVnfcNodeIdList'] = [scale_g_mat['target']]
                    loc['targetVduIdList'] = [sp_target]
            self.architect.add_vnfd(vnf_nid, vnfd.get_model())
    
    def gen_plan(self):

        '''
        generate the plan files

        '''
        instan_plan_mat = self.ns_t['Plans']['instantiatePlan']
        self.architect.add_instan_plan(instan_plan_mat['getFile'])

        for plan_id, v in self.ns_t['Plans']['scalingPlans'].items():
            self.architect.add_scale_plan(plan_id, v['getFile'])
    
    def finish_meta(self):

        '''
        complete the csar metadata

        '''

        #   add topology meta info
        ns_mat = self.ns_t
        
    ############ add vnf connections to meta topo info #########

        conn_mat = ns_mat['Connections']
        for conn_id, v in conn_mat.items():
            vnf_rel_id = v['vnfRelationshipTypeId']
            vnf_nid_1 = v['endOne']['vnfNodeId']
            vnf_nid_2 = v['endTwo']['vnfNodeId']
            vnf_epid_1 = self.helper.vnf_nid_to_epid_by_relation_tid(
                               vnf_rel_id, vnf_nid_1)
            vnf_epid_2 = self.helper.vnf_nid_to_epid_by_relation_tid(
                               vnf_rel_id, vnf_nid_2)
            self.meta.add_topo_vnf_connection_info(conn_id, 
                                        vnf_nid_1, vnf_epid_1, 
                                        vnf_nid_2, vnf_epid_2)
     
     ######### add ns endpoint to meta topo info ############
        
        ep_mat = ns_mat['EndPoints']
        for ep_id, v in ep_mat.items():
            vnf_nid = v['vnfNodeId']
            vnf_epid = v['vnfEndPointId']
            self.meta.add_topo_ns_endpoint_info(ep_id, vnf_nid, vnf_epid)
        
        prop_dependencies = [] # this is using to record the depended vnfc properties
        vnf_nid_list = self.helper.get_vnf_nid_list()
        for vnf_nid in vnf_nid_list:
            vnf_tid = self.helper.vnf_nid_to_tid(vnf_nid)
            vnf_mat = self.helper.get_vnf_t_mat_by_vnf_nid(vnf_nid)

            vnfc_nid_list = self.helper.get_vnfc_nid_list_by_vnf_nid(vnf_nid)
            for vnfc_nid in vnfc_nid_list:
               
               ############ add vnfc node to meta topo info ###########

                vnfc_tid = self.helper.vnfc_nid_to_tid_by_vnf_tid(vnf_tid, vnfc_nid)
                self.meta.add_topo_vnfc_info(vnf_nid, vnf_tid, vnfc_nid, vnfc_tid)

                vnfc_mat = self.helper.get_vnfc_t_mat_by_vnf_nid_vnfc_nid(
                                                      vnf_nid, vnfc_nid)

                ########## copy the artifact files and add info to the meta ##########
                vnfc_pack_info = vnfc_mat['DeploymentArtifact']\
                                         ['filePackInfo']
                local_pack_path = vnfc_pack_info['getFile']

                vnfc_image_info = vnfc_mat['DeploymentArtifact']\
                                         ['imageInfo']
                local_image_path = vnfc_image_info['getFile']
                
                #   add artifact file pack
                self.architect.add_artifact_file_pack(vnf_nid, vnfc_nid, local_pack_path)
                #   add artifact image file
                self.architect.add_artifact_image(vnf_nid, vnfc_nid, local_image_path)
                
                pack_t = vnfc_pack_info['packType']
                arti_root_dir = vnfc_pack_info['rootDir']

                #   add deployment artifact file pack info to meta
                local_csar_pack_path = self.architect.get_architect()['artiFilePackPaths']\
                                                               [vnf_nid][vnfc_nid]
                csar_pack_path = self.architect.get_csar_rel_path(local_csar_pack_path)
                pack_name = None
                if local_pack_path:
                    tmp, pack_name = os.path.split(local_pack_path)
                self.meta.add_arti_vnfc_pack(vnf_nid, vnfc_nid, pack_name,
                                 pack_t, csar_pack_path, arti_root_dir)

                #   add deployment artifact image info to meta
                local_csar_image_path = self.architect.get_architect()['artiImagePaths']\
                                                               [vnf_nid][vnfc_nid]
                csar_image_path = self.architect.get_csar_rel_path(local_csar_image_path)
                image_name = None
                if local_image_path:
                    tmp, image_name = os.path.split(local_image_path)
                self.meta.add_arti_vnfc_image(vnf_nid, vnfc_nid, image_name, csar_image_path)
        
        ########### add vnfc configuration info and properties info to meta #############
                
                for if_id, v in vnfc_mat['Interfaces'].items():
                    if_scope, if_order, if_format, if_f_p = \
                    v['scope'], v['order'], v['format'], v['absPath']
                    props = self.helper.get_prop_id_list_by_interface(vnf_nid, vnfc_nid, if_id)

                    #   add interface info to the meta
                    if_f_p = self.helper.deploy_abs_path_trans(arti_root_dir, if_f_p)
                    self.meta.add_conifg_interface(vnf_nid, vnfc_nid, if_id, 
                                   if_scope, if_order, if_format, if_f_p, props)

                    #   add configurable properties info to meta
                    for prop_id in props:
                        #print "DEBUG : ", vnf_nid, "----", vnfc_nid, "-----", prop_id
                        prop_v = self.helper.get_prop_value(vnf_nid, vnfc_nid, prop_id)
                        #print 'csar packer aaaaaaaaaaaaaa'
                        #print ' add vnfc properties '
                        #print 'prop_id: ', prop_id, ' prop_v', prop_v
                        multi_ins_opt, dep_vnf_nid, dep_vnfc_nid, dep_prop_id = \
                                  self.helper.get_depend_prop_by_vnf_nid(vnf_nid, vnfc_nid, prop_id)
                        if not dep_vnfc_nid:
                            self.meta.add_independent_para_info(vnf_nid, vnfc_nid, 
                                            prop_id, prop_v)
                        else:
                            prop_dependencies.append((dep_vnf_nid, dep_vnfc_nid, dep_prop_id))
                            self.meta.add_dependent_para_info(vnf_nid, vnfc_nid, prop_id,  
                                      dep_vnf_nid, dep_vnfc_nid, dep_prop_id, multi_ins_opt)

       ############ add vnfc connections to meta topo info #############      
            
            conn_mat = vnf_mat['Connections']
            for conn_id, v in conn_mat.items():
                vnfc_rel_id = v['vnfcRelationshipTypeId']
                vnfc_nid_1 = v['endOne']['vnfcNodeId']
                vnfc_nid_2 = v['endTwo']['vnfcNodeId']
                vnfc_epid_1 = self.helper.vnfc_nid_to_epid_by_relation_tid_vnf_tid(
                                   vnfc_rel_id, vnf_tid, vnfc_nid_1)
                vnfc_epid_2 = self.helper.vnfc_nid_to_epid_by_relation_tid_vnf_tid(
                                   vnfc_rel_id, vnf_tid, vnfc_nid_2)
                self.meta.add_topo_vnfc_connection_info(vnf_nid, vnf_tid, conn_id, 
                                            vnfc_nid_1, vnfc_epid_1, 
                                            vnfc_nid_2, vnfc_epid_2)
        
        ############ add vnf endpoint to meta topo info #############
            
            ep_mat = vnf_mat['EndPoints']
            for ep_id, v in ep_mat.items():
                vnfc_nid = v['vnfcNodeId']
                vnfc_epid = v['vnfcEndPointId']
                self.meta.add_topo_vnf_endpoint_info(vnf_nid, vnf_tid, ep_id, 
                                             vnfc_nid, vnfc_epid)
        
        ############ add vnfd meta info ################
        
            local_vnfd_f_p = self.architect.get_architect()['vnfdFilePaths']\
                                                     [vnf_nid]
            csar_vnfd_f_p = self.architect.get_csar_rel_path(local_vnfd_f_p)
            tmp, vnfd_f_n = os.path.split(local_vnfd_f_p)
            self.meta.add_vnfd_info(vnf_nid, vnfd_f_n, csar_vnfd_f_p)

        ############# add vnf monitor info to meta #############


            mon_mat = self.helper.get_vnf_t_monitor_mat_by_vnf_nid(vnf_nid)
            self.meta.add_monitor_options(mon_mat)
            '''
            for mon_id, v in mon_mat.items():
                t_vnfc_nids = v['filePackInfo']['target']
                pack_t = v['filePackInfo']['packType']
                locate = v['filePackInfo']['locate']
                root_dir = v['filePackInfo']['rootDir']
                local_monitor_pack_path = v['filePackInfo']['getFile']

                self.architect.add_monitor_artifact_file_pack(vnf_nid, mon_id, local_monitor_pack_path)

                local_csar_monitor_pack_path = self.architect.get_architect()\
                                         ['monitorArtiFilePaths'][vnf_nid][mon_id]
                csar_monitor_pack_path = self.architect.get_csar_rel_path(local_csar_monitor_pack_path)
                tmp, monitor_pack_name = os.path.split(local_monitor_pack_path)            
                self.meta.add_monitor_artifact(vnf_nid, mon_id, t_vnfc_nids, locate,  
                                   monitor_pack_name, pack_t, root_dir, csar_monitor_pack_path)

                for if_id, if_v in v['interfaces'].items():
                    if_scope, if_order, if_format, if_f_p = \
                    if_v['scope'], if_v['order'], if_v['format'], if_v['relPath']
                    props = self.helper.get_prop_id_list_by_monitor_interface(vnf_nid, mon_id, if_id)
                    if_f_p = self.helper.deploy_abs_path_trans(root_dir, if_f_p)
                    self.meta.add_monitor_interface(vnf_nid, mon_id, if_id, 
                                      if_scope, if_order, if_format, if_f_p, props)
                    
                    for prop_id in props:
                        prop_v = self.helper.get_mon_prop_value(vnf_nid, mon_id, prop_id)
                        self.meta.add_monitor_independent_parameter(vnf_nid, mon_id, 
                                                    prop_id, prop_v)
            '''

        
        ##########  add metric info to meta ############
        
        metric_mat = ns_mat['Metrics']
        for m_id, m_info in metric_mat.items():
            self.meta.add_metric(m_id, m_info['name'], 
                                       m_info['interval'], m_info['description'])
            for k, v in m_info['dimensions'].items():
                self.meta.add_dim_to_metric(m_id, k, v['valueType'], v['name'])
        
        
        ##########  add alarm info to meta ############

        alarm_mat = ns_mat['Alarms']
        for a_id, a_info in alarm_mat.items():
            
            #   add alarm artifact file pack
            local_pack_path = a_info['getFile']
            self.architect.add_alarm_file_pack(a_id, local_pack_path)

            #   add alarm artifact file pack info to meta
            local_csar_pack_path = self.architect.get_architect()\
                                            ['alarmArtiFilePaths'][a_id]
            csar_pack_path = self.architect.get_csar_rel_path(local_csar_pack_path)
            self.meta.add_alarm(a_id, csar_pack_path, a_info['statFormat'], 
                                      a_info['relPath'], a_info['outputEnv'], 
                                      a_info['comparison'], a_info['threshold'], 
                                      a_info['description'], a_info['packType'])
        
        ##########   complete the vnfc configurable properties info  ############     
        
        for dep in prop_dependencies:
            vnf_nid, vnfc_nid, prop_id = dep
            prop_v = self.helper.get_prop_value(vnf_nid, vnfc_nid, prop_id)
            self.meta.add_independent_para_info(vnf_nid, vnfc_nid, 
                                            prop_id, prop_v)
        
        ###########   add nsd meta info  ################
        
        local_nsd_f_p = self.architect.get_architect()['nsdFilePath']
        csar_nsd_f_p = self.architect.get_csar_rel_path(local_nsd_f_p)
        tmp, nsd_f_n = os.path.split(local_nsd_f_p)
        self.meta.add_nsd_info(nsd_f_n, csar_nsd_f_p)

        ###########   add resource info  #############
        
        self.meta.add_res_info(self.meta_res)

        ###########   add vnf sharing policy info to meta  ##############
        
        vsp_mat = self.helper.get_vnf_sharing_policies_mat()
        for vsp_id, v in vsp_mat.items():
            self.meta.add_vnf_sharing_policy(vsp_id, v['sharingType'], v['relatedVnfNode'])      
        
        ###########   add service exposure policy info to meta  ##############
        
        sep_mat = self.helper.get_service_exposure_policies_mat()
        for sep_id, v in sep_mat.items():
            sep_name = v['name']
            desc = v['description']
            self.meta.add_serv_exposure_policy(sep_id, sep_name, desc)

            for mem_id, mem_v in v['serviceMembers'].items():
                vnf_nid, serv_id = mem_v['vnfNodeId'], mem_v['serviceId']
                se_mat = self.helper.get_service_exposure_mat(vnf_nid, serv_id)
                serv_n, ep_id, se_desc = se_mat['name'], se_mat['exposureEndPointId'], se_mat['description']
                vnfc_nid, vnfc_ep_id = self.helper.vnf_epid_to_vnfc_nid_and_vnfc_epid_by_vnf_nid(vnf_nid, ep_id) 
                self.meta.add_service_member(sep_id, mem_id, vnf_nid, 
                                      serv_id, serv_n, ep_id, 
                                      vnfc_nid, vnfc_ep_id, se_desc)

        ###########   add property exposure policy info to meta  ##############
        
        pep_mat = self.helper.get_property_exposure_policies_mat()
        for pep_id, v in pep_mat.items():
            vnf_nid = v['vnfNodeId']
            vnfc_nid = v['vnfcNodeId']
            prop_id = v['propertyId']
            self.meta.add_prop_exposure_policy(pep_id, vnf_nid, vnfc_nid, prop_id)
        
        ###########   add scaling policy info to meta  ##############
        
        sp_mat = self.helper.get_scale_policies_mat()
        for sp_id, v in sp_mat.items():
            self.meta.add_scaling_policy(sp_id, v['alarmId'], v['hookType'], 
                                        v['cooldown'], v['scalingPlan'], v['description'])
            for act_id, act_v in v['actions'].items():
                if act_v['involvedEntityType'] == 'vnf':
                    self.meta.add_scaling_action_in_vnf(sp_id, act_id, act_v['involvedEntityId'], 
                                                                    act_v['scalingOpId'])
        
        ##############   add instantiate plan meta info ##################
        
        local_instan_plan_f_p = self.architect.get_architect()['planInstanFilePath']
        csar_instan_plan_f_p = self.architect.get_csar_rel_path(local_instan_plan_f_p)
        tmp, instan_plan_f_n = os.path.split(local_instan_plan_f_p)
        self.meta.add_instan_plan_info(instan_plan_f_n, csar_instan_plan_f_p)
        
        ##############   add scaling plan meta info ##################
        for k, v in self.architect.get_architect()['planScaleFilePaths'].items():
            local_scale_plan_f_p = v
            csar_scale_plan_f_p = self.architect.get_csar_rel_path(local_scale_plan_f_p)
            tmp, scale_plan_f_n = os.path.split(local_scale_plan_f_p)
            self.meta.add_scale_plan_info(k, scale_plan_f_n, csar_scale_plan_f_p)
        
        
        self.architect.add_meta_data(self.meta.get_meta())

    def pack_csar(self):
        fun = lambda x: self.architect.get_architect()[x]
        parent_dir, csar_name, csar_dir = map(fun, ['parentDir', 'csarName', 'csarDir'])
        csar_pack_name = csar_name + '.tar.gz'
        csar_pack = os.path.join(parent_dir, csar_pack_name)
        cur_work_dir = os.getcwd()
        os.chdir(parent_dir)
        sysstr = platform.system()
        if sysstr == 'Linux':
            os.system('tar -zcf ' + csar_pack + ' ' + csar_name)
        elif sysstr == 'Windows':
            os.system('tar zcf ' + csar_pack + ' ' + csar_name)
        os.chdir(cur_work_dir)

    def gen_csar_pack(self):
        self.gen_nsd_and_res_meta()
        self.gen_vnfd_and_res_meta()
        self.gen_plan()
        self.finish_meta()
        self.pack_csar()

    def get_csar_pack_path(self):
        return os.path.join(self.architect.get_architect()['parentDir'], 
                            self.architect.get_architect()['csarName'] +  
                            '.tar.gz')

if __name__ == '__main__':
    packer = CsarPacker()
    packer.gen_nsd()
    packer.gen_vnfd()
    packer.gen_plan()
    packer.finish_meta()
    packer.pack_csar()
