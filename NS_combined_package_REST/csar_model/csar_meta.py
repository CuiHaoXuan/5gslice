#   model class for CSAR meta

import re
import logging
import os
import sys
from collections import OrderedDict

#logging.basicConfig(filename='csarMeta.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
#log = logging.getLogger('csarMeta')

class CsarMeta(object):
    
    def __init__(self, ns_fid, ns_tid, ver, vendor, desc):
        self.meta = OrderedDict()

        self.meta['nsFlavorInfo'] = OrderedDict()
        nsf_info = self.meta['nsFlavorInfo']
        nsf_info['nsFlavorId'] = ns_fid
        nsf_info['nsTypeId'] = ns_tid
        nsf_info['version'] = ver
        nsf_info['vendor'] = vendor
        nsf_info['description'] = desc

        #   self.meta['tenantInfo'] = OrderedDict()
        #   self.meta['tenantInfo']['tenantId'] = tenant_id
        #   self.meta['tenantInfo']['tradeId'] = trade_id

########## not in v1 ################
        self.meta['slaInfo'] = OrderedDict()
#######################################

        self.meta['locationInfo'] = OrderedDict()
        self.meta['locationInfo']['referencePoints'] = OrderedDict()


        self.meta['topologyInfo'] = OrderedDict()
        self.meta['topologyInfo']['vnfInfo'] = OrderedDict()
        self.meta['topologyInfo']['connectionInfo'] = OrderedDict()
        self.meta['topologyInfo']['endPointInfo'] = OrderedDict()

        self.meta['nsdInfo'] = OrderedDict()
        self.meta['vnfdInfo'] = OrderedDict()

        self.meta['resourceInfo'] = OrderedDict()

############# not in v1 ###########
        #   self.meta['vnfcdInfo'] = OrderedDict()
#####################################

        self.meta['deploymentArtifactInfo'] = OrderedDict()

        self.meta['parameterInfo'] = OrderedDict()

        self.meta['vnfcConfigInfo'] = OrderedDict()

        self.meta['metricInfo'] = OrderedDict()

        #   self.meta['monitorCfgInfo'] = OrderedDict()
#####################################

        self.meta['monitorOptions'] = []

        self.meta['alarmInfo'] = OrderedDict()

        self.meta['planInfo'] = OrderedDict()
        self.meta['planInfo']['instantiatePlan']= OrderedDict()
        self.meta['planInfo']['scalingPlans'] = OrderedDict()

        self.meta['policies'] = OrderedDict()
        pol = self.meta['policies']
        pol['vnfSharingPolicies'] = OrderedDict()
        pol['serviceExposurePolicies'] = OrderedDict()
        pol['propertyExposurePolicies'] = OrderedDict()
        pol['scalingPolicies'] = OrderedDict()

############ generate the location info in the meta #############
    
    def add_ref_point_location_info(self, ref_ep, src_addr,
                                          l_max=500, 
                                          ref_ep_desc='an internal point of the NS'):
        '''
        add a locaiton awareness info of a reference endpoint

        '''
        loc = self.meta['locationInfo']['referencePoints']
        loc[ref_ep] = OrderedDict()
        loc = loc[ref_ep]
        loc['locationDescription'] = ref_ep_desc
        loc['latency'] = OrderedDict()
        loc['latency']['source'] = OrderedDict()
        loc['latency']['source']['ipAddress'] = src_addr
        loc['latency']['latencyMax'] = l_max

