#!/usr/bin/python


#   This script is for generating materials for testing,
#   the materials give the model of a ns with two vnf node,
#   where one vnf node consists of a db server vnfc node, 
#   and the other has a nginx server as a load-balancer and a web-server node


import yaml
import logging
import os
import json
from collections import OrderedDict

from common.util.util import get_class_func_name
from model.vnfc_type import VnfcType
from model.vnf_type import VnfType
from model.vnfc_relationship_type import VnfcRelationshipType
from model.vnf_relationship_type import VnfRelationshipType
from model.ns_type import NsType
from model.ns_flavor_design import NsFlavorDesign

from common.util.yaml_util import yaml_ordered_dump

print "finished"

MAIN_DIR = os.path.abspath(os.getcwd())

if 'design_files' not in os.listdir(MAIN_DIR):
    os.mkdir('snort_firewall_design_files')
DESIGN_FILE_PATH = os.path.join(MAIN_DIR, 'design_files', '')

if 'user_upload_files' not in os.listdir(MAIN_DIR):
    os.mkdir('user_upload_files')
USER_UPLOADS_DIR = os.path.join(MAIN_DIR, 'user_upload_files', '')

os.chdir(USER_UPLOADS_DIR)

if 'vnfc_artifacts' not in os.listdir(USER_UPLOADS_DIR):
    os.mkdir('vnfc_artifacts')
VNFC_ARTIFACT_DIR = os.path.join(USER_UPLOADS_DIR, 'vnfc_artifacts', '')

if 'vnfc_images' not in os.listdir(USER_UPLOADS_DIR):
    os.mkdir('vnfc_images')
VNFC_IMAGE_DIR = os.path.join(USER_UPLOADS_DIR, 'vnfc_images', '')

if 'monitor_file_packs' not in os.listdir(USER_UPLOADS_DIR):
    os.mkdir('monitor_file_packs')
VNF_MONITOR_PACK_DIR = os.path.join(USER_UPLOADS_DIR, 'monitor_file_packs', '')

if 'alarm_file_packs' not in os.listdir(USER_UPLOADS_DIR):
    os.mkdir('alarm_file_packs')
NS_ALARM_PACK_DIR = os.path.join(USER_UPLOADS_DIR, 'alarm_file_packs', '')

if 'plans' not in os.listdir(USER_UPLOADS_DIR):
    os.mkdir('plans')
PLAN_DIR = os.path.join(USER_UPLOADS_DIR, 'plans', '')

os.chdir(MAIN_DIR)

############ VNFC TYPE DEFINITION ###########

#   vnfc type id
VNFC1_T = 'IDS-VNFC'
#VNFC2_T = 'FIREWALL-VNFC'
#VNFC3_T = 'CONTROLLER-VNFC'


#   vnfc affiliation
VNFC1_AFF = '[' + 'IDS-VNF' + ']'
#VNFC2_AFF = '[' + 'FIREWALL-VNF' + ']'
#VNFC3_AFF = '[' + 'IDS-FIREWALL-VNF' + ']'
#   vnfc artifact file pack
#VNFC1_ARTIFACT = VNFC1_T + '-pack.tar.gz'
#VNFC2_ARTIFACT = VNFC2_T + '-pack.tar.gz'
#VNFC3_ARTIFACT = VNFC3_T + '-pack.tar.gz'
VNFC1_ARTIFACT = ''
VNFC2_ARTIFACT = ''
VNFC3_ARTIFACT = ''
VNFC4_ARTIFACT = ''
#   vnfc artifact image file
VNFC1_IMAGE = 'ids'#VNFC1_T + '_image.qcow'
#VNFC2_IMAGE = 'firewall'#VNFC2_T + '_image.qcow'
#VNFC3_IMAGE = 'ids'#VNFC3_T + '_image.qcow'
#VNFC4_IMAGE = VNFC3_T + '_image.qcow'
#VNFC_ARTIFACT_ROOTDIR = os.path.join('', 'usr', 'local')

#   vnfc property
#VNFC1_PROP_1 = 'webserver-port'
#VNFC1_PROP_2 = 'remote-db-addr'
#VNFC1_PROP_3 = 'remote-db-username'
#VNFC1_PROP_4 = 'remote-db-password'
VNFC1_PROP_4 = 'ids-public-addr'
VNFC1_PROP_5 = 'ids-private-addr'

#VNFC2_PROP_1 = 'firewall-public-addr'
#VNFC2_PROP_2 = 'firewall-private-addr'


#VNFC3_PROP_1 = 'hss-public-addr'
#VNFC3_PROP_2 = 'mme-remote-addr'
#VNFC3_PROP_3 = 'hss-private-addr'
 
#   vnfc endpoint
VNFC1_EP_1 = 'IDS-PORTAL'
#VNFC2_EP_1 = 'FIREWALL-PORTAL'
#VNFC3_EP_1 = 'HSS-PORTAL'
#VNFC4_EP_1 = 'mgmtAgent'
#   vnfc interface
VNFC_IF_ORDER = 1

