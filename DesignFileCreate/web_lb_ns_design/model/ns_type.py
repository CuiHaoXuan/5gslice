#   model class for NS type definition

import re
import os
from collections import OrderedDict

from common.util.util import get_class_func_name

SLA_VALUE_TYPE_SET = ('string', 'num', 'list_string', 'list_num')
METRIC_DIMENSION_VALUE_TYPE = ('string', 'num')
PACK_TYPE_SET = ('gzip', 'zip')
INTERFACE_SCOPE_SET = ('install', 'start', 'configure')
COMPARE_SET = ('lt', 'le', 'eq', 'ge', 'gt')

class NsType(object):
    
    def __init__(self):
        self.model = OrderedDict()
        self.model['Info'] = OrderedDict()
        self.model['VnfNodes'] = OrderedDict()
        self.model['EndPoints'] = OrderedDict()
        self.model['Connections'] = OrderedDict()
        self.model['VnfPropertiesMapping'] = OrderedDict()
        self.model['Metrics'] = OrderedDict()
        self.model['ServiceLevelAgreement'] = OrderedDict()
        self.model['Alarms'] = OrderedDict()
        self.model['Plans'] = OrderedDict()
        self.model['Plans']['instantiatePlan'] = OrderedDict()
        self.model['Plans']['scalingPlans'] = OrderedDict()
        self.model['Policies'] = OrderedDict()
        self.model['Policies']['vnfSharingPolicies'] = OrderedDict()
        self.model['Policies']['serviceExposurePolicies'] = OrderedDict()
        self.model['Policies']['propertyExposurePolicies'] = OrderedDict()
        self.model['Policies']['scalingPolicies'] = OrderedDict()

    def set_ns_info(self, type_id, 
                 desc, ver='1.0.0', vendor='iaa'):
        self.model['Info']['nsTypeId'] = type_id
        self.model['Info']['version'] = ver
        self.model['Info']['vendor'] = vendor
        self.model['Info']['description'] = desc
    
    def add_vnf_node(self, node_id, vnf_t):
        self.model['VnfNodes'][node_id] = OrderedDict()
        self.model['VnfNodes'][node_id]['vnfTypeId'] = vnf_t        

    def add_endpoint(self, ep_id, vnf_node, vnf_ep, desc):
        self.model['EndPoints'][ep_id] = OrderedDict()
        self.model['EndPoints'][ep_id]['vnfNodeId'] = vnf_node
        self.model['EndPoints'][ep_id]['vnfEndPointId'] = vnf_ep
        self.model['EndPoints'][ep_id]['description'] = desc
    
    def add_connection(self, con_id, rel_type, vnf_node_1, vnf_ep_1, vnf_node_2, vnf_ep_2):
        self.model['Connections'][con_id] = OrderedDict()
        self.model['Connections'][con_id]['vnfRelationshipTypeId'] = rel_type
        self.model['Connections'][con_id]['endOne'] = OrderedDict()
        self.model['Connections'][con_id]['endOne']['vnfNodeId'] = vnf_node_1
        self.model['Connections'][con_id]['endOne']['vnfEndPointId'] = vnf_ep_1
        self.model['Connections'][con_id]['endTwo'] = OrderedDict()
        self.model['Connections'][con_id]['endTwo']['vnfNodeId'] = vnf_node_2
        self.model['Connections'][con_id]['endTwo']['vnfEndPointId'] = vnf_ep_2

    def add_vnf_property_mapping(self, map_id, vnf_node_s, vnfc_node_s, vnfc_prop_s, 
                                                vnf_node_t, vnfc_node_t, vnfc_prop_t, mul_inst_opt=False):
        try:
            if vnf_node_s not in self.model['VnfNodes']:
                raise Exception('unknown vnf node: %s' % vnf_node_s)
            if vnf_node_t not in self.model['VnfNodes']:
                raise Exception('unknown vnf node: %s' % vnf_node_t)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['VnfPropertiesMapping'][map_id] = OrderedDict()
        self.model['VnfPropertiesMapping'][map_id]['multiInstanceOption'] = mul_inst_opt
        self.model['VnfPropertiesMapping'][map_id]['sourceProperty'] = OrderedDict()
        self.model['VnfPropertiesMapping'][map_id]['sourceProperty']['vnfNodeId'] = vnf_node_s
        self.model['VnfPropertiesMapping'][map_id]['sourceProperty']['propertyId'] = vnfc_prop_s
        self.model['VnfPropertiesMapping'][map_id]['sourceProperty']['vnfcNodeId'] = vnfc_node_s
        self.model['VnfPropertiesMapping'][map_id]['sourceProperty']['propertyId'] = vnfc_prop_s
        self.model['VnfPropertiesMapping'][map_id]['targetProperty'] = OrderedDict()
        self.model['VnfPropertiesMapping'][map_id]['targetProperty']['vnfNodeId'] = vnf_node_t
        self.model['VnfPropertiesMapping'][map_id]['targetProperty']['vnfcNodeId'] = vnfc_node_t
        self.model['VnfPropertiesMapping'][map_id]['targetProperty']['propertyId'] = vnfc_prop_t
    
    def add_metric(self, m_id, m_name, desc, interval=10):
        self.model['Metrics'][m_id] = OrderedDict()       
        self.model['Metrics'][m_id]['name'] = m_name
        self.model['Metrics'][m_id]['dimensions'] = OrderedDict()
        self.model['Metrics'][m_id]['interval'] = interval
        self.model['Metrics'][m_id]['description'] = desc
    
    def add_metric_dimension(self, m_id, dim_id, dim_name, inter, desc, v_type='string'):
        try:
            if m_id not in self.model['Metrics']:
                raise Exception('unknown metric type: %s' % m_id)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['Metrics'][m_id]['dimensions'][dim_id] = OrderedDict()
        try:
            if v_type not in METRIC_DIMENSION_VALUE_TYPE:
                raise Exception('unknown dimension value type: %s' % v_type)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['Metrics'][m_id]['dimensions'][dim_id]['valueType'] = v_type
        self.model['Metrics'][m_id]['dimensions'][dim_id]['name'] = dim_name
        self.model['Metrics'][m_id]['dimensions'][dim_id]['interval'] = inter
        self.model['Metrics'][m_id]['dimensions'][dim_id]['description'] = desc
    
    def add_sla(self, sla_id, desc, v_type='num', d_value=None):
        try:
            if v_type not in SLA_VALUE_TYPE_SET:
                raise Exception('unknown sla value type: %s' % v_type)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['ServiceLevelAgreement'][sla_id] = OrderedDict()
        self.model['ServiceLevelAgreement'][sla_id]['valueType'] = v_type
        self.model['ServiceLevelAgreement'][sla_id]['defaultValue'] = d_value
        self.model['ServiceLevelAgreement'][sla_id]['description'] = desc
    
    def add_alarm(self, a_id, f_pack, f_path, s_format, r_path, \
                        env, comp, thr, desc='a alarm', pack_t='gzip'):
        try:
            if comp not in COMPARE_SET:
                raise Exception('unknown comp type: %s' % comp)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['Alarms'].setdefault(a_id, OrderedDict())
        loc['statFilePack'] = f_pack
        loc['getFile'] = os.path.abspath(f_path)
        loc['packType'] = pack_t
        loc['statFormat'] = s_format
        loc['relPath'] = r_path
        loc['outputEnv'] = env
        loc['description'] = desc
        loc['comparison'] = comp
        loc['threshold'] = thr
        if not os.path.exists(os.path.abspath(f_path)):
            os.mknod(os.path.abspath(f_path))
    
    def add_instantiate_plan(self, plan_f_name, plan_f, desc):
        self.model['Plans']['instantiatePlan']['planFile'] = plan_f_name
        self.model['Plans']['instantiatePlan']['getFile'] = plan_f
        self.model['Plans']['instantiatePlan']['description'] = desc
        if not os.path.exists(os.path.abspath(plan_f)):
            os.mknod(os.path.abspath(plan_f))
    
    def add_scaling_plan(self, plan_id, plan_f_name, plan_f, desc):
	print plan_id
        loc = self.model['Plans']['scalingPlans'].setdefault(plan_id, OrderedDict())
        loc['planFile'] = plan_f_name
        loc['getFile'] = plan_f
        loc['description'] = desc
        if not os.path.exists(os.path.abspath(plan_f)):
            os.mknod(os.path.abspath(plan_f))
    
    def add_vnf_sharing_policy(self, vsp_id, s_type, vnf_nid):
        loc = self.model['Policies']['vnfSharingPolicies'].setdefault(vsp_id, OrderedDict())       
        loc['sharingType'] = s_type
        loc['relatedVnfNode'] = vnf_nid
    
    def add_service_exposure_policy(self, sep_id, sep_name, desc):
        loc = self.model['Policies']['serviceExposurePolicies'].setdefault(sep_id, OrderedDict())       
        loc['name'] = sep_name
        loc['description'] = desc
        loc['serviceMembers'] = OrderedDict()
    
    def add_exposed_service_member(self, sep_id, mem_id, vnf_node, serv):
        try:
            if sep_id not in self.model['Policies']['serviceExposurePolicies']:
                raise Exception('unknown service exposure policy: %s' % sep_id)
            if vnf_node not in self.model['VnfNodes']:
                raise Exception('unknown vnf node: %s' % vnf_node)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['Policies']['serviceExposurePolicies'][sep_id]['serviceMembers'].setdefault(mem_id, OrderedDict())
        loc['vnfNodeId'] = vnf_node
        loc['serviceId'] = serv
    
    def add_property_exposure_policy(self, pep_id, vnf_nid, vnfc_nid, prop_id):
        loc = self.model['Policies']['propertyExposurePolicies'].setdefault(pep_id, OrderedDict())       
        loc['vnfNodeId'] = vnf_nid
        loc['vnfNodeId'] = vnfc_nid
        loc['propertyId'] = prop_id
    
    def add_scaling_policy(self, sp_id, alarm_id, hook_t, cd, s_plan, desc):
        loc = self.model['Policies']['scalingPolicies'].setdefault(sp_id, OrderedDict())       
        loc['alarmId'] = alarm_id
        loc['hookType'] = hook_t
        loc['actions'] = OrderedDict()
        loc['cooldown'] = cd
        loc['scalingPlan'] = s_plan
        loc['description'] = desc
    
    def add_scaling_action_in_vnf(self, sp_id, act_id, vnf_nid, op_id):
        try:
            if sp_id not in self.model['Policies']['scalingPolicies']:
                raise Exception('unknown scaling policy: %s' % sp_id)
            if vnf_nid not in self.model['VnfNodes']:
                raise Exception('unknown vnf node: %s' % vnf_nid)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        loc = self.model['Policies']['scalingPolicies'][sp_id]['actions'].setdefault(act_id, OrderedDict())
        loc['involvedEntityType'] = 'vnf'
        loc['involvedEntityId'] = vnf_nid
        loc['scalingOpId'] = op_id
    
    def load_model(self, model_dict):
        self.model = model_dict
    
    def get_model(self):
        return self.model
