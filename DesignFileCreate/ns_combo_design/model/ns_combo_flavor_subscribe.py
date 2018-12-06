#   model class for NS combo flavor subscribe definition

import time
from collections import OrderedDict

from common.util.util import get_class_func_name

VNF_LOC_NAME_SET = ['access DC', 'regional DC', 'core DC']

class NsComboFlavorSubscribe(object):
    
    def __init__(self, ns_combo_f, desc, tenant='tenant_1', \
                       trade=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))):
        self.model = OrderedDict()
        loc = self.model.setdefault('Info', OrderedDict())
        loc['nsComboFlavorId'] = ns_combo_f
        loc['tenantId'] = tenant
        loc['tradeId'] = trade
        loc['description'] = desc

        loc = self.model.setdefault('SubscribedPolicies', OrderedDict())
        loc['vnfSharingPlicies'] = []
        loc['serviceExposurePolicies'] = []
        loc['propertyExposurePolicies'] = []
        loc['scalingPolicies'] = []

        loc = self.model.setdefault('LocationAwareness', OrderedDict())
        loc['referencePoints'] = OrderedDict()
        loc['vnfLocations'] = OrderedDict()

    def add_vnf_sharing_policy(self, vsp_id):
        self.model['SubscribedPolicies']['vnfSharingPolicies'].append(vsp_id)
    
    def add_serv_exposure_policy(self, sep_id):
        self.model['SubscribedPolicies']['serviceExposurePolicies'].append(sep_id)

    def add_prop_exposure_policy(self, pep_id):
        self.model['SubscribedPolicies']['propertyExposurePolicies'].append(sep_id)
    
    def add_scaling_policy(self, sp_id):
        self.model['SubscribedPolicies']['scalingPolicies'].append(sp_id)
    
    def add_vnf_locator_name(self, sub_ns_nid, vnf_nid, desc, loc_n):
        try:
            if loc_n not in VNF_LOC_NAME_SET:
                raise Exception('unknown vnf locator name: %s' % loc_n)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['LocationAwareness']['vnfLocations'].setdefault(sub_ns_nid, OrderedDict())
        loc = loc.setdefault(vnf_nid, OrderedDict())
        loc['locationDescription'] = desc
        loc['locatorName'] = loc_n

    def add_latency_locator_src_addr(self, ep, src_addr, desc, l_max=500):
        loc = self.model['LocationAwareness']['referencePoints'].setdefault(ep, OrderedDict())
        loc['locationDescription'] = desc
        loc = loc.setdefault('latency', OrderedDict())
        loc['source'] = OrderedDict()
        loc['source']['ipAddress'] = src_addr
        loc['latencyMax'] = l_max
    
    def load_model(self, model_dict):
        self.model = model_dict    
    
    def get_model(self):
        return self.model