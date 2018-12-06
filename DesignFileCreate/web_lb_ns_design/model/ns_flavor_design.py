#   model class for NS flavor design definition

import re
import logging
from collections import OrderedDict

from common.util.util import get_class_func_name

LOCATOR_SET = ('latency')

# logging.basicConfig(filename='nsFlavorDesign.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
# log = logging.getLogger('nsFlavorDesign')

class NsFlavorDesign(object):
    
    def __init__(self):
        self.model = OrderedDict()
        self.model['Info'] = OrderedDict()
        self.model['ServiceLevelAgreementFlavors'] = OrderedDict()
        self.model['VnfcDeploymentFlavors'] = OrderedDict()
        self.model['VnfcConfigurationFlavors'] = OrderedDict()
        self.model['VnfMonitorFlavors'] = OrderedDict()
        self.model['VnfMonitorFlavors']['monitorConfigurationFlavors'] = OrderedDict()

    def set_ns_flavor_info(self, flavor_id, type_id, 
                 desc, ver='1.0.0', vendor='iaa'):
        self.model['Info']['nsFlavorId'] = flavor_id
        self.model['Info']['nsTypeId'] = type_id
        self.model['Info']['version'] = ver
        self.model['Info']['vendor'] = vendor
        self.model['Info']['description'] = desc
    
    def add_vnfc_deploy_flavor(self, vnf_node, vnfc_node, vim_t='openstack', vm_f='m1.tiny', os_t='ubuntu14.04'):
        if vnf_node not in self.model['VnfcDeploymentFlavors']:
            self.model['VnfcDeploymentFlavors'][vnf_node] = OrderedDict()
        self.model['VnfcDeploymentFlavors'][vnf_node][vnfc_node] = OrderedDict()
        self.model['VnfcDeploymentFlavors'][vnf_node][vnfc_node]['vimType'] = vim_t
        self.model['VnfcDeploymentFlavors'][vnf_node][vnfc_node]['vmFlavor'] = vm_f
        self.model['VnfcDeploymentFlavors'][vnf_node][vnfc_node]['osType'] = os_t
    
    def add_sla_flavor(self, sla_id, val):
        self.model['ServiceLevelAgreementFlavors'][sla_id] = OrderedDict()
        self.model['ServiceLevelAgreementFlavors'][sla_id]['value'] = val
    
    def add_vnfc_config_flavor(self, vnf_node, vnfc_node, para, val):
        if vnf_node not in self.model['VnfcConfigurationFlavors']:
            self.model['VnfcConfigurationFlavors'][vnf_node] = OrderedDict()
        if vnfc_node not in self.model['VnfcConfigurationFlavors'][vnf_node]:
            self.model['VnfcConfigurationFlavors'][vnf_node][vnfc_node] = OrderedDict()
        self.model['VnfcConfigurationFlavors'][vnf_node][vnfc_node][para] = OrderedDict()
        self.model['VnfcConfigurationFlavors'][vnf_node][vnfc_node][para]['value'] = val

    def add_vnf_monitor_config_flavor(self, vnf_node, mon_opt, para, val):
        if vnf_node not in self.model['VnfMonitorFlavors']['monitorConfigurationFlavors']:
            self.model['VnfMonitorFlavors']['monitorConfigurationFlavors'][vnf_node] = OrderedDict()
        if mon_opt not in self.model['VnfMonitorFlavors']['monitorConfigurationFlavors'][vnf_node]:
            self.model['VnfMonitorFlavors']['monitorConfigurationFlavors'][vnf_node][mon_opt] = OrderedDict()
        self.model['VnfMonitorFlavors']['monitorConfigurationFlavors'][vnf_node][mon_opt][para] = OrderedDict()
        self.model['VnfMonitorFlavors']['monitorConfigurationFlavors'][vnf_node][mon_opt][para]['value'] = val
    
    def load_model(self, model_dict):
        self.model = model_dict
    
    def get_model(self):
        return self.model