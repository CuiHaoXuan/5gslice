#   model class for CSAR TOSCA vnfd

import re
import logging
import os
from collections import OrderedDict

#logging.basicConfig(filename='csarVnfd.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
#log = logging.getLogger('csarVnfd')

class ToscaVnfd(object):
    
    def __init__(self, nid, ver, vendor, desc):
        
        '''
        parameters:
            nid: vnfNodeId
            ver: version
            vendor: vendor
            desc: description
        '''

        self.model = OrderedDict()
        self.model['tosca_definitions_version'] = 'tosca_simple_profile_for_nfv_1_0'

        self.model['description'] = desc

        self.model['metadata'] = OrderedDict()
        self.model['metadata']['id'] = nid
        self.model['metadata']['vendor'] = vendor
        self.model['metadata']['version'] = ver

        self.model['node_types'] = OrderedDict()

        self.model['node_types']['tosca.nodes.nfv.VNF.' + nid] = OrderedDict()
        self.model['node_types']['tosca.nodes.nfv.VNF.' + nid]\
                                ['derived_from'] = 'tosca.nodes.nfv.VNF'
        self.model['node_types']['tosca.nodes.nfv.VNF.' + nid]\
                                ['requirements'] = OrderedDict()

        self.model['node_types']['tosca.nodes.nfv.VDU.Customized'] = OrderedDict()
        self.model['node_types']['tosca.nodes.nfv.VDU.Customized']\
                                ['derived_from'] = 'tosca.nodes.nfv.VDU'
        self.model['node_types']['tosca.nodes.nfv.VDU.Customized']\
                                ['properties'] = OrderedDict()
        self._add_prop_def_to_vdu_type('vim_type', 'vim type for the current vdu')
        self._add_prop_def_to_vdu_type('flavor_type', 'flavor type used in the vim type for the vdu')
        self._add_prop_def_to_vdu_type('os_type', 'os type for the current vdu')
        self._add_prop_def_to_vdu_type('image_name', 'image file name used for the vdu')
        self._add_prop_def_to_vdu_type('image_location', 'location of the image file')

        self.model['topology_template'] = OrderedDict()

        self.model['topology_template']['inputs'] = OrderedDict()

        self.model['topology_template']['substitution_mappings'] = OrderedDict()
        self.model['topology_template']['substitution_mappings']\
                                       ['node_type'] = 'tosca.nodes.nfv.VNF.' + nid
        self.model['topology_template']['substitution_mappings']\
                                       ['requirements'] = OrderedDict()
        
        self.model['topology_template']['node_templates'] = OrderedDict()

        self.model['topology_template']['policies'] = OrderedDict()




    def _add_prop_def_to_vdu_type(self, prop_n, desc, t='string'):
        self.model['node_types']['tosca.nodes.nfv.VDU.Customized']\
                                ['properties']\
                                [prop_n] = OrderedDict()
        prop_info = self.model['node_types']['tosca.nodes.nfv.VDU.Customized']\
                                ['properties']\
                                [prop_n]
        prop_info['type'] = t
        prop_info['description'] = desc
        

    def _add_input(self, para):
        input_info = self.model['topology_template']['inputs']
        input_info[para] = OrderedDict()
        input_info[para]['type'] = 'string'
    
    def _add_node_type_req_vl(self, vnf_epid):

        '''
        add a vl requirement to the vnf node defined in the node types

        '''
        nt_req_root = self.model['node_types']['tosca.nodes.nfv.VNF.' + \
                                               self.model['metadata']['id']]\
                                              ['requirements']
        nt_req_root['virtualLink_{{' + vnf_epid + '}}'] = OrderedDict()
        nt_req_root['virtualLink_{{' + vnf_epid + '}}']['capability'] = \
                                 'tosca.capabilities. nfv.VirtualLinkable'
        nt_req_root['virtualLink_{{' + vnf_epid + '}}']['relationship'] = \
                                 'tosca.relationships.nfv.VirtualLinksTo'
    
    def _add_subs_mapping_req_vl(self, vnf_epid, vnfc_nid, vnfc_epid):

        '''
        add a vl requirement to the substitution mappings

        '''
        sm_req_root = self.model['topology_template']['substitution_mappings']\
                                                     ['requirements']
        sm_req_root['virtualLink_{{' + vnf_epid + '}}'] = '[CP_{{' + vnfc_nid + '}}_{{' + \
                                                          vnfc_epid + '}}, virtualLink]'
    
    def add_vdu_node(self, vnfc_nid, 
                           vim_t='openstack', flavor_t='m1.tiny', os_t='ubuntu14.04', 
                           image_n=None, image_l=None):
        '''
        add vdu node, and return the vdu id
        '''
        self.model['topology_template']['node_templates']\
                                ['VDU_{{' + vnfc_nid + '}}'] = OrderedDict()
        vdu_root = self.model['topology_template']['node_templates']\
                                                  ['VDU_{{' + vnfc_nid + '}}']
        vdu_root['type']= 'tosca.nodes.nfv.VDU.Customized'
        vdu_root['properties'] = OrderedDict()
        
        prop = vdu_root['properties']
        prop['vim_type'] = vim_t
        prop['flavor_type'] = flavor_t
        prop['os_type'] = os_t
        prop['image_name'] = image_n
        prop['image_location'] = image_l
        
        #vdu_root['artifacts'] = OrderedDict()
        #arti = vdu_root['artifacts']
        #arti['pack_type'] = pack_t
        #arti['root_dir'] = arti_root_dir
        #para_n = 'arti_file_' + vnfc_nid
        #arti['get_file'] = None

        #vdu_root['interfaces'] = OrderedDict()
        #vdu_root['interfaces']['customized'] = []
        #if_info = vdu_root['interfaces']['customized']
        #if_info.extend(interface_list)

        return 'VDU_{{' + vnfc_nid + '}}'

    def add_cp_of_vnf_ep(self, vnf_epid, vnfc_nid, vnfc_epid):

        '''
        this function add a cp for vnf endpoint, and auto-add
        the related requirements in substitution_mappings and node type, 
        return the cp id and related vdu id

        '''
        cp_root = self.model['topology_template']['node_templates'].setdefault(
                                        'CP_{{' + vnfc_nid + '}}_{{' + vnfc_epid + '}}', OrderedDict())
        cp_root['type'] = 'tosca.nodes.nfv.CP'
        req_info = cp_root.setdefault('requirements', OrderedDict())
        req_info['virtualbinding'] = 'VDU_{{' + vnfc_nid + '}}'
        
        self._add_node_type_req_vl(vnf_epid)
        self._add_subs_mapping_req_vl(vnf_epid, vnfc_nid, vnfc_epid)

        return ('CP_{{' + vnfc_nid + '}}_{{' + vnfc_epid + '}}', 'VDU_{{' + vnfc_nid + '}}')
            
    def add_cp_in_connection(self, conn_id, vnfc_nid, vnfc_epid):

        '''
        this function add a cp for one end of a vnfc connection, 
        return the cp id

        '''
        cp_root = self.model['topology_template']['node_templates'].setdefault(
                                        'CP_{{' + vnfc_nid + '}}_{{' + vnfc_epid + '}}', OrderedDict())
        cp_root['type'] = 'tosca.nodes.nfv.CP'
        req_info = cp_root.setdefault('requirements', OrderedDict())
        req_info['virtualbinding'] = 'VDU_{{' + vnfc_nid + '}}'
        req_vl_info = req_info.setdefault('virtualLink', [])
        req_vl_info.append('internal_VL_{{' + conn_id + '}}')
        return 'CP_{{' + vnfc_nid + '}}_{{' + vnfc_epid + '}}'

    def add_vl_of_connection(self, conn_id):

        '''
        this function add a vl for a vnfc connection

        '''
        self.model['topology_template']['node_templates']\
                                ['internal_VL_{{' + conn_id + '}}'] = OrderedDict()
        self.model['topology_template']['node_templates']\
                                ['internal_VL_{{' + conn_id + '}}']\
                                ['type'] = 'tosca.nodes.nfv.VL.ELAN'

    def add_scaling_policy(self, op_id, s_step, cd,
                                 min_ins, max_ins, d_ins,
                                 *targets):
        '''
        this function add a scaling policy

        '''
        sp = '_'.join(('SP', op_id))
        target = targets[0]
        if int(s_step) > 0:
            sp = sp + target[3:] + '_OUT'
        else:
            sp = sp + target[3:] + '_IN'
        loc = self.model['topology_template']['policies'].setdefault(sp, OrderedDict())
        loc['type'] = 'tosca.policies.Scaling'
        loc = loc.setdefault('properties', OrderedDict())
        loc['increment'] = s_step
        loc['cooldown'] = cd
        loc['min_instances'] = min_ins
        loc['max_instances'] = max_ins
        loc['default_instances'] = d_ins
        loc['targets'] = []
        for t in targets:
            loc['targets'].append(t)
        
        return sp
    
    def get_model(self):
        return self.model