############ generate the topology info in the meta #############
    
    def add_topo_vnf_info(self, vnf_nid, vnf_tid):

        '''
        add a vnf node info to the topology vnf info

        '''
        info_b = self.meta['topologyInfo']['vnfInfo']
        try:
            if vnf_nid not in info_b.keys():
                info_b = self.meta['topologyInfo']['vnfInfo']
                info_b[vnf_nid] = OrderedDict()
                info_b = info_b[vnf_nid]
                info_b['vnfTypeId'] = vnf_tid
                info_b['vnfcInfo'] = OrderedDict()
                info_b['connectionInfo'] = OrderedDict()
                info_b['endPointInfo'] = OrderedDict()
            else:
                pass
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_topo_vnfc_info(self, vnf_nid, vnf_tid, vnfc_nid, vnfc_tid):

        '''
        add a vnfc node info to the topology vnf info

        '''
        try:
            self.add_topo_vnf_info(vnf_nid, vnf_tid)
            info_b = self.meta['topologyInfo']['vnfInfo']\
                              [vnf_nid]['vnfcInfo']
            info_b[vnfc_nid] = OrderedDict()
            info_b[vnfc_nid]['vnfcTypeId'] = vnfc_tid
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
    
    def add_topo_vnfc_connection_info(self, vnf_nid, vnf_tid, conn_id, 
                                            vnfc_nid_1, vnfc_epid_1, 
                                            vnfc_nid_2, vnfc_epid_2):
        '''
        add a vnfc connection to the topology vnf info

        '''
        try:
            self.add_topo_vnf_info(vnf_nid, vnf_tid)
            info_b = self.meta['topologyInfo']['vnfInfo']\
                              [vnf_nid]['connectionInfo']
            info_b[conn_id] = OrderedDict()
            info_b[conn_id]['endOne'] = OrderedDict()
            info_b[conn_id]['endTwo'] = OrderedDict()
            info_b_one, info_b_two = info_b[conn_id]['endOne'], info_b[conn_id]['endTwo']
            info_b_one['vnfcNodeId'], info_b_one['vnfcEndPointId'] = vnfc_nid_1, vnfc_epid_1
            info_b_two['vnfcNodeId'], info_b_two['vnfcEndPointId'] = vnfc_nid_2, vnfc_epid_2
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_topo_vnf_endpoint_info(self, vnf_nid, vnf_tid, ep_id, 
                                             vnfc_nid, vnfc_epid):

        '''
        add a vnf endpoint info to the topology vnf info

        '''
        try:
            self.add_topo_vnf_info(vnf_nid, vnf_tid)
            info_b = self.meta['topologyInfo']['vnfInfo']\
                              [vnf_nid]['endPointInfo']
            info_b[ep_id] = OrderedDict()
            info_b[ep_id]['vnfcNodeId'] = vnfc_nid
            info_b[ep_id]['vnfcEndPointId'] = vnfc_epid
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_topo_vnf_connection_info(self, conn_id, 
                                           vnf_nid_1, vnf_epid_1, 
                                           vnf_nid_2, vnf_epid_2):
        '''
        add a vnf connection to the topology info

        '''
        try:
            info_b = self.meta['topologyInfo']['connectionInfo']
            info_b[conn_id] = OrderedDict()
            info_b[conn_id]['endOne'] = OrderedDict()
            info_b[conn_id]['endTwo'] = OrderedDict()
            info_b_one, info_b_two = info_b[conn_id]['endOne'], info_b[conn_id]['endTwo']
            info_b_one['vnfNodeId'], info_b_one['vnfEndPointId'] = vnf_nid_1, vnf_epid_1
            info_b_two['vnfNodeId'], info_b_two['vnfEndPointId'] = vnf_nid_2, vnf_epid_2
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_topo_ns_endpoint_info(self, ep_id, vnf_nid, vnf_epid):

        '''
        add a ns endpoint info to the topology info

        '''
        try:
            info_b = self.meta['topologyInfo']['endPointInfo']
            info_b[ep_id] = OrderedDict()
            info_b[ep_id]['vnfNodeId'] = vnf_nid
            info_b[ep_id]['vnfEndPointId'] = vnf_epid
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

############ generate the nsd file info ###############
    
    def add_nsd_info(self, file_name, file_path):

        '''
        add the nsd info

        '''
        try:
            self.meta['nsdInfo']['nsdFile'] = file_name
            self.meta['nsdInfo']['csarFilePath'] = file_path
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

############ generate the vnfd files info ################

    def add_vnfd_info(self, vnf_nid, file_name, file_path):

        '''
        add the vnfd info

        '''
        try:
            info_b = self.meta['vnfdInfo']
            info_b = info_b.setdefault(vnf_nid, OrderedDict())
            info_b['vnfdFile'] = file_name
            info_b['csarFilePath'] = file_path
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

