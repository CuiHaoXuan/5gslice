#   model class for helper meta.
#   The helper read the design model, generates the mapper between identifiers,
#   and provide method to obtain information according to kinds of input identifier

import re
import logging
import os
import sys
from collections import OrderedDict

#logging.basicConfig(filename='csarHelper.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
#log = logging.getLogger('csarHelper')

class CsarHelper(object):
    
    def __init__(self, ns_f, ns_t,
                       vnf_r_list, vnf_t_list,
                       vnfc_r_list, vnfc_t_list):
        
        '''
        
        input design materials to generate the csar helper,
        each input material is either an ordereddict or a list of
        ordereddicts loaded from the related yaml/json files

        the input materials must be invariant
        
        '''

        self.material = OrderedDict()
        #   self.material['nsFlavorSubscribe'] = ns_f_sub
        self.material['nsFlavorDesign'] = ns_f
        self.material['nsType'] = ns_t
        self.material['vnfRelationshipTypeList'] = vnf_r_list
        self.material['vnfTypeList'] = vnf_t_list
        self.material['vnfcRelationshipTypeList'] = vnfc_r_list
        self.material['vnfcTypeList'] = vnfc_t_list
        
        self.helper = OrderedDict()
        self.helper['basciInfo'] = self._gen_basic_info()
        self.helper['vnfTypeIdUsedList'] = self._gen_vnf_tid_used_list()
        self.helper['vnfTypeIdToMaterial'] = self._gen_vnf_tid_to_mat()
        self.helper['vnfcTypeIdUsedList'] = self._gen_vnfc_tid_used_list()
        self.helper['vnfcTypeIdToMaterial'] = self._gen_vnfc_tid_to_mat()
        self.helper['vnfNodeIdToTypeId'] = self._gen_vnf_nid_to_tid()
        self.helper['vnfcNodeIdToTypeId'] = self._gen_vnfc_nid_to_tid()
        self.helper['vnfRelationIdUsedList'] = self._gen_vnf_rel_tid_used_list()
        self.helper['vnfRelationIdToMaterial'] = self._gen_vnf_rel_tid_to_mat()
        self.helper['vnfcRelationIdUsedList'] = self._gen_vnfc_rel_tid_used_list()
        self.helper['vnfcRelationIdToMaterial'] = self._gen_vnfc_rel_tid_to_mat()

    def _gen_basic_info(self):

        '''
        generate the basic information of the csar 
        as a dict including the following keys:
            'nsTypeId'
            'nsFlavorId'
            'version'
            'vendor'
            'nsFlavorDesc'
        '''
        try:
            b_info = OrderedDict()
            b_info.update(self.material['nsFlavorDesign']['Info'])
            if 'description' in b_info:
                b_info['nsFlavorDesc'] = b_info.pop('description')
            #   b_info.update(self.material['nsFlavorSubscribe']['SubscriberInfo'])
            #   if 'description' in b_info:
            #       b_info['subscriberDesc'] = b_info.pop('description')
            return b_info
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
        
    def _gen_vnf_tid_used_list(self):

        ''' 
        generate vnf type id list actually used in the ns,

        '''
        try:
            tid_list = []
            vnf_nodes = self.material['nsType']['VnfNodes']
            for nid, tid in vnf_nodes.items():
                tid_list.append(tid['vnfTypeId'])
            return list(set(tid_list))
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def _gen_vnf_tid_to_mat(self):

        ''' 
        generate a dict with the key as the vnf type id,
        and the value as the vnf type material, only the vnf types
        actually used in the ns are included:
            (vnfTypeId): material

        '''
        try:
            tid_to_mat = OrderedDict()
            for t in self.material['vnfTypeList']:
                tid_to_mat[t['Info']['vnfTypeId']] = t
            d_set = set(tid_to_mat.keys()).difference(set(self.helper['vnfTypeIdUsedList']))
            for tid in d_set:
                tid_to_mat.pop(tid)
            return tid_to_mat
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
        
    def _gen_vnfc_tid_used_list(self):

        ''' 
        generate vnfc type id list actually used in the ns,

        '''
        try:
            tid_list = []
            for vnf_t in self.helper['vnfTypeIdToMaterial'].values():
                vnfc_nodes = vnf_t['VnfcNodes']
                for nid, tid in vnfc_nodes.items():
                    tid_list.append(tid['vnfcTypeId'])
            return list(set(tid_list))
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def _gen_vnfc_tid_to_mat(self):

        ''' 
        generate a dict with the key as the vnfc type id,
        and the value as the vnfc type material, only the vnfc types
        actually used in the ns are included:
            (vnfcTypeId): material

        '''
        try:
            tid_to_mat = OrderedDict()
            for t in self.material['vnfcTypeList']:
                tid_to_mat[t['Info']['vnfcTypeId']] = t
            d_set = set(tid_to_mat.keys()).difference(set(self.helper['vnfcTypeIdUsedList']))
            for tid in d_set:
                tid_to_mat.pop(tid)
            return tid_to_mat
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def _gen_vnf_rel_tid_used_list(self):

        ''' 
        generate vnf relation type id list actually used in the ns,

        '''
        try:
            tid_list = []
            conns = self.material['nsType']['Connections']
            for conid, v in conns.items():
                tid_list.append(v['vnfRelationshipTypeId'])
            return list(set(tid_list))
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def _gen_vnf_rel_tid_to_mat(self):

        ''' 
        generate a dict with the key as the vnf relation type id,
        and the value as the vnf relation type material, only the vnf relation types
        actually used in the ns are included:
            (vnfRelationshipTypeId): material

        '''
        try:
            tid_to_mat = OrderedDict()
            for t in self.material['vnfRelationshipTypeList']:
                tid_to_mat[t['Info']['vnfRelationshipTypeId']] = t
            d_set = set(tid_to_mat.keys()).difference(set(self.helper['vnfRelationIdUsedList']))
            for tid in d_set:
                tid_to_mat.pop(tid)
            return tid_to_mat
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def _gen_vnfc_rel_tid_used_list(self):

        ''' 
        generate vnfc relation type id list actually used in the ns,

        '''
        try:
            tid_list = []
            for vnf_t in self.helper['vnfTypeIdToMaterial'].values():
                conns = vnf_t['Connections']
                for conid, v in conns.items():
                    tid_list.append(v['vnfcRelationshipTypeId'])
            return list(set(tid_list))
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def _gen_vnfc_rel_tid_to_mat(self):

        ''' 
        generate a dict with the key as the vnfc relation type id,
        and the value as the vnfc relation type material, only the vnfc relation types
        actually used in the ns are included:
            (vnfcRelationshipTypeId): material

        '''
        try:
            tid_to_mat = OrderedDict()
            for t in self.material['vnfcRelationshipTypeList']:
                tid_to_mat[t['Info']['vnfcRelationshipTypeId']] = t
            d_set = set(tid_to_mat.keys()).difference(set(self.helper['vnfcRelationIdUsedList']))
            for tid in d_set:
                tid_to_mat.pop(tid)
            return tid_to_mat
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def _gen_vnf_nid_to_tid(self):

        '''
        get the vnf types used actually used in the ns,
        a map is return with the key as the vnf node id,
        and the value as the vnf type id, i.e.:
            (vnfNodeId): (vnfTypeId)

        '''
        try:
            nid_to_tid_map = {}
            vnf_nodes = self.material['nsType']['VnfNodes']
            for nid, tid in vnf_nodes.items():
                nid_to_tid_map[nid] = tid['vnfTypeId']
            return nid_to_tid_map
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def _gen_vnfc_nid_to_tid(self):

        '''
        get the vnfc types used actually used in the ns,
        a map is returned consists of follows:
            (vnfTypeId):
                (vnfcNodeId): (vnfcTypeId)

        '''
        try:
            nid_to_tid_map = {}
            for tid, mat in self.helper['vnfTypeIdToMaterial'].items():
                nid_to_tid_map[tid] = {}
                vnfc_nodes = mat['VnfcNodes']
                for nid, ctid in vnfc_nodes.items():
                    nid_to_tid_map[tid][nid] = ctid['vnfcTypeId']
            return nid_to_tid_map
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None

    
    
    def get_helper(self):
        return self.helper

    def get_material(self):
        return self.material

    def get_basic_info(self):
        return self.helper['basciInfo']

    def get_vnf_nid_list(self):

        '''
        get vnf node id list

        '''
        try:
            return self.helper['vnfNodeIdToTypeId'].keys()
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnfc_nid_list_by_vnf_tid(self, vnf_tid):

        '''
        get vnfc node id list by vnf type id,
        only the vnf types used in the ns are available

        '''
        try:
            vnf_mat = self.helper['vnfTypeIdToMaterial'][vnf_tid]
            return vnf_mat['VnfcNodes'].keys()
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnfc_nid_list_by_vnf_nid(self, vnf_nid):

        '''
        get vnfc node id list by vnf node id,
        only the vnf types used in the ns are available

        '''
        try:
            vnf_tid = self.helper['vnfNodeIdToTypeId'][vnf_nid]
            return self.get_vnfc_nid_list_by_vnf_tid(vnf_tid)
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnfc_interface_id_list(self, vnfc_tid):

        '''
        get interface id list of a vnfc type,
        only the vnfc types used in the ns are available

        '''
        try:
            return self.helper['vnfcTypeIdToMaterial'][vnfc_tid]['ConfigurableProperties'].keys()
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnfc_prop_id_list(self, vnfc_tid):

        '''
        get configurable property id list of a vnfc type,
        only the vnfc types used in the ns are available

        '''
        try:
            return self.helper['vnfcTypeIdToMaterial'][vnfc_tid]['Interfaces'].keys()
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_service_exposure_policies_mat(self):

        '''
        get the service exposure policies material

        '''
        try:
            return self.material['nsType']['Policies']['serviceExposurePolicies']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None

    def get_property_exposure_policies_mat(self):

        '''
        get the property exposure policies material

        '''
        try:
            return self.material['nsType']['Policies']['propertyExposurePolicies']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_service_exposure_mat(self, vnf_nid, serv_id):

        '''
        get the service exposure material by vnf node id and service id

        '''
        try:
            return self.get_vnf_t_mat_by_vnf_nid(vnf_nid)\
                                            ['ServiceExposures'][serv_id]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnf_sharing_policies_mat(self):

        '''
        get the vnf sharing policies material

        '''
        try:
            return self.material['nsType']['Policies']['vnfSharingPolicies']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_scale_policies_mat(self):

        '''
        get the scaling policies material

        '''
        try:
            return self.material['nsType']['Policies']['scalingPolicies']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnf_t_mat_by_vnf_nid(self, vnf_nid):

        '''
        get vnf type material by vnf node id

        '''
        try:
            vnf_tid = self.helper['vnfNodeIdToTypeId'][vnf_nid]
            return self.helper['vnfTypeIdToMaterial'][vnf_tid]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnf_t_monitor_mat_by_vnf_nid(self, vnf_nid):

        '''
        get vnf type monitor material by vnf node id

        '''
        try:
            return self.get_vnf_t_mat_by_vnf_nid(vnf_nid)['MonitorOptions']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnf_t_scale_mat_by_vnf_nid(self, vnf_nid):

        '''
        get scaling info material in vnf type by vnf node id

        '''
        try:
            return self.get_vnf_t_mat_by_vnf_nid(vnf_nid)['ScalingInfo']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None

    def get_vnf_t_scale_group_mat_by_vnf_nid_and_scale_opid(self, vnf_nid, op_id):

        '''
        get scaling group material in vnf type by vnf node id and scaling operation id

        '''
        try:
            scale_mat = self.get_vnf_t_mat_by_vnf_nid(vnf_nid)['ScalingInfo']
            group_id = scale_mat['scalingOperations'].get(op_id, {}).get('targetGroup', None)
            return scale_mat['scalingGroups'].get(group_id, None)
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None   
    
    def get_vnfc_t_mat_by_vnf_tid_vnfc_nid(self, vnf_tid, vnfc_nid):

        '''
        get vnfc type material by vnf type id and vnfc node id

        '''
        try:
            vnfc_tid = self.helper['vnfcNodeIdToTypeId'][vnf_tid][vnfc_nid]
            return self.helper['vnfcTypeIdToMaterial'][vnfc_tid]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None

    def get_vnfc_t_mat_by_vnf_nid_vnfc_nid(self, vnf_nid, vnfc_nid):

        '''
        get vnfc type material by vnf node id and vnfc node id

        '''
        try:
            vnf_tid = self.helper['vnfNodeIdToTypeId'][vnf_nid]
            return self.get_vnfc_t_mat_by_vnf_tid_vnfc_nid(vnf_tid, vnfc_nid)
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnfc_t_if_mat_by_vnf_tid_vnfc_nid(self, vnf_tid, vnfc_nid):

        '''
        get vnfc type interface material by vnf type id and vnfc node id

        '''
        try:
            return self.get_vnfc_t_mat_by_vnf_tid_vnfc_nid(vnf_tid, vnfc_nid)['Interfaces']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnfc_t_if_mat_by_vnf_nid_vnfc_nid(self, vnf_nid, vnfc_nid):

        '''
        get vnfc type interface material by vnf node id and vnfc node id

        '''
        try:
            return self.get_vnfc_t_mat_by_vnf_nid_vnfc_nid(vnf_nid, vnfc_nid)['Interfaces']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnfc_t_prop_mat_by_vnf_nid(self, vnf_nid, vnfc_nid):

        '''
        get vnfc type properties material by vnf node id and vnfc node id

        '''
        try:
            return self.get_vnfc_t_mat_by_vnf_nid_vnfc_nid(vnf_nid, vnfc_nid)['ConfigurableProperties']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnfc_t_arti_mat_by_vnf_nid(self, vnf_nid, vnfc_nid):

        '''
        get vnfc type artifact material by vnf node id and vnfc node id

        '''
        try:
            return self.get_vnfc_t_mat_by_vnf_nid_vnfc_nid(vnf_nid, vnfc_nid)['DeploymentArtifact']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def get_vnfc_t_deploy_flavor_mat_by_vnf_nid(self, vnf_nid, vnfc_nid):

        '''
        get vnfc type deployment flavor material by vnf node id and vnfc node id

        '''
        try:
            return self.get_vnfc_t_mat_by_vnf_nid_vnfc_nid(vnf_nid, vnfc_nid)['DeploymentFlavorConstraints']['hostFlavorDesc']
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def vnf_nid_to_tid(self, vnf_nid):

        '''
        get vnf type id by vnf node id

        '''
        try:
            return self.helper['vnfNodeIdToTypeId'][vnf_nid]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None

    def vnf_epid_to_vnfc_nid_and_vnfc_epid_by_vnf_nid(self, vnf_nid, ep_id):

        '''
        get vnfc node id and vnfc endpoint id by vnf node id and vnf endpoint id

        '''
        try:
            ep_mat = self.get_vnf_t_mat_by_vnf_nid(vnf_nid)['EndPoints']
            vnfc_nid = ep_mat[ep_id]['vnfcNodeId']
            vnfc_epid = ep_mat[ep_id]['vnfcEndPointId']
            return (vnfc_nid, vnfc_epid)
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return (None, None)
    
    def vnfc_nid_to_tid_by_vnf_tid(self, vnf_tid, vnfc_nid):

        '''
        get vnfc type id by vnf type id and vnfc node id,
        only the vnf types used in the ns are available

        '''
        try:
            return self.helper['vnfcNodeIdToTypeId'][vnf_tid][vnfc_nid]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def vnfc_nid_to_tid_by_vnf_nid(self, vnf_nid, vnfc_nid):
        
        '''
        get vnfc type id by vnf node id and vnfc node id

        '''
        try:
            vnf_tid = self.helper['vnfNodeIdToTypeId'][vnf_nid]
            return vnfc_nid_to_tid_by_vnf_tid(vnf_tid, vnfc_nid)
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None

    def vnf_nid_to_epid_by_relation_tid(self, vnf_rel_id, vnf_nid):
        
        '''
        get vnf endpoint id by vnf node id, vnf relationship id

        '''
        try:
            rel_mat_src = self.helper['vnfRelationIdToMaterial'][vnf_rel_id]['SourceEndType']
            rel_mat_tgt = self.helper['vnfRelationIdToMaterial'][vnf_rel_id]['TargetEndType']
            mapper = {}
            mapper[rel_mat_src['vnfTypeId']] = rel_mat_src['vnfEndPointId']
            mapper[rel_mat_tgt['vnfTypeId']] = rel_mat_tgt['vnfEndPointId']
            vnf_tid = self.vnf_nid_to_tid(vnf_nid)
            return mapper[vnf_tid]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def vnfc_nid_to_epid_by_relation_tid_vnf_tid(self, vnfc_rel_id, vnf_tid, vnfc_nid):
        
        '''
        get vnfc endpoint id by vnfc node id, vnfc relationship id and vnf type id

        '''
        try:
            rel_mat_src = self.helper['vnfcRelationIdToMaterial'][vnfc_rel_id]['SourceEndType']
            rel_mat_tgt = self.helper['vnfcRelationIdToMaterial'][vnfc_rel_id]['TargetEndType']
            mapper = {}
            mapper[rel_mat_src['vnfcTypeId']] = rel_mat_src['vnfcEndPointId']
            mapper[rel_mat_tgt['vnfcTypeId']] = rel_mat_tgt['vnfcEndPointId']
            vnfc_tid = self.vnfc_nid_to_tid_by_vnf_tid(vnf_tid, vnfc_nid)
            return mapper[vnfc_tid]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def vnfc_nid_to_epid_by_relation_tid_vnf_nid(self, vnfc_rel_id, vnf_nid, vnfc_nid):
        
        '''
        get vnfc endpoint id by vnfc node id, vnfc relationship id and vnf node id

        '''
        try:
            rel_mat_src = self.helper['vnfcRelationIdToMaterial'][vnfc_rel_id]['SourceEndType']
            rel_mat_tgt = self.helper['vnfcRelationIdToMaterial'][vnfc_rel_id]['TargetEndType']
            mapper = {}
            mapper[rel_mat_src['vnfcTypeId']] = rel_mat_src['vnfcEndPoint']
            mapper[rel_mat_tgt['vnfcTypeId']] = rel_mat_tgt['vnfcEndPoint']
            vnfc_tid = self.vnfc_nid_to_tid_by_vnf_nid(vnf_nid, vnfc_nid)
            return mapper[vnfc_tid]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def ns_epid_to_vnf_nid_and_vnf_epid(self, ep_id):

        '''
        get vnf node id and vnf endpoint id by ns endpoint id

        '''
        #try:
        ep_mat = self.material['nsType']['EndPoints']
        vnf_nid = ep_mat[ep_id]['vnfNodeId']
        vnf_epid = ep_mat[ep_id]['vnfEndPointId']
        return (vnf_nid, vnf_epid)
        #except Exception, e:
         #   print Exception, ':', e, sys._getframe().f_code.co_name
          #  return (None, None)
    
    def get_depend_prop_by_vnf_nid(self, vnf_nid, vnfc_nid, prop_id):

        '''
        get the dependent vnf node id, vnfc node id and configurable property id 
        according to the property mappings in vnf and ns
        
        '''
        try:
            vnf_t_mat = self.get_vnf_t_mat_by_vnf_nid(vnf_nid)['VnfcPropertiesMapping']
            #print vnf_t_mat
            mapper = {}
            for v in vnf_t_mat.values():
                mapper[(v['sourceProperty']['vnfcNodeId'], \
                    v['sourceProperty']['propertyId'])] = \
                   [v['multiInstanceOption'], \
                    v['targetProperty']['vnfcNodeId'], \
                    v['targetProperty']['propertyId']]
            mul_inst_opt, dep_vnfc_nid, dep_prop_id = mapper.get((vnfc_nid, prop_id), [None, None, None])
            if not dep_vnfc_nid:
                ns_t_mat = self.material['nsType']['VnfPropertiesMapping']
                mapper = {}
                for v in ns_t_mat.values():
                    mapper[(v['sourceProperty']['vnfNodeId'], \
                            v['sourceProperty']['vnfcNodeId'], \
                            v['sourceProperty']['propertyId'])] = \
                           [v['multiInstanceOption'], \
                            v['targetProperty']['vnfNodeId'], \
                            v['targetProperty']['vnfcNodeId'], \
                            v['targetProperty']['propertyId']]
             #       print 'csar helper aaaaaaaaaaaaaa'
              #      print 'get dependent prop '
               #     print 'source: ', vnf_nid, vnfc_nid, prop_id
                return mapper.get((vnf_nid, vnfc_nid, prop_id), [None, None, None, None])
            else:
                return [mul_inst_opt, vnf_nid, dep_vnfc_nid, dep_prop_id]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return (None, None, None)
    
    def get_prop_value(self, vnf_nid, vnfc_nid, prop_id):

        '''
        get configurable property value described in ns flavor
        by vnf node id, vnfc node id and property id.
        the property mapping will be auto-handled

        '''
        try:
            act_vnf_nid, act_vnfc_nid, act_prop_id = vnf_nid, vnfc_nid, prop_id
            #print 'csar helper aaaaaaaaaaaaaaa'
            #print 'get prop value '
            #print 'act: ', act_vnf_nid, act_vnfc_nid, act_prop_id
            mul_inst_opt, depend_vnf_nid, depend_vnfc_nid, depend_prop_id = self.get_depend_prop_by_vnf_nid(
                                                                       vnf_nid, vnfc_nid, prop_id)
            #print 'depend: ', depend_vnf_nid, depend_vnfc_nid, depend_prop_id
            if depend_vnfc_nid:
                act_vnf_nid, act_vnfc_nid, act_prop_id = depend_vnf_nid, depend_vnfc_nid, depend_prop_id
            prop_val_mat = self.material['nsFlavorDesign']['VnfcConfigurationFlavors']
            #print "DEBUG : ",self.material
            return prop_val_mat[act_vnf_nid][act_vnfc_nid][act_prop_id]['value']
            #act_val = val
            '''
            val = val.strip('{').strip('}').strip()
            if val.startswith('get_'):
                fun, epid = val.split(':')
                epid = epid.strip()
                tmp, attr = fun.split('_')
                act_val = '{get_attr: ' + 'CP_' + \
                                      act_vnfc_nid + '_' + \
                                      epid + ', ' + attr + '}'
            '''
            #return act_val
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None

    def get_prop_id_list_by_interface(self, vnf_nid, vnfc_nid, if_id):

        '''
        get the involved property id list by vnf node id, vnfc node id and interface id

        '''
        try:
            mat = self.get_vnfc_t_if_mat_by_vnf_nid_vnfc_nid(vnf_nid, vnfc_nid)[if_id]
            if_format = mat['format']
            return [n.split('}}')[0] for n in if_format.split('{{') if '}}' in n]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
        
    
    def get_mon_prop_value(self, vnf_nid, mon_id, para_id):

        '''
        get the value of a configurable parameter by vnf node id, 
        monitor option id and parameter id

        '''
        try:
            prop_val_mat = self.material['nsFlavorDesign']['VnfMonitorFlavors']\
                                                          ['monitorConfigurationFlavors']
            return prop_val_mat[vnf_nid][mon_id][para_id]['value']
            
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None       
    
    def get_prop_id_list_by_monitor_interface(self, vnf_nid, mon_id, if_id):

        '''
        get the involved property id list of a interface for a monitor option,
        by vnf node id, monitor id and interface id

        '''
        try:
            mat = self.get_vnf_t_monitor_mat_by_vnf_nid(vnf_nid)\
                                              [mon_id]['interfaces'][if_id]
            if_format = mat['format']
            return [n.split('}}')[0] for n in if_format.split('{{') if '}}' in n]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def deploy_abs_path_trans(self, root_dir, abs_path):

        '''
        translate the abs path format containing in-build express of "{{get_rootDir: filePack}}"
        into a direct path format by replace the in-build express with the root_dir

        '''
        try:
            if not abs_path.startswith('{{get_rootDir: filePack}}'):
                return abs_path
            rel_path = abs_path.replace('{{get_rootDir: filePack}}', '')
            return os.path.join(root_dir, rel_path)
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None
    
    def trans_interface_format(self, vnf_nid, vnfc_nid, if_id):

        '''
        translate the interface format indicated by the vnf node id, 
        vnfc node id and interface id, the parameter in the format will be
        replaced with the actual property's value,
        return the translated format

        '''
        try:
            if_format = self.get_vnfc_t_if_mat_by_vnf_nid_vnfc_nid(vnf_nid, vnfc_nid)\
                             [if_id]['format']
            props = [n.split('}}')[0] for n in if_format.split('{{') if '}}' in n]
            cnt = len(props)
            fun = self.get_prop_value
            prop_vals = map(fun, [vnf_nid] * cnt, [vnfc_nid] * cnt, props)
            mapper = dict(zip(props, prop_vals))
            if_format = if_format.replace('{', '').replace('}', '')
            for k, v in mapper.items():
                if_format = if_format.replace(k, v)
            return if_format
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
            return None

    def get_scale_policy_mat_by_vnf_nid_and_scale_opid(self, vnf_nid, op_id):

        '''
        get the scaling policy material by vnf node id and scaling operation id

        '''
        ns_scale_mat = self.get_scale_policies_mat()
        for spid, sp_v in ns_scale_mat.items():
            op_used_list = [(act['involvedEntityId'], act['scalingOpId']) \
                                  for act in sp_v['actions'].values() \
                                  if act['involvedEntityType'] == 'vnf']
            if (vnf_nid, op_id) in op_used_list:
                return sp_v
        
        return None
    
    def is_vnf_scale_op_used(self, vnf_nid, scale_op_id):

        '''
        check whether the vnf scaling option is used in any scaling policy

        '''
        ns_scale_mat = self.get_scale_policies_mat()
        op_used_list = [(act['involvedEntityId'], act['scalingOpId']) \
                                  for act in ns_scale_mat.values()['actions'].values() \
                                  if act['involvedEntityType'] == 'vnf']
        return (vnf_nid, scale_op_id) in op_used_list

    def get_used_alarm_list(self):

        '''
        return the list of the actually used alarm ids

        '''
        
        sp_mat = self.material['nsType']['Policies']['scalingPolicies']
        return list(set([n['alarmId'] for n in sp_mat.keys()]))
