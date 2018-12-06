#   model class for CSAR TOSCA nsd

import re
import logging
import os
from collections import OrderedDict

#logging.basicConfig(filename='csarNsd.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
#log = logging.getLogger('csarNsd')

class ToscaNsd(object):
    
    def __init__(self, tid, fid, ver, vendor, desc):
        
        '''
        parameters:
            tid: nsTypeId
            fid: nsFlavorId
            ver: version
            vendor: vendor
            desc: description
        '''

        self.model = OrderedDict()
        self.model['tosca_definitions_version'] = 'tosca_simple_profile_for_nfv_1_0'

        self.model['description'] = desc

        self.model['metadata'] = OrderedDict()
        self.model['metadata']['id'] = tid + '_' + fid
        self.model['metadata']['vendor'] = vendor
        self.model['metadata']['version'] = ver

        self.model['imports'] = []

        self.model['topology_template'] = OrderedDict()
        self.model['topology_template']['node_templates'] = OrderedDict()



    def add_import_vnfd(self, vnf_nid):
        # self.model['imports'].append(vnf_nid + '-vnfd.yaml')
        self.model['imports'].append(vnf_nid + '_vnfd.yaml')

    def add_vnf_node(self, vnf_nid):

        '''
        add vnf node and return the vnf node id in nsd

        '''
        self.model['topology_template']['node_templates']\
                                ['VNF_{{' + vnf_nid + '}}'] = OrderedDict()
        vnf_root = self.model['topology_template']['node_templates']\
                                                  ['VNF_{{' + vnf_nid + '}}']
        vnf_root['type']= 'tosca.nodes.nfv.VNF.' + vnf_nid
        vnf_root['requirements'] = OrderedDict()
        return 'VNF_{{' + vnf_nid + '}}'

    def add_vnf_requirements(self, vnf_nid, vnf_epid, other_id):

        '''
        add reqiurements to the vnf node,
        the vnf node need be add first

        '''
        vnf_req = self.model['topology_template']['node_templates']\
                                                  ['VNF_{{' + vnf_nid + '}}']\
                                                  ['requirements']
        vnf_req_vl = vnf_req.setdefault('virtualLink_{{' + vnf_epid + '}}', [])
        vnf_req_vl.append('VL_{{' + other_id + '}}')
    
    def add_cp_of_ns_ep(self, epid, vnf_nid, vnf_epid):

        '''
        this function add a cp for ns endpoint

        '''
        self.model['topology_template']['node_templates']\
                                ['CP_{{' + epid + '}}'] = OrderedDict()
        cp_root = self.model['topology_template']['node_templates']\
                                                 ['CP_{{' + epid + '}}']
        cp_root['type'] = 'tosca.nodes.nfv.CP'
        req_info = cp_root.setdefault('requirements', OrderedDict())
        req_info['virtualLink'] = 'VL_{{' + epid + '}}'
        self.add_vnf_requirements(vnf_nid, vnf_epid, epid)

    def add_vl(self, vl_id):

        '''
        this function add a vl for either vnf connection
        or ns endpoint

        '''
        self.model['topology_template']['node_templates']\
                                ['VL_{{' + vl_id + '}}'] = OrderedDict()
        self.model['topology_template']['node_templates']\
                                ['VL_{{' + vl_id + '}}']\
                                ['type'] = 'tosca.nodes.nfv.VL.ELine'

    def get_model(self):
        return self.model
