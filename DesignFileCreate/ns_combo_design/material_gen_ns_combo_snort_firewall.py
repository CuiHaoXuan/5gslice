#!/usr/bin/python


#   This script is for generating ns comboe materials for testing,
#   the materials give the model of a ns combo with two lb-web sub ns nodes,
#   no connection between the two sub ns nodes


import yaml
import logging
import os
import json
from collections import OrderedDict

from common.util.util import get_class_func_name
from model.ns_combo_flavor_design import NsComboFlavorDesign
from model.ns_combo_flavor_subscribe import NsComboFlavorSubscribe

from common.util.yaml_util import yaml_ordered_dump

MAIN_DIR = os.path.abspath(os.getcwd())

if 'ns_combo_design_files' not in os.listdir(MAIN_DIR):
    os.mkdir('protection-platform_design_files')
DESIGN_FILE_PATH = os.path.join(MAIN_DIR, 'ns_combo_design_files', '')

NS_T = 'IDS-NS'
NS_F = 'IDS-FLAVOR'
NS_EP = 'IDS-ENDPOINT'
NS_SP = ''

NS_VNF_N_1 = 'IDS-NODE'
#NS_VNF_N_2 = 'CLEANER-NODE'

############ NS COMBO FLAVOR DESIGN ###########

#   basic info
NS_COMBO_FLAVOR = 'IDS-SERVICE'
NS_COMBO_FLAVOR_DESC = NS_COMBO_FLAVOR

#   sub ns flavors
SUB_NS_1 = 'IDS-SUBNS-1'
SUB_NS_1_T = NS_T
SUB_NS_1_F = NS_F



#   endpoints
ENDPOINT_1 = 'IDS-SUBNS-1-ENDPOINT'
ENDPOINT_1_SUB_NS = SUB_NS_1
ENDPOINT_1_SUB_NS_EP = NS_EP
ENDPOINT_1_DESC = ENDPOINT_1


#   connections

#   ns combo SLA
NS_COMBO_SLA_1 = 'ns-combo-sla-1'
NS_COMBO_SLA_1_VALUE_T = 'num'
NS_COMBO_SLA_1_DESC = NS_COMBO_SLA_1
NS_COMBO_SLA_1_VALUE = 100




#   vnf locator
NS_COMBO_VNF_LOCATOR_1 = SUB_NS_1

NS_COMBO_VNF_LOCATOR_1_VNF_1 = NS_VNF_N_1
NS_COMBO_VNF_LOCATOR_1_VNF_1_DESC = NS_COMBO_VNF_LOCATOR_1_VNF_1 + '@' + NS_COMBO_VNF_LOCATOR_1
'''
NS_COMBO_VNF_LOCATOR_1_VNF_2 = NS_VNF_N_2
NS_COMBO_VNF_LOCATOR_1_VNF_2_DESC = NS_COMBO_VNF_LOCATOR_1_VNF_2 + '@' + NS_COMBO_VNF_LOCATOR_1
'''
#NS_COMBO_VNF_LOCATOR_2 = SUB_NS_2

#NS_COMBO_VNF_LOCATOR_2_VNF_1 = NS_VNF_N_1
#NS_COMBO_VNF_LOCATOR_2_VNF_1_DESC = NS_COMBO_VNF_LOCATOR_2_VNF_1 + '@' + NS_COMBO_VNF_LOCATOR_2

#NS_COMBO_VNF_LOCATOR_2_VNF_2 = NS_VNF_N_2
#NS_COMBO_VNF_LOCATOR_2_VNF_2_DESC = NS_COMBO_VNF_LOCATOR_2_VNF_2 + '@' + NS_COMBO_VNF_LOCATOR_2

#   endpoint locator
NS_COMBO_LOCATOR_1 = ENDPOINT_1
NS_COMBO_LOCATOR_1_DESC = NS_COMBO_LOCATOR_1

