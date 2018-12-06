#   model class for VNF type definition

import re
import os
from collections import OrderedDict

from common.util.util import get_class_func_name

MONITOR_LOCATE_SET = ('host', 'agent_host')
MONITOR_CONFIG_VALUE_TYPE_SET = ('string', 'num', 'list_string', 'list_num')
PACK_TYPE_SET = ('gzip', 'zip')
INTERFACE_SCOPE_SET = ('install', 'start', 'configure')

class VnfType(object):
    
    def __init__(self):
        self.model = OrderedDict()
        self.model['Info'] = OrderedDict()
        self.model['VnfcNodes'] = OrderedDict()
        self.model['EndPoints'] = OrderedDict()
        self.model['Connections'] = OrderedDict()
        self.model['VnfcPropertiesMapping'] = OrderedDict()
        self.model['ServiceExposures'] = OrderedDict()
        self.model['MonitorOptions'] = []
        self.model['ScalingInfo'] = OrderedDict()
        self.model['ScalingInfo']['scalingGroups'] = OrderedDict()
        self.model['ScalingInfo']['scalingOperations'] = OrderedDict()

    def set_vnf_info(self, type_id, 
                 desc, ver='1.0.0', vendor='iaa'):
        self.model['Info']['vnfTypeId'] = type_id
        self.model['Info']['version'] = ver
        self.model['Info']['vendor'] = vendor
        self.model['Info']['description'] = desc
    
    def add_vnfc_node(self, node_id, vnfc_t):
        self.model['VnfcNodes'][node_id] = OrderedDict()
        self.model['VnfcNodes'][node_id]['vnfcTypeId'] = vnfc_t        

    def add_endpoint(self, ep_id, vnfc_node, vnfc_ep, desc):
        self.model['EndPoints'][ep_id] = OrderedDict()
        self.model['EndPoints'][ep_id]['vnfcNodeId'] = vnfc_node
        self.model['EndPoints'][ep_id]['vnfcEndPointId'] = vnfc_ep
        self.model['EndPoints'][ep_id]['description'] = desc
    
    def add_connection(self, con_id, rel_type, vnfc_node_1, vnfc_ep_1, vnfc_node_2, vnfc_ep_2):
        self.model['Connections'][con_id] = OrderedDict()
        self.model['Connections'][con_id]['vnfcRelationshipTypeId'] = rel_type
        self.model['Connections'][con_id]['endOne'] = OrderedDict()
        self.model['Connections'][con_id]['endOne']['vnfcNodeId'] = vnfc_node_1
        self.model['Connections'][con_id]['endOne']['vnfcEndPointId'] = vnfc_ep_1
        self.model['Connections'][con_id]['endTwo'] = OrderedDict()
        self.model['Connections'][con_id]['endTwo']['vnfcNodeId'] = vnfc_node_2
        self.model['Connections'][con_id]['endTwo']['vnfcEndPointId'] = vnfc_ep_2

    def add_vnfc_property_mapping(self, map_id, vnfc_node_s, vnfc_prop_s, vnfc_node_t, vnfc_prop_t, mul_inst_opt=False):
        try:
            if vnfc_node_s not in self.model['VnfcNodes']:
                raise Exception('unknown vnfc node: %s' % vnfc_node_s)
            if vnfc_node_t not in self.model['VnfcNodes']:
                raise Exception('unknown vnfc node: %s' % vnfc_node_t)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['VnfcPropertiesMapping'][map_id] = OrderedDict()
        self.model['VnfcPropertiesMapping'][map_id]['multiInstanceOption'] = mul_inst_opt
        self.model['VnfcPropertiesMapping'][map_id]['sourceProperty'] = OrderedDict()
        self.model['VnfcPropertiesMapping'][map_id]['sourceProperty']['vnfcNodeId'] = vnfc_node_s
        self.model['VnfcPropertiesMapping'][map_id]['sourceProperty']['propertyId'] = vnfc_prop_s
        self.model['VnfcPropertiesMapping'][map_id]['targetProperty'] = OrderedDict()
        self.model['VnfcPropertiesMapping'][map_id]['targetProperty']['vnfcNodeId'] = vnfc_node_t
        self.model['VnfcPropertiesMapping'][map_id]['targetProperty']['propertyId'] = vnfc_prop_t

    def add_exposed_service(self, serv_id, s_name, ep, desc):
        try:
            if ep not in self.model['EndPoints']:
                raise Exception('unknown endpoint: %s' % ep)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['ServiceExposures'][serv_id] = OrderedDict()
        self.model['ServiceExposures'][serv_id]['name'] = s_name
        self.model['ServiceExposures'][serv_id]['exposureEndPointId'] = ep
        self.model['ServiceExposures'][serv_id]['description'] = desc

    def add_monitor_option(self, monitor_target, parameters):
        monitortarget = OrderedDict()
        monitortarget[monitor_target] = parameters
        self.model['MonitorOptions'].append(monitortarget)


    '''
    def add_monitor_option(self, mon_id, f_pack_name, f_pack, desc, target_vnfc, 
                           pack_type='gzip', locate='host', root_dir='/usr/local/monitors/'):
        try:
            if pack_type not in PACK_TYPE_SET:
                raise Exception('unknown pack type: %s' % pack_type)
            if locate not in MONITOR_LOCATE_SET:
                raise Exception('unknown locate type: %s' % locate)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['MonitorOptions'][mon_id] = OrderedDict()       
        self.model['MonitorOptions'][mon_id]['filePackInfo'] = OrderedDict()
        self.model['MonitorOptions'][mon_id]['monitorConfigs'] = OrderedDict()
        self.model['MonitorOptions'][mon_id]['interfaces'] = OrderedDict()
        self.model['MonitorOptions'][mon_id]['filePackInfo']['filePack'] = f_pack_name
        self.model['MonitorOptions'][mon_id]['filePackInfo']['getFile'] = f_pack
        self.model['MonitorOptions'][mon_id]['filePackInfo']['packType'] = pack_type
        self.model['MonitorOptions'][mon_id]['filePackInfo']['locate'] = locate
        self.model['MonitorOptions'][mon_id]['filePackInfo']['rootDir'] = root_dir
        self.model['MonitorOptions'][mon_id]['filePackInfo']['description'] = desc
        if not os.path.exists(os.path.abspath(f_pack)):
            os.mknod(os.path.abspath(f_pack))
        try:
            if target_vnfc.startswith('[') and target_vnfc.endswith(']'):
                self.model['MonitorOptions'][mon_id]['filePackInfo']['target'] = []
                for n in re.split(', |  ', target_vnfc.strip('[]')):
                    if n.strip() not in self.model['VnfcNodes']:
                        raise Exception('unknown vnfc node: %s' % target_vnfc)
                    self.model['MonitorOptions'][mon_id]['filePackInfo']['target'].append(n.strip())
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
    '''

    def add_monitor_config(self, mon_id, conf_id, desc, v_type='string', d_value=None):
        try:
            if mon_id not in self.model['MonitorOptions']:
                raise Exception('unknown monitor option: %s' % mon_id)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['MonitorOptions'][mon_id]['monitorConfigs'][conf_id] = OrderedDict()
        try:
            if v_type not in MONITOR_CONFIG_VALUE_TYPE_SET:
                raise Exception('unknown property value type: %s' % v_type)
        except Exception, e:
            print Exception, ":", e
        self.model['MonitorOptions'][mon_id]['monitorConfigs'][conf_id]['valueType'] = v_type
        self.model['MonitorOptions'][mon_id]['monitorConfigs'][conf_id]['defaultValue'] = d_value
        self.model['MonitorOptions'][mon_id]['monitorConfigs'][conf_id]['description'] = desc    
    
    def add_monitor_interface(self, mon_id, if_id, scope, order, fm, f_path):
        self.model['MonitorOptions'][mon_id]['interfaces'][if_id] = OrderedDict()
        try:
            if scope not in INTERFACE_SCOPE_SET:
                raise Exception('unknown interface scope: %s' % scope)
        except Exception, e:
            print Exception, ":", e
        self.model['MonitorOptions'][mon_id]['interfaces'][if_id]['scope'] = scope
        self.model['MonitorOptions'][mon_id]['interfaces'][if_id]['order'] = order
        self.model['MonitorOptions'][mon_id]['interfaces'][if_id]['format'] = fm
        self.model['MonitorOptions'][mon_id]['interfaces'][if_id]['relPath'] = f_path
    
    def add_scale_group(self, g_id, t_vnfc, min_v, max_v, d_v):
        loc = self.model['ScalingInfo']['scalingGroups'].setdefault(g_id, OrderedDict())
        loc['target'] = t_vnfc
        loc['min'] = min_v
        loc['max'] = max_v
        loc['defaultGroup'] = d_v
    
    def add_scale_oper(self, op_id, s_step, t_group, desc):
        loc = self.model['ScalingInfo']['scalingOperations'].setdefault(op_id, OrderedDict())
        loc['scalingStep'] = s_step
        loc['targetGroup'] = t_group
        loc['description'] = desc
    
    def load_model(self, model_dict):
        self.model = model_dict
    
    def get_model(self):
        return self.model