############ generate the datacenter resource info #############

    def add_res_info(self, res_info):
        self.meta['resourceInfo'].update(res_info)

############ generate the vnfc deployment artifacts info #############

    def add_arti_vnfc_image(self, vnf_nid, vnfc_nid, image_f, file_path):

        '''
        add a vnfc node artifact image file info to the artifact info

        '''
        try:
            info_b = self.meta['deploymentArtifactInfo']
            info_b = info_b.setdefault(vnf_nid, OrderedDict())
            info_b = info_b.setdefault(vnfc_nid, OrderedDict())
            info_b = info_b.setdefault('imageInfo', OrderedDict())
            info_b['imageFile'] = image_f
            info_b['csarFilePath'] = file_path
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
    
    def add_arti_vnfc_pack(self, vnf_nid, vnfc_nid, file_pack,
                                 pack_type, file_path, root_dir):

        '''
        add a vnfc node artifact file pack info to the artifact info

        '''
        try:
            info_b = self.meta['deploymentArtifactInfo']
            info_b = info_b.setdefault(vnf_nid, OrderedDict())
            info_b = info_b.setdefault(vnfc_nid, OrderedDict())
            info_b = info_b.setdefault('filePackInfo', OrderedDict())
            info_b['filePack'] = file_pack
            info_b['packType'] = pack_type
            info_b['csarFilePath'] = file_path
            info_b['deployRootDir'] = root_dir
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

############# generate the configurable parameter info #############

    def add_independent_para_info(self, vnf_nid, vnfc_nid, 
                                        para_id, para_v):
        '''
        add a independent configurable parameter info

        '''
        try:
            info_b = self.meta['parameterInfo']
            info_b = info_b.setdefault(vnf_nid, OrderedDict())
            info_b = info_b.setdefault(vnfc_nid, OrderedDict())
            info_b = info_b.setdefault('independentParas', OrderedDict())
            info_b = info_b.setdefault(para_id, OrderedDict())
            info_b['value'] = para_v
            info_b['isBuildInFunc'] = False
            if para_v.startswith('{{ get_') or para_v.startswith('{{get_'):
                info_b['isBuildInFunc'] = True
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_dependent_para_info(self, vnf_nid, vnfc_nid, para_id,  
                                      de_vnf_nid, de_vnfc_nid, de_para_id, mul_inst_opt):
        '''
        add a dependent configurable parameter info

        '''
        try:
            info_b = self.meta['parameterInfo']
            info_b = info_b.setdefault(vnf_nid, OrderedDict())
            info_b = info_b.setdefault(vnfc_nid, OrderedDict())
            info_b = info_b.setdefault('dependentParas', OrderedDict())
            info_b = info_b.setdefault(para_id, OrderedDict())
            info_b = info_b.setdefault('dependency', OrderedDict())
            info_b['vnfNodeId'] = de_vnf_nid
            info_b['vnfcNodeId'] = de_vnfc_nid
            info_b['propertyId'] = de_para_id
            info_b['multiInstanceOption'] = mul_inst_opt
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

################## generate the vnfc configuration info ###########

    def add_conifg_interface(self, vnf_nid, vnfc_nid, if_id, 
                                   scope, order, form, file_p, 
                                   paras):
        '''
        add an interface to the vnfc configuration

        '''
        try:
            info_b = self.meta['vnfcConfigInfo']
            info_b = info_b.setdefault(vnf_nid, OrderedDict())
            info_b = info_b.setdefault(vnfc_nid, OrderedDict())
            info_b = info_b.setdefault(if_id, OrderedDict())
            info_b['scope'] = scope
            info_b['order'] = order
            info_b['format'] = form
            info_b['deployFileAbsPath'] = file_p
            info_b['involveParas'] = paras
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

