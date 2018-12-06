#   model class for NS combo flavor design definition

import re
import logging
from collections import OrderedDict

from common.util.util import get_class_func_name

LOCATOR_SET = ('latency')
SLA_VALUE_TYPE_SET = ('string', 'num', 'list_string', 'list_num')

# logging.basicConfig(filename='nsFlavorDesign.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
# log = logging.getLogger('nsFlavorDesign')

class NsComboFlavorDesign(object):
    
    def __init__(self):
        self.model = OrderedDict()
        self.model['Info'] = OrderedDict()
        self.model['SubNsFlavors'] = OrderedDict()
        self.model['EndPoints'] = OrderedDict()
        self.model['Connections'] = OrderedDict()
        self.model['ServiceLevelAgreementFlavors'] = OrderedDict()
        self.model['Policies'] = OrderedDict()
        self.model['Policies']['vnfSharingPolicies'] = OrderedDict()
        self.model['Policies']['serviceExposurePolicies'] = OrderedDict()
        self.model['Policies']['propertyExposurePolicies'] = OrderedDict()
        self.model['Policies']['scalingPolicies'] = OrderedDict()
        self.model['LocationAwareness'] = OrderedDict()
        self.model['LocationAwareness']['vnfLocations'] = OrderedDict()
        self.model['LocationAwareness']['referencePoints'] = OrderedDict()

    def set_ns_combo_flavor_info(self, flavor_id, 
                 desc, ver='1.0.0', vendor='iaa'):
        self.model['Info']['nsComboFlavorId'] = flavor_id
        self.model['Info']['version'] = ver
        self.model['Info']['vendor'] = vendor
        self.model['Info']['description'] = desc
    
    def add_subns_flavor(self, node_id, ns_t, ns_f):
        loc = self.model['SubNsFlavors'].setdefault(node_id, OrderedDict())
        loc['nsTypeId'] = ns_t
        loc['nsFlavorId'] = ns_f

    def add_endpoint(self, ep_id, subns, ns_ep, desc):
        loc = self.model['EndPoints'].setdefault(ep_id, OrderedDict())
        loc['subNsNodeId'] = subns
        loc['nsEndPointId'] = ns_ep
        loc['description'] = desc
    
    def add_connection(self, con_id, subns_1, ns_ep_1, subns_2, ns_ep_2):
        loc = self.model['Connections'].setdefault(con_id, OrderedDict())
        loc_1 = loc.setdefault('endOne', OrderedDict())
        loc_1['subNsNodeId'] = subns_1
        loc_1['nsEndPointId'] = ns_ep_1
        loc_2 = loc.setdefault('endTwo', OrderedDict())
        loc_2['subNsNodeId'] = subns_2
        loc_2['nsEndPointId'] = ns_ep_2
    
    def add_sla_flavor(self, sla_id, val, desc, val_t='num'):
        try:
            if val_t not in SLA_VALUE_TYPE_SET:
                raise Exception('unknown sla value type: %s' % val_t)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['ServiceLevelAgreementFlavors'].setdefault(sla_id, OrderedDict())
        loc['valueType'] = val_t
        loc['description'] = desc
        loc['value'] = val
    
    def add_vnf_sharing_policy(self, vsp_id, subns, p_id):
        try:
            if subns not in self.model['SubNsFlavors']:
                raise Exception('unknown sub ns node id: %s' % subns)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['Policies']['vnfSharingPolicies'].setdefault(vsp_id, OrderedDict())
        loc['referedSubNsNodeId'] = subns
        loc['referedPolicyId'] = p_id
    
    def add_serv_exposure_policy(self, sep_id, subns, p_id):
        try:
            if subns not in self.model['SubNsFlavors']:
                raise Exception('unknown sub ns node id: %s' % subns)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['Policies']['serviceExposurePolicies'].setdefault(sep_id, OrderedDict())
        loc['referedSubNsNodeId'] = subns
        loc['referedPolicyId'] = p_id
    
    def add_prop_exposure_policy(self, pep_id, subns, p_id, conn_subns, conn_epid):
        try:
            if subns not in self.model['SubNsFlavors']:
                raise Exception('unknown sub ns node id: %s' % subns)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['Policies']['propertyExposurePolicies'].setdefault(pep_id, OrderedDict())
        loc['referedSubNsNodeId'] = subns
        loc['referedPolicyId'] = p_id
        loc['connectedSubNsNodeId'] = conn_subns
        loc['connectedSubNsEndPointId'] = conn_epid
    
    def add_scaling_policy(self, sp_id, subns, p_id):
        try:
            if subns not in self.model['SubNsFlavors']:
                raise Exception('unknown sub ns node id: %s' % subns)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['Policies']['scalingPolicies'].setdefault(sp_id, OrderedDict())
        loc['referedSubNsNodeId'] = subns
        loc['referedPolicyId'] = p_id
    
    def add_vnf_location(self, sub_ns_nid, vnf_nid, loc_desc):
        try:
            if sub_ns_nid not in self.model['SubNsFlavors']:
                raise Exception('unknown sub ns node id: %s' % sub_ns_nid)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['LocationAwareness']['vnfLocations'].setdefault(sub_ns_nid, OrderedDict())
        loc = loc.setdefault(vnf_nid, OrderedDict())
        loc['locationDescription'] = loc_desc
    
    def add_location_refer_point(self, ep_id, loc_desc):
        try:
            if ep_id not in self.model['EndPoints']:
                raise Exception('unknown endpoint id: %s' % ep_id)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['LocationAwareness']['referencePoints'].setdefault(ep_id, OrderedDict())
        loc['locationDescription'] = loc_desc

    def load_model(self, model_dict):
        self.model = model_dict
    
    def get_model(self):
        return self.model