#NS_COMBO_LOCATOR_2 = ENDPOINT_2
#NS_COMBO_LOCATOR_2_DESC = NS_COMBO_LOCATOR_2

############ NS COMBO FLAVOR SUBSCRIBE #############

#   subscriber info
TENANT = 'tenant-1'

#   vnf location name
NS_COMBO_VNF_LOCATOR_1_VNF_1_LOC = 'core DC'
NS_COMBO_VNF_LOCATOR_1_VNF_2_LOC = 'regional DC'
NS_COMBO_VNF_LOCATOR_2_VNF_1_LOC = 'core DC'
NS_COMBO_VNF_LOCATOR_2_VNF_2_LOC = 'regional DC'

#   latency source
LATENCY_SRC = '10.10.26.10/24'


#logging.basicConfig(filename='materialGenerator.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
#log = logging.getLogger('materialGenerator')

if hasattr(yaml, 'CSafeLoader'):
    yaml_loader = yaml.CSafeLoader
else:
    yaml_loader = yaml.SafeLoader 

class NsComboMaterialGenerator(object):

    def __init__(self):
        self.ns_combo_flavor_design = {}

########## generate ns combo flavor design ############

    def add_ns_combo_flavor_design(self):
        ns_combo_f = NsComboFlavorDesign()
        ns_combo_f.set_ns_combo_flavor_info(NS_COMBO_FLAVOR, NS_COMBO_FLAVOR_DESC)
        ns_combo_f.add_subns_flavor(SUB_NS_1, SUB_NS_1_T, SUB_NS_1_F)
        #ns_combo_f.add_subns_flavor(SUB_NS_2, SUB_NS_2_T, SUB_NS_2_F)
        ns_combo_f.add_endpoint(ENDPOINT_1, ENDPOINT_1_SUB_NS, ENDPOINT_1_SUB_NS_EP, ENDPOINT_1_DESC)
        #ns_combo_f.add_endpoint(ENDPOINT_2, ENDPOINT_2_SUB_NS, ENDPOINT_2_SUB_NS_EP, ENDPOINT_2_DESC)
        ns_combo_f.add_sla_flavor(NS_COMBO_SLA_1, NS_COMBO_SLA_1_VALUE, NS_COMBO_SLA_1_DESC)
        #ns_combo_f.add_scaling_policy(NS_COMBO_SP_1, NS_COMBO_SP_1_SUB_NS, NS_COMBO_SP_1_SUB_NS_SP)
        #ns_combo_f.add_scaling_policy(NS_COMBO_SP_2, NS_COMBO_SP_2_SUB_NS, NS_COMBO_SP_2_SUB_NS_SP)
        ns_combo_f.add_vnf_location(NS_COMBO_VNF_LOCATOR_1, NS_COMBO_VNF_LOCATOR_1_VNF_1, NS_COMBO_VNF_LOCATOR_1_VNF_1_DESC)
        #ns_combo_f.add_vnf_location(NS_COMBO_VNF_LOCATOR_1, NS_COMBO_VNF_LOCATOR_1_VNF_2, NS_COMBO_VNF_LOCATOR_1_VNF_2_DESC)
        #ns_combo_f.add_vnf_location(NS_COMBO_VNF_LOCATOR_2, NS_COMBO_VNF_LOCATOR_2_VNF_1, NS_COMBO_VNF_LOCATOR_2_VNF_1_DESC)
        #ns_combo_f.add_vnf_location(NS_COMBO_VNF_LOCATOR_2, NS_COMBO_VNF_LOCATOR_2_VNF_2, NS_COMBO_VNF_LOCATOR_2_VNF_2_DESC)
        #   ns_combo_f.add_location_refer_point(NS_COMBO_LOCATOR_1, NS_COMBO_LOCATOR_1_DESC)
        #   ns_combo_f.add_location_refer_point(NS_COMBO_LOCATOR_2, NS_COMBO_LOCATOR_2_DESC)
        self.ns_combo_flavor_design[NS_COMBO_FLAVOR] = ns_combo_f