################## generate the metric info ###########

    def add_metric(self, m_id, m_name, interval, desc): 

        '''
        add a metric to the metric info

        '''
        try:
            info_b = self.meta['metricInfo']
            info_b = info_b.setdefault(m_id, OrderedDict())
            info_b['name'] = m_name
            info_b['dimensions'] = OrderedDict()
            info_b['interval'] = interval
            info_b['description'] = desc
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_dim_to_metric(self, m_id, dim_id, v_type, dim_n): 

        '''
        add a dimention to the a specific dimension

        '''
        try:
            info_b = self.meta['metricInfo'].get(m_id, None)
            info_b = info_b['dimensions'].setdefault(dim_id, OrderedDict())
            info_b['valueType'] = v_type
            info_b['dimName'] = dim_n
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name


################## generate the alarm info ###########

    def add_alarm(self, a_id, f_path, s_format, r_path, env, 
                        comp, thr, desc, p_type='gzip'): 

        '''
        add a alarm to the alarm info

        '''
        try:
            info_b = self.meta['alarmInfo']
            info_b = info_b.setdefault(a_id, OrderedDict())
            info_b['csarFilePath'] = f_path
            info_b['packType'] = p_type
            info_b['statFormat'] = s_format
            info_b['relPath'] = r_path
            info_b['outputEnv'] = env
            info_b['comparison'] = comp
            info_b['threshold'] = thr
            info_b['description'] = desc
            info_b['involveMetrics'] = [n.strip('}}') for n in s_format.split('{{') if '}}' in n]
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_monitor_options(self, monitor_target):
        try:
           info_b = self.meta['monitorOptions']
           for monitor_target_item in monitor_target:
               info_b.append(monitor_target_item)
        except Exception, e:
            print "error in add_monitor_options"

########### generate the monitor info ###############

    def add_monitor_artifact(self, vnf_nid, mon_id, t_vnfc_nids, locate,  
                                   file_pack, pack_t, root_dir, file_path):
        '''
        add a monitor artifact info

        '''
        try:
            info_b = self.meta['monitorInfo']
            info_b = info_b.setdefault(vnf_nid, OrderedDict())
            info_b = info_b.setdefault(mon_id, OrderedDict())
            info_b['targetVnfcNodeIds'] = t_vnfc_nids
            info_b['locate'] = locate
            info_b = info_b.setdefault('filePackInfo', OrderedDict())
            info_b['filePack'] = file_pack
            info_b['packType'] = pack_t
            info_b['deployRootDir'] = root_dir
            info_b['csarFilePath'] = file_path
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
    
    def add_monitor_independent_parameter(self, vnf_nid, mon_id, 
                                                    mon_conf_id, para_v):
        '''
        add an independent parameter info for monitor

        '''
        try:
            info_b = self.meta['monitorInfo']
            info_b = info_b.setdefault(vnf_nid, OrderedDict())
            info_b = info_b.setdefault(mon_id, OrderedDict())
            info_b = info_b.setdefault('independentParas', OrderedDict())
            info_b = info_b.setdefault(mon_conf_id, OrderedDict())
            info_b['value'] = para_v
            info_b['isBuildInFunc'] = False
            if para_v.startswith('{{ get_') or para_v.startswith('{{get_'):
                info['isBuildInFunc'] = True
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
    
    def add_monitor_interface(self, vnf_nid, mon_id, if_id, 
                                      scope, order, form, file_p, paras):
        '''
        add an interface info for monitor

        '''
        try:
            info_b = self.meta['monitorInfo']
            info_b = info_b.setdefault(vnf_nid, OrderedDict())
            info_b = info_b.setdefault(mon_id, OrderedDict())
            info_b = info_b.setdefault('interfaceInfo', OrderedDict())
            info_b = info_b.setdefault(if_id, OrderedDict())
            info_b['scope'] = scope
            info_b['order'] = order
            info_b['format'] = form
            info_b['deployFileAbsPath'] = file_p
            info_b['involveParas'] = paras
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
    
