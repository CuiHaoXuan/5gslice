#!/usr/bin/python

#   this script is used to pack the whole ns combo files including the ns combo meta and the related sub ns csar packs

import yaml
import logging
import os
import json
import platform
from collections import OrderedDict

from csar_packer import CsarPacker
from ns_combo_model.ns_combo_meta import NsComboMeta

from common.util.yaml_util import yaml_ordered_dump as yaml_dump, yaml_ordered_load as yaml_load

#logging.basicConfig(filename='nsComboPacker.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
#log = logging.getLogger('nsComboPacker')


class NsComboPacker(object):

    def __init__(self, ns_combo_flavor_file_path, subscribe_file_path, 
                                                    sub_ns_node_file_dirs):
        
        '''
        the sub_ns_node_file_dirs is a dict consisted in:
            (subNsNodeId):
                designFilesDir:
                userUploadsDir:
        '''
        
        self.MAIN_DIR = os.path.abspath(os.getcwd())

        f = open(os.path.abspath(ns_combo_flavor_file_path), 'r')
        self.ns_combo_f = yaml_load(f)
        f.close()
        f = open(os.path.abspath(subscribe_file_path), 'r')
        self.ns_combo_sub = yaml_load(f)
        f.close()
        self.sub_ns_csar_packer = {}

        # actually, we only have one casr right now!
        for sub_ns, v in sub_ns_node_file_dirs.items():
            self.sub_ns_csar_packer[sub_ns] = CsarPacker(v['designFilesDir'], v['userUploadsDir'], sub_ns)

        self.NS_COMBO_PARENT_DIR = os.path.join(self.MAIN_DIR, 'ns_combo_pack', '')
        if not os.path.exists(self.NS_COMBO_PARENT_DIR):
            os.mkdir(self.NS_COMBO_PARENT_DIR) 
        
        f_info, sub_info = self.ns_combo_f['Info'], self.ns_combo_sub['Info']
        self.meta = NsComboMeta(f_info['nsComboFlavorId'], f_info['version'], f_info['vendor'],
                       f_info['description'], sub_info['tenantId'], sub_info['tradeId'], sub_info['description'])

        self.NS_COMBO_FALVOR_NAME = '_'.join((f_info['nsComboFlavorId'], \
                                      f_info['version'], \
                                      f_info['vendor'], \
                                      sub_info['tenantId'], \
                                      sub_info['tradeId'].replace(' ', '@')))
        self.NS_COMBO_FLAVOR_DIR = os.path.join(self.NS_COMBO_PARENT_DIR, self.NS_COMBO_FALVOR_NAME, '')
        if not os.path.exists(self.NS_COMBO_FLAVOR_DIR):
            os.mkdir(self.NS_COMBO_FLAVOR_DIR)
        
        ####### generate the sla info ###########
        
        for k, v in self.ns_combo_f['ServiceLevelAgreementFlavors'].items():
            self.meta.add_sla_info(k, v)


        ####### generate the vnf location info ##########

        for sub_ns_nid, ns_v in self.ns_combo_sub['LocationAwareness']['vnfLocations'].items():
            for vnf_nid, v in ns_v.items():
                self.meta.add_vnf_location_info(sub_ns_nid, vnf_nid, v['locatorName'], v['locationDescription'])
        
        ####### generate the topology info ##########

        for sub_ns_nid, v in self.ns_combo_f['SubNsFlavors'].items():
            self.meta.add_topo_sub_ns_info(sub_ns_nid, v['nsTypeId'])

        # because right now we only have one subNs , so the ns_combo_flavor.yaml
        # won't contain the connections
        # this code won't work
        for conn_id, v in self.ns_combo_f['Connections'].items():
            sub_ns_nid_1, sub_ns_epid_1 = v['endOne']['subNsNodeId'], v['endOne']['nsEndPointId']
            sub_ns_nid_2, sub_ns_epid_2 = v['endTwo']['subNsNodeId'], v['endTwo']['nsEndPointId']
            vnf_nid_1, vnf_epid_1 = self.sub_ns_csar_packer[sub_ns_nid_1].helper.\
                                         ns_epid_to_vnf_nid_and_vnf_epid(sub_ns_epid_1)
            vnf_nid_2, vnf_epid_2 = self.sub_ns_csar_packer[sub_ns_nid_2].helper.\
                                         ns_epid_to_vnf_nid_and_vnf_epid(sub_ns_epid_2)
            self.meta.add_topo_sub_ns_connection_info(conn_id, 
                                                        sub_ns_nid_1, sub_ns_epid_1, vnf_nid_1, vnf_epid_1, 
                                                        sub_ns_nid_2, sub_ns_epid_2, vnf_nid_2, vnf_epid_2)

        for ep_id, v in self.ns_combo_f['EndPoints'].items():
            sub_ns_nid, sub_ns_epid = v['subNsNodeId'], v['nsEndPointId']
            vnf_nid, vnf_epid = self.sub_ns_csar_packer[sub_ns_nid].helper.\
                                         ns_epid_to_vnf_nid_and_vnf_epid(sub_ns_epid)
            self.meta.add_topo_ns_combo_endpoint_info(ep_id, sub_ns_nid, sub_ns_epid, 
                                                     vnf_nid, vnf_epid)
        
        ######## generat the sub ns csar info #########

        for sub_ns_nid in self.ns_combo_f['SubNsFlavors'].keys():
            self.sub_ns_csar_packer[sub_ns_nid].gen_csar_pack()
            csar_path = os.path.abspath(self.sub_ns_csar_packer[sub_ns_nid].get_csar_pack_path())
            tmp, csar_name = os.path.split(csar_path)
            sysstr = platform.system()
            if sysstr == 'Linux':
                print self.NS_COMBO_FLAVOR_DIR
                os.system('cp ' + csar_path + ' ' + self.NS_COMBO_FLAVOR_DIR)
            elif sysstr == 'Windows':
                os.system('copy ' + csar_path + ' ' + self.NS_COMBO_FLAVOR_DIR)
            self.meta.add_sub_ns_csar_info(sub_ns_nid, csar_name)


        ######## generate the vnf sharing policies  ########

        p_info = self.ns_combo_f['Policies']['vnfSharingPolicies']
        for vsp_id in self.ns_combo_sub['SubscribedPolicies'].get('vnfSharingPolicies', []):
            loc = p_info.get(vsp_id, {})
            self.meta.add_vnf_sharing_policy(vsp_id, \
                                             loc.get('referedSubNsNodeId', None), \
                                             loc.get('referedPolicyId', None))

        ######## generate the service exposure policies  ########

        p_info = self.ns_combo_f['Policies']['serviceExposurePolicies']
        for sep_id in self.ns_combo_sub['SubscribedPolicies'].get('serviceExposurePolicies', []):
            loc = p_info.get(sep_id, {})
            self.meta.add_serv_exposure_policy(sep_id, \
                                             loc.get('referedSubNsNodeId', None), \
                                             loc.get('referedPolicyId', None))
    
        ######## generate the property exposure policies  ########

        p_info = self.ns_combo_f['Policies']['propertyExposurePolicies']
        for pep_id in self.ns_combo_sub['SubscribedPolicies'].get('propertyExposurePolicies', []):
            loc = p_info.get(pep_id, {})
            self.meta.add_prop_exposure_policy(pep_id, \
                                               loc.get('referedSubNsNodeId', None), \
                                               loc.get('referedPolicyId', None), \
                                               loc.get('connectedSubNsNodeId', None), \
                                               loc.get('connectedSubNsEndPointId', None))
        
        ######## generate the scaling policies  ########

        p_info = self.ns_combo_f['Policies']['scalingPolicies']
        for sp_id in self.ns_combo_sub['SubscribedPolicies'].get('scalingPolicies', []):
            loc = p_info.get(sp_id, {})
            self.meta.add_scaling_policy(sp_id, \
                                             loc.get('referedSubNsNodeId', None), \
                                             loc.get('referedPolicyId', None))

    def gen_ns_combo_pack(self):
        meta_path = os.path.join(self.NS_COMBO_FLAVOR_DIR, 'metadata.yaml')
        f = open(meta_path, 'wb')
        yaml_dump(self.meta.get_meta(), f, default_flow_style=False)
        f.close()
        os.chdir(self.NS_COMBO_PARENT_DIR)
        self.NS_COMBO_FALVOR_PACK = os.path.join(self.NS_COMBO_PARENT_DIR, self.NS_COMBO_FALVOR_NAME + '.tar.gz')
        sysstr = platform.system()
        if sysstr == 'Linux':
            os.system('tar -zcf ' + self.NS_COMBO_FALVOR_PACK + ' ' + self.NS_COMBO_FALVOR_NAME)
        elif sysstr == 'Windows':
            os.system('tar zcf ' + self.NS_COMBO_FALVOR_PACK + ' ' + self.NS_COMBO_FALVOR_NAME)
        os.chdir(self.MAIN_DIR)

    def get_ns_combo_pack_path(self):
        return self.NS_COMBO_FALVOR_PACK

if __name__ == '__main__':
    packer = NsComboPacker()
    packer.gen_ns_combo_pack()
    print packer.get_ns_combo_pack_path()