########## generate ns combo flavor subscribe ############

    def add_ns_combo_flavor_subscribe(self):
        ns_combo_f_sub = NsComboFlavorSubscribe(NS_COMBO_FLAVOR, 'subscribed by ' + TENANT, TENANT)
 #       ns_combo_f_sub.add_scaling_policy(NS_COMBO_SP_1)
  #      ns_combo_f_sub.add_scaling_policy(NS_COMBO_SP_2)
        ns_combo_f_sub.add_vnf_locator_name(NS_COMBO_VNF_LOCATOR_1, NS_COMBO_VNF_LOCATOR_1_VNF_1, NS_COMBO_VNF_LOCATOR_1_VNF_1_DESC, NS_COMBO_VNF_LOCATOR_1_VNF_1_LOC)
        #ns_combo_f_sub.add_vnf_locator_name(NS_COMBO_VNF_LOCATOR_1, NS_COMBO_VNF_LOCATOR_1_VNF_2, NS_COMBO_VNF_LOCATOR_1_VNF_2_DESC, NS_COMBO_VNF_LOCATOR_1_VNF_2_LOC)
        #ns_combo_f_sub.add_vnf_locator_name(NS_COMBO_VNF_LOCATOR_2, NS_COMBO_VNF_LOCATOR_2_VNF_1, NS_COMBO_VNF_LOCATOR_2_VNF_1_DESC, NS_COMBO_VNF_LOCATOR_2_VNF_1_LOC)
    #    ns_combo_f_sub.add_vnf_locator_name(NS_COMBO_VNF_LOCATOR_2, NS_COMBO_VNF_LOCATOR_2_VNF_2, NS_COMBO_VNF_LOCATOR_2_VNF_2_DESC, NS_COMBO_VNF_LOCATOR_2_VNF_2_LOC)
        #   ns_combo_f_sub.add_latency_locator_src_addr(NS_COMBO_LOCATOR_1, LATENCY_SRC, NS_COMBO_LOCATOR_1_DESC)
        #   ns_combo_f_sub.add_latency_locator_src_addr(NS_COMBO_LOCATOR_2, LATENCY_SRC, NS_COMBO_LOCATOR_2_DESC)
        self.ns_combo_flavor_subscribe = ns_combo_f_sub



########## generate yaml and json file ###################

  
    def generate_ns_combo_flavor_design_yaml_json(self):
        for f_id, v in self.ns_combo_flavor_design.items():
            f_path = os.path.join(DESIGN_FILE_PATH, f_id + '_ns_combo_flavor_design.yaml')
            f = file(f_path, 'w')
            yaml_ordered_dump(v.model, stream=f, Dumper=yaml.SafeDumper, default_flow_style=False)
            #yaml_to_json(f_path)

    def generate_ns_combo_flavor_subscribe_yaml_json(self):
        for f_id in self.ns_combo_flavor_design.keys():
            f_path = os.path.join(DESIGN_FILE_PATH, f_id + '_ns_combo_flavor_subscribe.yaml')
            f = file(f_path, 'w')
            yaml_ordered_dump(self.ns_combo_flavor_subscribe.model, stream=f, Dumper=yaml.SafeDumper, 
                              default_flow_style=False)
            #yaml_to_json(f_path)

    def generate_yaml_json(self):
        self.generate_ns_combo_flavor_design_yaml_json()
        self.generate_ns_combo_flavor_subscribe_yaml_json()


if __name__ == '__main__':
    if os.path.exists(DESIGN_FILE_PATH):
        os.system('rm -r ' + DESIGN_FILE_PATH)
    os.mkdir(DESIGN_FILE_PATH)
    gen = NsComboMaterialGenerator()
    gen.add_ns_combo_flavor_design()
    gen.add_ns_combo_flavor_subscribe()
    gen.generate_yaml_json() 
