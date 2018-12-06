#   model class for ns combo meta

import re
import logging
import os
import sys
from collections import OrderedDict

from common.util.yaml_util import yaml_ordered_load

#logging.basicConfig(filename='nsComboMeta.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
#log = logging.getLogger('nsComboMeta')

class NsComboMeta(object):
    
    def __init__(self, combo_fid, ver, vendor,
                       f_desc, tenant_id, trade_id, sub_desc):
        self.meta = OrderedDict()

        self.meta['flavorInfo'] = OrderedDict()
        f_info = self.meta['flavorInfo']
        f_info['flavorId'] = combo_fid
        f_info['version'] = ver
        f_info['vendor'] = vendor
        f_info['description'] = f_desc

        self.meta['subscriberInfo'] = OrderedDict()
        self.meta['subscriberInfo']['tenantId'] = tenant_id
        self.meta['subscriberInfo']['tradeId'] = trade_id
        self.meta['subscriberInfo']['description'] = sub_desc

        self.meta['slaInfo'] = OrderedDict()

        self.meta['locationInfo'] = OrderedDict()
        self.meta['locationInfo']['vnfLocations'] = OrderedDict()
        self.meta['locationInfo']['referencePoints'] = OrderedDict()


        self.meta['topologyInfo'] = OrderedDict()
        self.meta['topologyInfo']['subNsInfo'] = OrderedDict()
        self.meta['topologyInfo']['connectionInfo'] = OrderedDict()
        self.meta['topologyInfo']['endPointInfo'] = OrderedDict()

        self.meta['subNsCsarInfo'] = OrderedDict()

        self.meta['policies'] = OrderedDict()

        pol_meta = self.meta['policies']
        pol_meta['vnfSharingPolicies'] = OrderedDict()
        pol_meta['serviceExposurePolicies'] = OrderedDict()
        pol_meta['propertyExposurePolicies'] = OrderedDict()
        pol_meta['scalingPolicies'] = OrderedDict()

############ generate the location info in the meta #############
    
    def add_vnf_location_info(self, sub_ns_nid, vnf_nid, locate_n, desc='a vnf of the NS combo'):

        '''
        add a location awareness info of a vnf node

        '''
        loc = self.meta['locationInfo']['vnfLocations']
        loc = loc.setdefault(sub_ns_nid, OrderedDict())
        loc = loc.setdefault(vnf_nid, OrderedDict())
        loc['locationDescription'] = desc
        loc['locatorName'] = locate_n
    
    def add_ref_point_location_info(self, ref_ep, src_addr,
                                          l_max=500, 
                                          ref_ep_desc='an external point of the NS combo'):
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

############ generate the sla info in the meta ##########

    def add_sla_info(self, sla_id, val):

        '''
        add a sla info to the meta

        '''
        loc = self.meta['slaInfo'].setdefault(sla_id, OrderedDict())
        loc['value'] = val