VNFC1_IF_ABS_PATH = '/bin/'
#VNFC2_IF_ABS_PATH = '/bin/'
#VNFC3_IF_ABS_PATH = '/bin/'


VNFC1_IF_START = 'ids-start'
VNFC1_IF_CONFIGURE = 'ids-configure'
VNFC1_IF_STOP = 'ids-stop'
VNFC1_IF_START_FORMAT = './ids-start'
VNFC1_IF_CONFIGURE_FORMAT = './ids-configure'
VNFC1_IF_STOP_FORMAT = './ids-stop'

############ VNFC RELATIONSHIP TYPE DEFINITION ###########

############ VNF TYPE DEFINITION ###########

#   vnf type id
VNF1_T = 'IDS-VNF'

#   vnfc node
VNF1_VNFC_N_1 = 'IDS-NODE'
VNF1_VNFC_N_1_T = VNFC1_T

#   vnf endpoint
VNF1_EP_1 = 'IDS-ENDPOINT'
VNF1_EP_1_VNFC_N = VNF1_VNFC_N_1
VNF1_EP_1_VNFC_EP = VNFC1_EP_1

#MAPPINGS = {VNF1_MAPPING_1: {'source': {S_VNFC_N_1: S_VNFC_N_PROP_1}, 'target':{T_VNFC_N_1: T_VNFC_N_PROP_1}}}

#   service exposure
#   monitor options
#   scaling info
############ VNF RELATIONSHIP TYPE DEFINITION #############

#   vnf relationship type
#VNF_RELATIONS = {VNF_RELATION_T: {'source': {S_VNF_T: S_EP}, 'target': {T_VNF_T: T_EP}}}

############ NS TYPE DEFINITION #############

#   ns type id
NS_T = 'IDS-NS'

#   vnf node
NS_VNF_N_1 = 'IDS-NODE'
NS_VNF_N_1_T = VNF1_T


#   ns endpoint
NS_EP_1 = 'IDS-ENDPOINT'
NS_EP_1_VNF_N = NS_VNF_N_1
NS_EP_1_VNF_EP = VNF1_EP_1

#   vnf connection
#   vnf property mapping
#   ns metric
#   ns SLA
#   ns alarm
#   ns Plan
NS_INSTAN_PLAN_FILE = 'ids-instantiate.bpmn'

#   ns vnf sharing policy
#   ns service exposure policy
#   ns scaling policy
############ NS FLAVOR DESIGN DEFINITION #############

#   ns flavor id
NS_F = 'IDS-FLAVOR'

#   ns sla flavor

#   vnfc deploy flavor
NS_F_VNFC1_FLAVOR_VALUE = '[ m1.huge ]'
NS_F_VNFC1_IMAGE_VALUE = 'ids'

#logging.basicConfig(filename='nsMaterialGenerator.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
#log = logging.getLogger('nsMaterialGenerator')

if hasattr(yaml, 'CSafeLoader'):
    yaml_loader = yaml.CSafeLoader
else: 
    yaml_loader = yaml.SafeLoader 

class NsMaterialGenerator(object):

    def __init__(self):
        self.vnfc_types = {}
        self.vnfc_relationship_types = {}
        self.vnf_types = {}
        self.vnf_relationship_types = {}
        self.ns_type = {}
        self.ns_flavor_design = {}

######### generate vnfc type ##########

    def add_vnfc1_type(self):
        vnfc_t = VnfcType()
        vnfc_t.set_vnfc_info(VNFC1_T, VNFC1_AFF, VNFC1_T)
        vnfc_t.set_artifact(None, None, 'qcow', VNFC1_IMAGE, VNFC_IMAGE_DIR + VNFC1_IMAGE, 
                            'gzip', None)
        vnfc_t.add_flavor_constraint(NS_F_VNFC1_IMAGE_VALUE, NS_F_VNFC1_FLAVOR_VALUE)
        vnfc_t.add_endpoint(VNFC1_EP_1, VNFC1_EP_1)
        
        
        self.vnfc_types[VNFC1_T] = vnfc_t
        

    def add_vnfc_types(self):
        self.add_vnfc1_type()
######### generate vnfc relationship type ##########
    
    
######### generate vnf type ##########

    def add_vnf1_type(self):
        vnf_t = VnfType()
        vnf_t.set_vnf_info(VNF1_T, VNF1_T)
        vnf_t.add_vnfc_node(VNF1_VNFC_N_1, VNF1_VNFC_N_1_T)
        #vnf_t.add_vnfc_node(VNF1_VNFC_N_2, VNF1_VNFC_N_2_T)
        vnf_t.add_endpoint(VNF1_EP_1, VNF1_EP_1_VNFC_N, VNF1_EP_1_VNFC_EP, 
                           VNF1_EP_1_VNFC_N + ':' + VNF1_EP_1_VNFC_EP)
       # vnf_t.add_endpoint(VNF1_EP_2, VNF1_EP_2_VNFC_N, VNF1_EP_2_VNFC_EP, 
        #                   VNF1_EP_2_VNFC_N + ':' + VNF1_EP_2_VNFC_EP)

        self.vnf_types[VNF1_T] = vnf_t
    
    def add_vnf_types(self):
        self.add_vnf1_type()