############## generate plan info ################
    
    def add_instan_plan_info(self, file_name, file_path):

        '''
        add the instantiate plan info

        '''
        try:
            self.meta['planInfo']['instantiatePlan']['planFile'] = file_name
            self.meta['planInfo']['instantiatePlan']['csarFilePath'] = file_path
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_scale_plan_info(self, p_id, file_name, file_path):

        '''
        add the instantiate plan info

        '''
        try:
            loc = self.meta['planInfo']['scalingPlans'].setdefault(p_id, OrderedDict())
            loc['planFile'] = file_name
            loc['csarFilePath'] = file_path
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

########## generate the vnf sharing policies info #######

    def add_vnf_sharing_policy(self, vsp_id, s_type, vnf_nid):

        '''
        add a vnf sharing policy info

        '''
        try:
            info_b = self.meta['policies']['vnfSharingPolicies']
            info_b = info_b.setdefault(vsp_id, OrderedDict())
            info_b['sharingType'] = s_type
            info_b['relatedVnfNode'] = vnf_nid
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

########## generate the service exposure policies info #######

    def add_serv_exposure_policy(self, sep_id, sep_n, sep_desc):

        '''
        add a service exposure policy info

        '''
        try:
            info_b = self.meta['policies']['serviceExposurePolicies']
            info_b = info_b.setdefault(sep_id, OrderedDict())
            info_b['name'] = sep_n
            info_b['description'] = sep_desc
            info_b['serviceMembers'] = OrderedDict()
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_service_member(self, sep_id, mem_id, vnf_nid, 
                                 serv_id, serv_n, ep_id, 
                                 vnfc_nid, vnfc_ep_id, desc):

        '''
        add a service member to the exposure policy

        '''
        try:
            info_b = self.meta['policies']['serviceExposurePolicies']
            info_b = info_b.get(sep_id, None)
            if not info_b:
                raise Exception('unknown exposure policy id: ' + sep_id)
            info_b = info_b['serviceMembers']
            info_b = info_b.setdefault(mem_id, OrderedDict())
            info_b['vnfNodeId'] = vnf_nid
            info_b['serviceId'] = serv_id
            info_b = info_b.setdefault('serviceInfo', OrderedDict())
            info_b['name'] = serv_n
            info_b['endPointId'] = ep_id
            info_b['vnfcNodeId'] = vnfc_nid
            info_b['vnfcEndPointId'] = vnfc_ep_id
            info_b['description'] = desc
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

########## generate the property exposure policies info #######

    def add_prop_exposure_policy(self, pep_id, vnf_nid, vnfc_nid, prop_id):

        '''
        add a property exposure policy info

        '''
        try:
            info_b = self.meta['policies']['propertyExposurePolicies']
            info_b = info_b.setdefault(pep_id, OrderedDict())
            info_b['vnfNodeId'] = vnf_nid
            info_b['vnfcNodeId'] = vnfc_nid
            info_b['propertyId'] = prop_id
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

########## generate the scaling policies info #######

    def add_scaling_policy(self, sp_id, alarm_id, hook_t, 
                                        cd, plan, desc):

        '''
        add a service exposure policy info

        '''
        try:
            info_b = self.meta['policies']['scalingPolicies']
            info_b = info_b.setdefault(sp_id, OrderedDict())
            info_b['alarmId'] = alarm_id
            info_b['hookType'] = hook_t
            info_b['actions'] = OrderedDict()
            info_b['cooldown'] = cd
            info_b['scalingPlan'] = plan
            info_b['description'] = desc
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_scaling_action_in_vnf(self, sp_id, act_id, vnf_nid, op_id):

        '''
        add a scaling action defined in a vnf node to the scaling policy

        '''
        try:
            info_b = self.meta['policies']['scalingPolicies']
            info_b = info_b.get(sp_id, None)
            if not info_b:
                raise Exception('unknown scaling policy id: ' + sp_id)
            info_b = info_b['actions']
            info_b = info_b.setdefault(act_id, OrderedDict())
            info_b['involvedEntityType'] = 'vnf'
            info_b['involvedEntityId'] = vnf_nid
            info_b['scalingOpId'] = op_id
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def get_meta(self):
        return self.meta