############ generate the topology info in the meta #############
    
    def add_topo_sub_ns_info(self, sub_ns_nid, ns_tid):

        '''
        add a sub ns node info to the topology sub ns info

        '''
        info_b = self.meta['topologyInfo']['subNsInfo']
        try:
            if sub_ns_nid not in info_b.keys():
                info_b = self.meta['topologyInfo']['subNsInfo']
                info_b[sub_ns_nid] = OrderedDict()
                info_b = info_b[sub_ns_nid]
                info_b['nsTypeId'] = ns_tid
            else:
                pass
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_topo_sub_ns_connection_info(self, conn_id, 
                                           sub_ns_nid_1, sub_ns_epid_1, vnf_nid_1, vnf_epid_1, 
                                           sub_ns_nid_2, sub_ns_epid_2, vnf_nid_2, vnf_epid_2):
        '''
        add a sub ns connection to the topology info

        '''
        try:
            info_b = self.meta['topologyInfo']['connectionInfo']
            info_b[conn_id] = OrderedDict()
            info_b[conn_id]['endOne'] = OrderedDict()
            info_b[conn_id]['endTwo'] = OrderedDict()
            info_b_one, info_b_two = info_b[conn_id]['endOne'], info_b[conn_id]['endTwo']
            info_b_one['subNsNodeId'], info_b_one['subNsEndPointId'] = sub_ns_nid_1, sub_ns_epid_1
            info_b_one['relatedVnfNodeId'], info_b_one['relatedVnfEndPointId'] = vnf_nid_1, vnf_epid_1
            info_b_two['subNsNodeId'], info_b_two['subNsEndPointId'] = sub_ns_nid_2, sub_ns_epid_2
            info_b_two['relatedVnfNodeId'], info_b_two['relatedVnfEndPointId'] = vnf_nid_2, vnf_epid_2
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def add_topo_ns_combo_endpoint_info(self, ep_id, sub_ns_nid, sub_ns_epid, 
                                                     vnf_nid, vnf_epid):

        '''
        add a ns combo endpoint info to the topology info

        '''
        try:
            info_b = self.meta['topologyInfo']['endPointInfo']
            info_b[ep_id] = OrderedDict()
            info_b[ep_id]['subNsNodeId'] = sub_ns_nid
            info_b[ep_id]['subNsEndPointId'] = sub_ns_epid
            info_b[ep_id]['relatedVnfNodeId'] = vnf_nid
            info_b[ep_id]['relatedVnfEndPointId'] = vnf_epid
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

############ generate the sub ns csar info ################

    def add_sub_ns_csar_info(self, sub_ns_nid, pack_name):

        '''
        add the sub ns csar info

        '''
        try:
            info_b = self.meta['subNsCsarInfo']
            info_b = info_b.setdefault(sub_ns_nid, OrderedDict())
            info_b['csarPackName'] = pack_name
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name
    
########## generate the vnf sharing policies info ######

    def add_vnf_sharing_policy(self, vsp_id, sub_ns_nid, p_id):

        '''
        add a vnf sharing policy info

        '''
        try:
            info_b = self.meta['policies']['vnfSharingPolicies']
            info_b = info_b.setdefault(vsp_id, OrderedDict())
            info_b['referedSubNsNodeId'] = sub_ns_nid
            info_b['referedPolicyId'] = p_id
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

########## generate the service exposure policies info ######

    def add_serv_exposure_policy(self, sep_id, sub_ns_nid, p_id):

        '''
        add a service exposure policy info

        '''
        try:
            info_b = self.meta['policies']['serviceExposurePolicies']
            info_b = info_b.setdefault(sep_id, OrderedDict())
            info_b['referedSubNsNodeId'] = sub_ns_nid
            info_b['referedPolicyId'] = p_id
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

########## generate the property exposure policies info ######

    def add_prop_exposure_policy(self, pep_id, sub_ns_nid, p_id, conn_sub_ns, conn_ep_id):

        '''
        add a property exposure policy info

        '''
        try:
            info_b = self.meta['policies']['propertyExposurePolicies']
            info_b = info_b.setdefault(pep_id, OrderedDict())
            info_b['referedSubNsNodeId'] = sub_ns_nid
            info_b['referedPolicyId'] = p_id
            info_b['connectedSubNsNodeId'] = conn_sub_ns
            info_b['connectedSubNsEndPointId'] = conn_ep_id
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

########## generate the scaling policies info ######

    def add_scaling_policy(self, sep_id, sub_ns_nid, p_id):

        '''
        add a scaling policy info

        '''
        try:
            info_b = self.meta['policies']['scalingPolicies']
            info_b = info_b.setdefault(sep_id, OrderedDict())
            info_b['referedSubNsNodeId'] = sub_ns_nid
            info_b['referedPolicyId'] = p_id
        except Exception, e:
            print Exception, ':', e, sys._getframe().f_code.co_name

    def get_meta(self):
        return self.meta