######### generate vnf relationship type ##########
    
   
######### generate ns type ##########

    def add_ns_type(self):
        ns_t = NsType()
        ns_t.set_ns_info(NS_T, NS_T)
        ns_t.add_vnf_node(NS_VNF_N_1, NS_VNF_N_1_T)
        ns_t.add_endpoint(NS_EP_1, NS_EP_1_VNF_N, NS_EP_1_VNF_EP, 
                          NS_EP_1_VNF_N + ':' + NS_EP_1_VNF_EP)
        
        self.ns_type[NS_T] = ns_t

########## generate ns flavor design ############

    def add_ns_flavor_design(self):
        ns_f = NsFlavorDesign()
        ns_f.add_vnfc_deploy_flavor(NS_VNF_N_1, VNF1_VNFC_N_1, 'openstack','m1.huge','ids')
#        ns_f.add_vnfc_deploy_flavor(NS_VNF_N_1, VNF1_VNFC_N_2)

        ns_f.set_ns_flavor_info(NS_F, NS_T, NS_T + ':' + NS_F)
         #                                  VNF2_MONITOR_OPT_1_CONFIG_1, NS_F_VNF_MON_CONF_VALUE_1)
        self.ns_flavor_design[NS_F] = ns_f



########## generate yaml and json file ###################

    def generate_vnfc_type_yaml_json(self):
        for t_id, v in self.vnfc_types.items():
            f_path = os.path.join(DESIGN_FILE_PATH, t_id + '_vnfc_type.yaml')
            f = file(f_path, 'w')
            yaml_ordered_dump(v.model, stream=f, Dumper=yaml.SafeDumper, default_flow_style=False)
            #yaml_to_json(f_path)

    
    def generate_vnfc_relationship_type_yaml_json(self):
        for t_id, v in self.vnfc_relationship_types.items():
            f_path = os.path.join(DESIGN_FILE_PATH, t_id + '_vnfc_rel_type.yaml')
            f = file(f_path, 'w')
            yaml_ordered_dump(v.model, stream=f, Dumper=yaml.SafeDumper, default_flow_style=False)
            #yaml_to_json(f_path)
    
    
    def generate_vnf_type_yaml_json(self):
        for t_id, v in self.vnf_types.items():
            f_path = os.path.join(DESIGN_FILE_PATH, t_id + '_vnf_type.yaml')
            f = file(f_path, 'w')
            yaml_ordered_dump(v.model, stream=f, Dumper=yaml.SafeDumper, default_flow_style=False)
            #yaml_to_json(f_path)
    
    def generate_vnf_relationship_type_yaml_json(self):
        for t_id, v in self.vnf_relationship_types.items():
            f_path = os.path.join(DESIGN_FILE_PATH, t_id + '_vnf_rel_type.yaml')
            f = file(f_path, 'w')
            yaml_ordered_dump(v.model, stream=f, Dumper=yaml.SafeDumper, default_flow_style=False)
            #yaml_to_json(f_path)

    
    def generate_ns_type_yaml_json(self):
        for t_id, v in self.ns_type.items():
            f_path = os.path.join(DESIGN_FILE_PATH, t_id + '_ns_type.yaml')
            f = file(f_path, 'w')
            yaml_ordered_dump(v.model, stream=f, Dumper=yaml.SafeDumper, default_flow_style=False)
            #yaml_to_json(f_path)
  
    def generate_ns_flavor_design_yaml_json(self):
        for t_id, v in self.ns_flavor_design.items():
            f_path = os.path.join(DESIGN_FILE_PATH, t_id + '_ns_flavor.yaml')
            f = file(f_path, 'w')
            yaml_ordered_dump(v.model, stream=f, Dumper=yaml.SafeDumper, default_flow_style=False)
            #yaml_to_json(f_path)

    def generate_yaml_json(self):
        self.generate_vnfc_type_yaml_json()
        self.generate_vnfc_relationship_type_yaml_json()
        self.generate_vnf_type_yaml_json()
        self.generate_vnf_relationship_type_yaml_json()
        self.generate_ns_type_yaml_json()
        self.generate_ns_flavor_design_yaml_json()


if __name__ == '__main__':
    if os.path.exists(DESIGN_FILE_PATH):
        os.system('rm -r ' + DESIGN_FILE_PATH)
    os.mkdir(DESIGN_FILE_PATH)
    gen = NsMaterialGenerator()
    gen.add_vnfc_types()
    gen.add_vnf_types()
    gen.add_ns_type()
    gen.add_ns_flavor_design()
    gen.generate_yaml_json() 
