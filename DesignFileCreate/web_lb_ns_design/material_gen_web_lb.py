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

print "hello"

MAIN_DIR = os.path.abspath(os.getcwd())

if 'design_files' not in os.listdir(MAIN_DIR):
    os.mkdir('design_files')
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
VNFC1_T = 'SPGW-VNFC'
VNFC2_T = 'MME-VNFC'
VNFC3_T = 'HSS-VNFC'
VNFC4_T = 'MGMT-AGENT-VNFC'

#   vnfc affiliation
VNFC1_AFF = '[' + 'SPGW-VNF' + ']'
VNFC2_AFF = '[' + 'MME-HSS-VNF' + ']'
VNFC3_AFF = '[' + 'MME-HSS-VNF' + ']'
VNFC4_AFF = '[' + 'SPGW-VNF, MME-HSS-VNF' + ']'
#   vnfc artifact file pack
#VNFC1_ARTIFACT = VNFC1_T + '-pack.tar.gz'
#VNFC2_ARTIFACT = VNFC2_T + '-pack.tar.gz'
#VNFC3_ARTIFACT = VNFC3_T + '-pack.tar.gz'
VNFC1_ARTIFACT = ''
VNFC2_ARTIFACT = ''
VNFC3_ARTIFACT = ''
VNFC4_ARTIFACT = ''
#   vnfc artifact image file
VNFC1_IMAGE = 'spgw'#VNFC1_T + '_image.qcow'
VNFC2_IMAGE = 'mme'#VNFC2_T + '_image.qcow'
VNFC3_IMAGE = 'hss'#VNFC3_T + '_image.qcow'
VNFC4_IMAGE = VNFC3_T + '_image.qcow'
#VNFC_ARTIFACT_ROOTDIR = os.path.join('', 'usr', 'local')

#   vnfc property
#VNFC1_PROP_1 = 'webserver-port'
#VNFC1_PROP_2 = 'remote-db-addr'
#VNFC1_PROP_3 = 'remote-db-username'
#VNFC1_PROP_4 = 'remote-db-password'
VNFC1_PROP_4 = 'spgw-public-addr'
VNFC1_PROP_5 = 'spgw-private-addr'

VNFC2_PROP_1 = 'mme-public-addr'
VNFC2_PROP_2 = 'hss-remote-addr'
VNFC2_PROP_3 = 'mme-private-addr'
VNFC2_PROP_5 = 'spgw-remote-addr'

VNFC3_PROP_1 = 'hss-public-addr'
VNFC3_PROP_2 = 'mme-remote-addr'
VNFC3_PROP_3 = 'hss-private-addr'
 
#   vnfc endpoint
VNFC1_EP_1 = 'SPGW-PORTAL'
VNFC2_EP_1 = 'MME-PORTAL'
VNFC3_EP_1 = 'HSS-PORTAL'
VNFC4_EP_1 = 'mgmtAgent'
#   vnfc interface
VNFC_IF_ORDER = 1

VNFC1_IF_ABS_PATH = '/bin/'
VNFC2_IF_ABS_PATH = '/bin/'
VNFC3_IF_ABS_PATH = '/bin/'

VNF1_MONITOR_TARGET = 'monitorTargetSPGW'
VNF1_MONITOR_PARAMS = {
    'parameters': [{
        'monitorConfigSPGW': {
            'valueType': 'string',
            'defaultValue': 'null',
            'target': ['SPGW-NODE','SPGW-NODE'],
            'script': {
                'type': 'create_monitor_item',
                'url': 'http://monitorServer/memory/availableMemory'
            },
            'function': [
                {
                    'type': 'REST',
                    'url': 'monitorConfigSPGW'
                }
            ]
        }
    }],
    'format': '{{monitorConfigSPGW}}',
    'url': 'monitorTargetSPGW'
}
VNF2_MONITOR_TARGET = 'monitorTargetMME-HSS'
VNF2_MONITOR_PARAMS = {
    'parameters': [{
        'monitorConfigMME': {
            'valueType': 'string',
            'defaultValue': 'null',
            'target': ['MME-HSS-NODE', 'MME-NODE'],
            'script': {
                'type': 'create_monitor_item',
                'url': 'http://monitorServer/memory/availableMemory'
            },
            'function': [
                {
                    'type': 'REST',
                    'url': 'monitorConfigMME'
                }
            ]
        }
    }, {
        'monitorConfigHSS': {
            'valueType': 'string',
            'defaultValue': 'null',
            'target': ['MME-HSS-NODE', 'HSS-NODE'],
            'script': {
                'type': 'create_monitor_item',
                'url': 'http://monitorServer/memory/availableMemory'
            },
            'function': [
                {
                    'type': 'REST',
                    'url': 'monitorConfigHSS'
                }
            ]
        }
    }],
    'format': '{{monitorConfigMME}} + {{monitorConfigHSS}}',
    'url': 'monitorTargetMME-HSS'
}

VNFC1_IF_START = 'spgw-start'
VNFC1_IF_CONFIGURE = 'spgw-set-addr'
VNFC1_IF_STOP = 'spgw-stop'
VNFC1_IF_START_FORMAT = './spgw-start'
VNFC1_IF_CONFIGURE_FORMAT = './spgw-set-addr -i ' + '{{' + VNFC1_PROP_5 + '}}' + '/24'
VNFC1_IF_STOP_FORMAT = './spgw-stop'

VNFC2_IF_START = 'mme-start'
VNFC2_IF_CONFIGURE = 'mme-set-addr'
VNFC2_IF_STOP = 'mme-stop'
VNFC2_IF_START_FORMAT = './mme-start'
VNFC2_IF_CONFIGURE_FORMAT = './mme-set-addr -n ' + '{{' + VNFC2_PROP_2 + '}}' \
        + ' -m ' + '{{' + VNFC2_PROP_3 + '}}' + '/24' + \
        ' -s ' + '{{' + VNFC2_PROP_5 + '}}' + '/24' + ' -M 208 93'
VNFC2_IF_STOP_FORMAT = './mme-stop'

VNFC3_IF_START = 'hss-start'
VNFC3_IF_CONFIGURE = 'hss-set-addr'
VNFC3_IF_STOP = 'hss-stop'
VNFC3_IF_START_FORMAT = './hss-start'
VNFC3_IF_CONFIGURE_FORMAT = './hss-set-addr -n ' + '{{' + VNFC3_PROP_3 + '}}' \
        + ' -m ' + '{{' + VNFC3_PROP_2 + '}}'
VNFC3_IF_STOP_FORMAT = './hss-stop'

'''
VNFC1_IF_INSTALL = VNFC1_T + '-install'
VNFC1_IF_START = VNFC1_T + '-start'
VNFC1_IF_INSTALL_FORMAT =  './' + VNFC1_IF_INSTALL + '.sh'
VNFC1_IF_START_FORMAT =  './' + VNFC1_IF_START + '.sh' + ' --db ' + '{{' + VNFC1_PROP_2 + '}}'
                                                         #' --dbuser ' + '{{' + VNFC1_PROP_3 + '}}' + \
                                                         #' --dbpass ' + '{{' + VNFC1_PROP_4 + '}}'

VNFC2_IF_INSTALL = VNFC2_T + '-install'
VNFC2_IF_START = VNFC2_T + '-start'
VNFC2_IF_INSTALL_FORMAT =  './' + VNFC2_IF_INSTALL + '.sh'
VNFC2_IF_START_FORMAT =  './' + VNFC2_IF_START + '.sh' + ' --backend ' + '{{' + VNFC2_PROP_1 + '}}'

VNFC3_IF_INSTALL = VNFC3_T + '-install'
VNFC3_IF_START = VNFC3_T + '-start'
VNFC3_IF_INSTALL_FORMAT =  './' + VNFC3_IF_INSTALL + '.sh'
VNFC3_IF_START_FORMAT =  './' + VNFC3_IF_START + '.sh' + ' --username ' + '{{' + VNFC3_PROP_1 + '}}' + \
                                                         ' --password ' + '{{' + VNFC3_PROP_2 + '}}'
'''

############ VNFC RELATIONSHIP TYPE DEFINITION ###########

#   vnfc relationship type
VNFC_RELATION_1_T = 'VNFC-RELATION-MME-HSS'
VNFC_REL_1_S_VNFC_T_1 = VNFC2_T
VNFC_REL_1_S_VNFC_EP_1 = VNFC2_EP_1
VNFC_REL_1_T_VNFC_T_1 = VNFC3_T
VNFC_REL_1_T_VNFC_EP_1 = VNFC3_EP_1

#VNFC_RELATIONS = {VNFC_RELATION_1_T: {'source': {S_VNFC_T_1: S_VNFC_EP_1}, 'target': {T_VNFC_T_1: T_VNFC_EP_1}}}

############ VNF TYPE DEFINITION ###########

#   vnf type id
VNF1_T = 'SPGW-VNF'
VNF2_T = 'MME-HSS-VNF'

#   vnfc node
VNF1_VNFC_N_1 = 'SPGW-NODE'
VNF1_VNFC_N_1_T = VNFC1_T
VNF1_VNFC_N_2 = 'mgmtAgent'
VNF1_VNFC_N_2_T = VNFC4_T



VNF2_VNFC_N_1 = 'MME-NODE'
VNF2_VNFC_N_1_T = VNFC2_T

VNF2_VNFC_N_2 = 'HSS-NODE'
VNF2_VNFC_N_2_T = VNFC3_T

VNF2_VNFC_N_3 = 'mgmtAgent'
VNF2_VNFC_N_3_T = VNFC4_T


#   vnf endpoint
VNF1_EP_1 = 'SPGW-ENDPOINT'
VNF1_EP_1_VNFC_N = VNF1_VNFC_N_1
VNF1_EP_1_VNFC_EP = VNFC1_EP_1

VNF1_EP_2 = 'mgmtAgent'
VNF1_EP_2_VNFC_N = VNF1_VNFC_N_2
VNF1_EP_2_VNFC_EP = VNFC4_EP_1



VNF2_EP_1 = 'MME-ENDPOINT'
VNF2_EP_1_VNFC_N = VNF2_VNFC_N_1
VNF2_EP_1_VNFC_EP = VNFC2_EP_1

VNF2_EP_2 = 'HSS-ENDPOINT'
VNF2_EP_2_VNFC_N = VNF2_VNFC_N_2
VNF2_EP_2_VNFC_EP = VNFC3_EP_1

VNF2_EP_3 = 'mgmtAgent'
VNF2_EP_3_VNFC_N = VNF2_VNFC_N_3
VNF2_EP_3_VNFC_EP = VNFC4_EP_1

#   vnfc connection
VNF2_CONNECT_1 = 'VNFC-CONNECTION-MME-HSS'
VNF2_CONNECT_1_RELATION_T = VNFC_RELATION_1_T
VNF2_CONNECT_1_END_1 = VNF2_VNFC_N_1
VNF2_CONNECT_1_END_1_EP = VNFC2_EP_1
VNF2_CONNECT_1_END_2 = VNF2_VNFC_N_2
VNF2_CONNECT_1_END_2_EP = VNFC3_EP_1

#   vnfc property mapping
VNF2_MAPPING_1 = 'MME-HSS-ADDR-MAPPING'
VNF2_MAPPING_1_MUL_INST_OPT = True
VNF2_MAP_1_S_VNFC_N = VNF2_VNFC_N_2
VNF2_MAP_1_S_VNFC_N_PROP = VNFC3_PROP_2
VNF2_MAP_1_T_VNFC_N = VNF2_VNFC_N_1
VNF2_MAP_1_T_VNFC_N_PROP = VNFC2_PROP_1



VNF2_MAPPING_2 = 'HSS-MME-ADDR-MAPPING'
VNF2_MAP_2_S_VNFC_N = VNF2_VNFC_N_1
VNF2_MAP_2_S_VNFC_N_PROP = VNFC2_PROP_2
VNF2_MAP_2_T_VNFC_N = VNF2_VNFC_N_2
VNF2_MAP_2_T_VNFC_N_PROP = VNFC3_PROP_1

#MAPPINGS = {VNF1_MAPPING_1: {'source': {S_VNFC_N_1: S_VNFC_N_PROP_1}, 'target':{T_VNFC_N_1: T_VNFC_N_PROP_1}}}

#   service exposure
VNF2_SERV_1 = 'WEB-SERVICE-MME-HSS'
VNF2_SERV_1_NAME = VNF2_SERV_1
VNF2_SERV_1_EP = VNF2_EP_1

#   monitor options
#VNF_MON_FILEPACK_ROOTDIR = os.path.join('', 'usr', 'local')
VNF_MON_IF_ORDER = 1
VNF_MON_IF_ABS_PATH = '{{get_rootDir: filePack}}/interfaces/'

VNF2_MONITOR_OPT_1 = 'WEB-SERVER-LOADER-MONITOR'
VNF2_MONITOR_OPT_1_FILE_PACK = VNF2_MONITOR_OPT_1 + '_pack.tar.gz'
#VNF1_MONITOR_OPT_1_FILE_PACK = None
VNF2_MONITOR_OPT_1_TARGET = '[' + VNF2_VNFC_N_2 + ']'
VNF2_MONITOR_OPT_1_CONFIG_1 = 'collector-public-addr'
VNF2_MONITOR_OPT_1_IF_INSTALL = VNF2_MONITOR_OPT_1 + '-install'
VNF2_MONITOR_OPT_1_IF_START = VNF2_MONITOR_OPT_1 + '-start'
VNF2_MONITOR_OPT_1_IF_INSTALL_FORMAT = './' + VNF2_MONITOR_OPT_1_IF_INSTALL + '.sh' + \
                                       ' -c ' + '{{' + VNF2_MONITOR_OPT_1_CONFIG_1 + '}}'
VNF2_MONITOR_OPT_1_IF_START_FORMAT = './' + VNF2_MONITOR_OPT_1_IF_START + '.sh'

#   scaling info
VNF2_SCALE_GROUP_1 = 'WEB-SERVER-SCALE-GROUP'
VNF2_SCALE_GROUP_1_TARGET = VNF2_VNFC_N_2
VNF2_SCALE_GROUP_1_MIN = 1
VNF2_SCALE_GROUP_1_MAX = 4
VNF2_SCALE_GROUP_1_DEFAULT = 2

VNF2_SCALE_OP_1 = 'WEB-SERVER-SCALE-OUT'
VNF2_SCALE_OP_1_STEP = 1
VNF2_SCALE_OP_1_T_GROUP = VNF2_SCALE_GROUP_1
VNF2_SCALE_OP_1_DESC = 'web server scale out'

VNF2_SCALE_OP_2 = 'WEB-SERVER-SCALE-IN'
VNF2_SCALE_OP_2_STEP = -1
VNF2_SCALE_OP_2_T_GROUP = VNF2_SCALE_GROUP_1
VNF2_SCALE_OP_2_DESC = 'web server scale in'

############ VNF RELATIONSHIP TYPE DEFINITION #############

#   vnf relationship type
VNF_RELATION_1_T = 'VNF-RELATION-vEPC'
VNF_REL_1_S_VNF_T_1 = VNF2_T
VNF_REL_1_S_VNF_EP_1 = VNF2_EP_1
VNF_REL_1_T_VNF_T_1 = VNF1_T
VNF_REL_1_T_VNF_EP_1 = VNF1_EP_1

#VNF_RELATIONS = {VNF_RELATION_T: {'source': {S_VNF_T: S_EP}, 'target': {T_VNF_T: T_EP}}}

############ NS TYPE DEFINITION #############

#   ns type id
NS_T = 'vEPC-NS'

#   vnf node
NS_VNF_N_1 = 'SPGW-NODE'
NS_VNF_N_1_T = VNF1_T
NS_VNF_N_2 = 'MME-HSS-NODE'
NS_VNF_N_2_T = VNF2_T

#   ns endpoint
NS_EP_1 = 'vEPC-ENDPOINT'
NS_EP_1_VNF_N = NS_VNF_N_1
NS_EP_1_VNF_EP = VNF1_EP_1

#   vnf connection
NS_CONNECT_1 = 'VNF-CONNECTION-vEPC'
NS_CONNECT_1_RELATION_T = VNF_RELATION_1_T
NS_CONNECT_1_END_1 = NS_VNF_N_2
NS_CONNECT_1_END_1_EP = VNF2_EP_1
NS_CONNECT_1_END_2 = NS_VNF_N_1
NS_CONNECT_1_END_2_EP = VNF1_EP_1

#   vnf property mapping
NS_MAPPING_1 = 'SPGW-ADDR-MAPPING'
NS_MAPPING_1_MUL_INST_OPT = False
NS_MAP_1_S_VNF_N_1 = NS_VNF_N_2
NS_MAP_1_S_VNFC_N_1 = VNF2_VNFC_N_1
NS_MAP_1_S_VNFC_N_PROP_1 = VNFC2_PROP_5
NS_MAP_1_T_VNF_N_1 = NS_VNF_N_1
NS_MAP_1_T_VNFC_N_1 = VNF1_VNFC_N_1
NS_MAP_1_T_VNFC_N_PROP_1 = VNFC1_PROP_4

#   ns metric
NS_METRIC_1 = 'NS-METRIC-1'
NS_METRIC_1_NAME = NS_METRIC_1
NS_METRIC_1_DIM = NS_METRIC_1 + '-dim'
NS_METRIC_1_DIM_NAME = NS_METRIC_1_DIM
NS_METRIC_1_INTERVAL = 60

#   ns SLA
NS_SLA_1 = 'NS-SLA-1'

#   ns alarm
NS_ALARM_1 = 'SPGW_alarm_1'
NS_ALARM_1_FILE_PACK = NS_ALARM_1 + '_pack.tar.gz'
NS_ALARM_1_STAT_FORMAT = './' + NS_ALARM_1 + '.sh' + \
                         ' -m ' + '{{' + VNF1_MONITOR_TARGET + '}}'
NS_ALARM_1_REL_PATH = '/'
NS_ALARM_1_OUTPUT_ENV = 'ALARM_RESULT'
NS_ALARM_1_DESC = NS_ALARM_1
NS_ALARM_1_COMP = 'lt'
NS_ALARM_1_THR = 50

NS_ALARM_2 = 'SPGW_alarm_2'
NS_ALARM_2_FILE_PACK = NS_ALARM_2 + '_pack.tar.gz'
NS_ALARM_2_STAT_FORMAT = './' + NS_ALARM_2 + '.sh' + \
                         ' -m ' + '{{' + VNF1_MONITOR_TARGET + '}}'
NS_ALARM_2_REL_PATH = '/'
NS_ALARM_2_OUTPUT_ENV = 'ALARM_RESULT'
NS_ALARM_2_DESC = NS_ALARM_2
NS_ALARM_2_COMP = 'gt'
NS_ALARM_2_THR = 100

NS_ALARM_3 = 'MME_alarm_1'
NS_ALARM_3_FILE_PACK = NS_ALARM_3 + '_pack.tar.gz'
NS_ALARM_3_STAT_FORMAT = './' + NS_ALARM_3 + '.sh' + \
                         ' -m ' + '{{' + VNF2_MONITOR_TARGET + '}}'
NS_ALARM_3_REL_PATH = '/'
NS_ALARM_3_OUTPUT_ENV = 'ALARM_RESULT'
NS_ALARM_3_DESC = NS_ALARM_3
NS_ALARM_3_COMP = 'lt'
NS_ALARM_3_THR = 50

NS_ALARM_4 = 'MME_alarm_2'
NS_ALARM_4_FILE_PACK = NS_ALARM_4 + '_pack.tar.gz'
NS_ALARM_4_STAT_FORMAT = './' + NS_ALARM_4 + '.sh' + \
                         ' -m ' + '{{' + VNF1_MONITOR_TARGET + '}}'
NS_ALARM_4_REL_PATH = '/'
NS_ALARM_4_OUTPUT_ENV = 'ALARM_RESULT'
NS_ALARM_4_DESC = NS_ALARM_4
NS_ALARM_4_COMP = 'gt'
NS_ALARM_4_THR = 100

NS_ALARM_5 = 'HSS_alarm_1'
NS_ALARM_5_FILE_PACK = NS_ALARM_5 + '_pack.tar.gz'
NS_ALARM_5_STAT_FORMAT = './' + NS_ALARM_5 + '.sh' + \
                         ' -m ' + '{{' + VNF2_MONITOR_TARGET + '}}'
NS_ALARM_5_REL_PATH = '/'
NS_ALARM_5_OUTPUT_ENV = 'ALARM_RESULT'
NS_ALARM_5_DESC = NS_ALARM_5
NS_ALARM_5_COMP = 'lt'
NS_ALARM_5_THR = 50

NS_ALARM_6 = 'HSS_alarm_2'
NS_ALARM_6_FILE_PACK = NS_ALARM_6 + '_pack.tar.gz'
NS_ALARM_6_STAT_FORMAT = './' + NS_ALARM_6 + '.sh' + \
                         ' -m ' + '{{' + VNF2_MONITOR_TARGET + '}}'
NS_ALARM_6_REL_PATH = '/'
NS_ALARM_6_OUTPUT_ENV = 'ALARM_RESULT'
NS_ALARM_6_DESC = NS_ALARM_6
NS_ALARM_6_COMP = 'gt'
NS_ALARM_6_THR = 100
#   ns Plan
#   ns Plan
#   ns Plan
NS_INSTAN_PLAN_FILE = 'ns-web-lb-instantiate.bpmn'

NS_SCALE_PLAN_1 = 'WEB-SERVER-SCALE-OUT'
NS_SCALE_PLAN_1_FILE = 'web-server-scale-out.bpmn'
NS_SCALE_PLAN_2 = 'WEB-SERVER-SCALE-IN'
NS_SCALE_PLAN_2_FILE = 'web-server-scale-in.bpmn'

#   ns vnf sharing policy
NS_VSP_1 = 'SHARING-DB'
NS_VSP_1_TYPE = 'providing'
NS_VSP_1_VNF_NODE = NS_VNF_N_1

#   ns service exposure policy
NS_SEP_1 = 'LB-WEB-SERVICE'
NS_SEP_1_NAME = NS_SEP_1

NS_SEP_1_MEMBER_1 = NS_SEP_1 + '-member-1'
NS_SEP_1_MEMBER_1_VNF_N = NS_VNF_N_2
NS_SEP_1_MEMBER_1_SERV = VNF2_SERV_1

#   ns scaling policy
NS_SP_1 = 'WEB-SERVER-SCALE-OUT'
NS_SP_1_ALARM = NS_ALARM_1
NS_SP_1_HOOK = 'rest'
NS_SP_1_COOLDOWN = 60
NS_SP_1_PLAN = NS_SCALE_PLAN_1
NS_SP_1_DESC = NS_SP_1

NS_SP_1_ACTION_1 = NS_SP_1 + '-action-1'
NS_SP_1_ACTION_1_VNF = NS_VNF_N_2
NS_SP_1_ACTION_1_OP = VNF2_SCALE_OP_1

############ NS FLAVOR DESIGN DEFINITION #############

#   ns flavor id
NS_F = 'vEPC-FLAVOR'

#   ns sla flavor
NS_F_SLA_1 = NS_SLA_1
NS_F_SLA_1_VALUE = 100

#   vnfc deploy flavor
NS_F_VNFC1_FLAVOR_VALUE = '[ m1.large ]'
NS_F_VNFC1_IMAGE_VALUE = 'spgw'

NS_F_VNFC2_FLAVOR_VALUE = '[ m1.large ]'
NS_F_VNFC2_IMAGE_VALUE = 'mme'

NS_F_VNFC3_FLAVOR_VALUE = '[ m1.large ]'
NS_F_VNFC3_IMAGE_VALUE = 'hss'

NS_F_VNFC4_FLAVOR_VALUE = '[ m1.large ]'
NS_F_VNFC4_IMAGE_VALUE = 'ubuntu14.04'


#   vnfc config flavor
NS_F_VNFC_CONF_VALUE_1 = '{{get_privateIp: ' + VNFC1_EP_1 + '}}' # NS_VNF_N_2 VNF2_VNFC_N_2 VNFC1_PROP_5
NS_F_VNFC_CONF_VALUE_2 = '{{get_privateIp: ' + VNFC2_EP_1 + '}}' # NS_VNF_N_2 VNF2_VNFC_N_2 VNFC1_PROP_5 
NS_F_VNFC_CONF_VALUE_5 = '{{get_privateIp: ' + VNFC3_EP_1 + '}}' # NS_VNF_N_1 VNF1_VNFC_N_1 VNFC3_PROP_3

NS_F_VNFC_CONF_VALUE_6 = '{{get_publicIp: ' + VNFC1_EP_1 + '}}' # NS_VNF_N_2 VNF2_VNFC_N_2 VNFC1_PROP_5
NS_F_VNFC_CONF_VALUE_7 = '{{get_publicIp: ' + VNFC2_EP_1 + '}}' # NS_VNF_N_2 VNF2_VNFC_N_2 VNFC1_PROP_5 
NS_F_VNFC_CONF_VALUE_8 = '{{get_publicIp: ' + VNFC3_EP_1 + '}}' # NS_VNF_N_1 VNF1_VNFC_N_1 VNFC3_PROP_3

#   vnf monitor flavor
NS_F_VNF_MON_CONF_VALUE_1 = '10.10.26.158' # NS_VNF_N_2 VNF2_MONITOR_OPT_1 VNF2_MONITOR_OPT_1_CONFIG_1


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
        #vnfc_t.add_config_property(VNFC1_PROP_2, VNFC1_PROP_2)
        vnfc_t.add_config_property(VNFC1_PROP_5, VNFC1_PROP_5)
        vnfc_t.add_config_property(VNFC1_PROP_4, VNFC1_PROP_4)

        vnfc_t.add_interface(VNFC1_IF_CONFIGURE, 'configure', VNFC_IF_ORDER, VNFC1_IF_CONFIGURE_FORMAT, 
                             VNFC1_IF_ABS_PATH, VNFC1_IF_CONFIGURE)
        vnfc_t.add_interface(VNFC1_IF_START, 'start', VNFC_IF_ORDER, VNFC1_IF_START_FORMAT, 
                             VNFC1_IF_ABS_PATH, VNFC1_IF_START)
        vnfc_t.add_interface(VNFC1_IF_STOP, 'stop', VNFC_IF_ORDER, \
                VNFC1_IF_STOP_FORMAT, VNFC1_IF_ABS_PATH, VNFC1_IF_STOP)
        
        
        self.vnfc_types[VNFC1_T] = vnfc_t
        
    def add_vnfc2_type(self):
        vnfc_t = VnfcType()
        vnfc_t.set_vnfc_info(VNFC2_T, VNFC2_AFF, VNFC2_T)
        vnfc_t.set_artifact(None, None, 'qcow', VNFC2_IMAGE, VNFC_IMAGE_DIR + VNFC2_IMAGE, 
                            'gzip', None)
        vnfc_t.add_flavor_constraint(NS_F_VNFC2_IMAGE_VALUE, NS_F_VNFC2_FLAVOR_VALUE)
        vnfc_t.add_endpoint(VNFC2_EP_1, VNFC2_EP_1)
        vnfc_t.add_config_property(VNFC2_PROP_1, VNFC2_PROP_1)
        vnfc_t.add_config_property(VNFC2_PROP_2, VNFC2_PROP_2)
        vnfc_t.add_config_property(VNFC2_PROP_5, VNFC2_PROP_5)
        vnfc_t.add_config_property(VNFC2_PROP_3, VNFC2_PROP_3)

        vnfc_t.add_interface(VNFC2_IF_CONFIGURE, 'configure', VNFC_IF_ORDER, VNFC2_IF_CONFIGURE_FORMAT, 
                             VNFC2_IF_ABS_PATH, VNFC2_IF_CONFIGURE)
        vnfc_t.add_interface(VNFC2_IF_START, 'start', VNFC_IF_ORDER, VNFC2_IF_START_FORMAT, 
                             VNFC2_IF_ABS_PATH, VNFC2_IF_START)
        vnfc_t.add_interface(VNFC2_IF_STOP, 'stop', VNFC_IF_ORDER, \
                VNFC2_IF_STOP_FORMAT, VNFC2_IF_ABS_PATH, VNFC2_IF_STOP)
        self.vnfc_types[VNFC2_T] = vnfc_t    
    
    def add_vnfc3_type(self):
        vnfc_t = VnfcType()
        vnfc_t.set_vnfc_info(VNFC3_T, VNFC3_AFF, VNFC3_T)
        vnfc_t.set_artifact(None, None, 'qcow', VNFC3_IMAGE, VNFC_IMAGE_DIR + VNFC3_IMAGE, 
                            'gzip', None)
        vnfc_t.add_flavor_constraint(NS_F_VNFC3_IMAGE_VALUE, NS_F_VNFC3_FLAVOR_VALUE)
        vnfc_t.add_endpoint(VNFC3_EP_1, VNFC3_EP_1)
        vnfc_t.add_config_property(VNFC3_PROP_1, VNFC3_PROP_1)
        vnfc_t.add_config_property(VNFC3_PROP_2, VNFC3_PROP_2)
        vnfc_t.add_config_property(VNFC3_PROP_3, VNFC3_PROP_3)
        vnfc_t.add_interface(VNFC3_IF_CONFIGURE, 'configure', VNFC_IF_ORDER, VNFC3_IF_CONFIGURE_FORMAT, 
                             VNFC3_IF_ABS_PATH, VNFC3_IF_CONFIGURE)
        vnfc_t.add_interface(VNFC3_IF_START, 'start', VNFC_IF_ORDER, VNFC3_IF_START_FORMAT, 
                             VNFC3_IF_ABS_PATH, VNFC3_IF_START)
        vnfc_t.add_interface(VNFC3_IF_STOP, 'stop', VNFC_IF_ORDER, \
                VNFC3_IF_STOP_FORMAT, VNFC3_IF_ABS_PATH, VNFC3_IF_STOP)

        self.vnfc_types[VNFC3_T] = vnfc_t
    
    
    def add_vnfc4_type(self):
        vnfc_t = VnfcType()
        vnfc_t.set_vnfc_info(VNFC4_T, VNFC4_AFF, VNFC4_T)
        vnfc_t.set_artifact(None, None, 'qcow', VNFC4_IMAGE, VNFC_IMAGE_DIR + VNFC4_IMAGE, 
                            'gzip', None)
        vnfc_t.add_flavor_constraint(NS_F_VNFC4_IMAGE_VALUE, NS_F_VNFC4_FLAVOR_VALUE)
        vnfc_t.add_endpoint(VNFC4_EP_1, VNFC4_EP_1)
        #vnfc_t.add_config_property(VNFC1_PROP_2, VNFC1_PROP_2)
        #vnfc_t.add_config_property(VNFC1_PROP_5, VNFC1_PROP_5)
        #vnfc_t.add_interface(VNFC1_IF_CONFIGURE, 'configure', VNFC_IF_ORDER, VNFC1_IF_CONFIGURE_FORMAT, 
        #    VNFC_IF_ABS_PATH, VNFC1_IF_CONFIGURE)
        #vnfc_t.add_interface(VNFC1_IF_START, 'start', VNFC_IF_ORDER, VNFC1_IF_START_FORMAT, 
        #                     VNFC_IF_ABS_PATH, VNFC1_IF_START)
        #vnfc_t.add_interface(VNFC2_IF_STOP, 'stop', VNFC_IF_ORDER, \
        #        VNFC2_IF_STOP_FORMAT, VNFC_IF_ABS_PATH, VNFC2_IF_STOP)
        
        
        self.vnfc_types[VNFC4_T] = vnfc_t

    def add_vnfc_types(self):
        self.add_vnfc1_type()
        self.add_vnfc2_type()
        self.add_vnfc3_type()
        #self.add_vnfc4_type()
######### generate vnfc relationship type ##########
    
    def add_vnfc_relationship_1_type(self):
        vnfc_rel = VnfcRelationshipType()
        vnfc_rel.set_vnfc_relationship_info(VNFC_RELATION_1_T, VNFC_REL_1_S_VNFC_T_1 + ':' + VNFC_REL_1_S_VNFC_EP_1 + 
                                                            '->' + VNFC_REL_1_T_VNFC_T_1 + ':' + VNFC_REL_1_T_VNFC_EP_1)
        vnfc_rel.set_source_end(VNFC_REL_1_S_VNFC_T_1, VNFC_REL_1_S_VNFC_EP_1)
        vnfc_rel.set_target_end(VNFC_REL_1_T_VNFC_T_1, VNFC_REL_1_T_VNFC_EP_1)
        self.vnfc_relationship_types[VNFC_RELATION_1_T] = vnfc_rel

    def add_vnfc_relationship_types(self):
        self.add_vnfc_relationship_1_type()
    
######### generate vnf type ##########

    def add_vnf1_type(self):
        vnf_t = VnfType()
        vnf_t.set_vnf_info(VNF1_T, VNF1_T)
        vnf_t.add_vnfc_node(VNF1_VNFC_N_1, VNF1_VNFC_N_1_T)
        # vnf_t.add_vnfc_node(VNF1_VNFC_N_2, VNF1_VNFC_N_2_T)
        vnf_t.add_endpoint(VNF1_EP_1, VNF1_EP_1_VNFC_N, VNF1_EP_1_VNFC_EP, 
                           VNF1_EP_1_VNFC_N + ':' + VNF1_EP_1_VNFC_EP)
        # vnf_t.add_endpoint(VNF1_EP_2, VNF1_EP_2_VNFC_N, VNF1_EP_2_VNFC_EP,
        #                   VNF1_EP_2_VNFC_N + ':' + VNF1_EP_2_VNFC_EP)
        vnf_t.add_monitor_option(VNF1_MONITOR_TARGET, VNF1_MONITOR_PARAMS)
        vnf_t.add_scale_group('SPGWGroup','SPGW-NODE','1','2','1')
        vnf_t.add_scale_oper('SPGWScaleOut','1','SPGWGroup','SPGW scale out')
        vnf_t.add_scale_oper('SPGWScaleIn','-1','SPGWGroup','SPGW scale in')
        self.vnf_types[VNF1_T] = vnf_t

    def add_vnf2_type(self):
        vnf_t = VnfType()
        vnf_t.set_vnf_info(VNF2_T, VNF2_T)
        vnf_t.add_vnfc_node(VNF2_VNFC_N_1, VNF2_VNFC_N_1_T)
        vnf_t.add_vnfc_node(VNF2_VNFC_N_2, VNF2_VNFC_N_2_T)
        # vnf_t.add_vnfc_node(VNF2_VNFC_N_3, VNF2_VNFC_N_3_T)
        vnf_t.add_connection(VNF2_CONNECT_1, VNF2_CONNECT_1_RELATION_T,
                             VNF2_CONNECT_1_END_1, VNF2_CONNECT_1_END_1_EP,
                             VNF2_CONNECT_1_END_2, VNF2_CONNECT_1_END_2_EP)
        vnf_t.add_endpoint(VNF2_EP_1, VNF2_EP_1_VNFC_N, VNF2_EP_1_VNFC_EP, 
                           VNF2_EP_1_VNFC_N + ':' + VNF2_EP_1_VNFC_EP)
        vnf_t.add_endpoint(VNF2_EP_2, VNF2_EP_2_VNFC_N, VNF2_EP_2_VNFC_EP, 
                           VNF2_EP_2_VNFC_N + ':' + VNF2_EP_2_VNFC_EP)
        # vnf_t.add_endpoint(VNF2_EP_3, VNF2_EP_3_VNFC_N, VNF2_EP_3_VNFC_EP,
        #                    VNF2_EP_3_VNFC_N + ':' + VNF2_EP_3_VNFC_EP)

        vnf_t.add_vnfc_property_mapping(VNF2_MAPPING_1, VNF2_MAP_1_S_VNFC_N, VNF2_MAP_1_S_VNFC_N_PROP,
                                                        VNF2_MAP_1_T_VNFC_N, VNF2_MAP_1_T_VNFC_N_PROP, 
                                                        VNF2_MAPPING_1_MUL_INST_OPT)
        vnf_t.add_vnfc_property_mapping(VNF2_MAPPING_2, VNF2_MAP_2_S_VNFC_N, VNF2_MAP_2_S_VNFC_N_PROP, 
                                                        VNF2_MAP_2_T_VNFC_N, VNF2_MAP_2_T_VNFC_N_PROP, 
                                                        VNF2_MAPPING_1_MUL_INST_OPT)

        '''
        vnf_t.add_exposed_service(VNF2_SERV_1, VNF2_SERV_1_NAME, VNF2_SERV_1_EP, 
                                  VNF2_SERV_1_NAME + '@' + VNF2_SERV_1_EP)
        '''
        vnf_t.add_monitor_option(VNF2_MONITOR_TARGET, VNF2_MONITOR_PARAMS)
        '''
        vnf_t.add_monitor_option(VNF2_MONITOR_OPT_1, VNF2_MONITOR_OPT_1_FILE_PACK, 
                                 VNF_MONITOR_PACK_DIR + VNF2_MONITOR_OPT_1_FILE_PACK,
                               VNF2_MONITOR_OPT_1, VNF2_MONITOR_OPT_1_TARGET)
        vnf_t.add_monitor_config(VNF2_MONITOR_OPT_1, VNF2_MONITOR_OPT_1_CONFIG_1, 
                                 VNF2_MONITOR_OPT_1_CONFIG_1)
        vnf_t.add_monitor_interface(VNF2_MONITOR_OPT_1, VNF2_MONITOR_OPT_1_IF_INSTALL,
                                    'install', VNF_MON_IF_ORDER, 
                                    VNF2_MONITOR_OPT_1_IF_INSTALL_FORMAT, 
                                    VNF_MON_IF_ABS_PATH)
        vnf_t.add_monitor_interface(VNF2_MONITOR_OPT_1, VNF2_MONITOR_OPT_1_IF_START,
                                    'start', VNF_MON_IF_ORDER, 
                                    VNF2_MONITOR_OPT_1_IF_START_FORMAT, 
                                    VNF_MON_IF_ABS_PATH)
        '''
        '''
        vnf_t.add_scale_group(VNF2_SCALE_GROUP_1, VNF2_SCALE_GROUP_1_TARGET, 
                              VNF2_SCALE_GROUP_1_MIN, VNF2_SCALE_GROUP_1_MAX, 
                              VNF2_SCALE_GROUP_1_DEFAULT)
        vnf_t.add_scale_oper(VNF2_SCALE_OP_1, VNF2_SCALE_OP_1_STEP, 
                             VNF2_SCALE_OP_1_T_GROUP, VNF2_SCALE_OP_1_DESC)
        vnf_t.add_scale_oper(VNF2_SCALE_OP_2, VNF2_SCALE_OP_2_STEP, 
                             VNF2_SCALE_OP_2_T_GROUP, VNF2_SCALE_OP_2_DESC)
        '''
        vnf_t.add_scale_group('MMEGroup', 'MME-NODE', '1', '3', '1')
        vnf_t.add_scale_group('HSSGroup', 'HSS-NODE', '1', '2', '1')
        vnf_t.add_scale_oper('MMEScaleOut', '1', 'MMEGroup', 'MME scale out')
        vnf_t.add_scale_oper('HSSScaleOut', '1', 'HSSGroup', 'HSS scale out')
        vnf_t.add_scale_oper('MMEScaleIn', '-1', 'MMEGroup', 'MME scale in')
        vnf_t.add_scale_oper('HSSScaleIn', '-1', 'HSSGroup', 'HSS scale in')
        self.vnf_types[VNF2_T] = vnf_t
    
    def add_vnf_types(self):
        self.add_vnf1_type()
        self.add_vnf2_type()

######### generate vnf relationship type ##########


    def add_vnf_relationship_1_type(self):
        vnf_rel = VnfRelationshipType()
        vnf_rel.set_vnf_relationship_info(VNF_RELATION_1_T, VNF_REL_1_S_VNF_T_1 + ':' + VNF_REL_1_S_VNF_EP_1 + 
                                                            '->' + VNF_REL_1_T_VNF_T_1 + ':' + VNF_REL_1_T_VNF_EP_1)
        vnf_rel.set_source_end(VNF_REL_1_S_VNF_T_1, VNF_REL_1_S_VNF_EP_1)
        vnf_rel.set_target_end(VNF_REL_1_T_VNF_T_1, VNF_REL_1_T_VNF_EP_1)
        self.vnf_relationship_types[VNF_RELATION_1_T] = vnf_rel
    
    def add_vnf_relationship_types(self):
        self.add_vnf_relationship_1_type()
    
######### generate ns type ##########

    def add_ns_type(self):
        ns_t = NsType()
        ns_t.set_ns_info(NS_T, NS_T)
        ns_t.add_vnf_node(NS_VNF_N_1, NS_VNF_N_1_T)
        ns_t.add_vnf_node(NS_VNF_N_2, NS_VNF_N_2_T)
        ns_t.add_endpoint(NS_EP_1, NS_EP_1_VNF_N, NS_EP_1_VNF_EP, 
                          NS_EP_1_VNF_N + ':' + NS_EP_1_VNF_EP)
        
        ns_t.add_connection(NS_CONNECT_1, NS_CONNECT_1_RELATION_T, 
                            NS_CONNECT_1_END_1, NS_CONNECT_1_END_1_EP, 
                            NS_CONNECT_1_END_2, NS_CONNECT_1_END_2_EP)
        
        ns_t.add_vnf_property_mapping(NS_MAPPING_1, NS_MAP_1_S_VNF_N_1, NS_MAP_1_S_VNFC_N_1, NS_MAP_1_S_VNFC_N_PROP_1, 
                                                NS_MAP_1_T_VNF_N_1, NS_MAP_1_T_VNFC_N_1, NS_MAP_1_T_VNFC_N_PROP_1, 
                                                NS_MAPPING_1_MUL_INST_OPT)
        '''
        ns_t.add_metric(NS_METRIC_1, NS_METRIC_1_NAME, NS_METRIC_1_NAME)
        ns_t.add_metric_dimension(NS_METRIC_1, NS_METRIC_1_DIM, NS_METRIC_1_DIM_NAME, 
                                  NS_METRIC_1_INTERVAL, NS_METRIC_1_DIM_NAME)
        ns_t.add_sla(NS_SLA_1, NS_SLA_1)
        '''
        ns_t.add_alarm(NS_ALARM_1, NS_ALARM_1_FILE_PACK, NS_ALARM_PACK_DIR + NS_ALARM_1_FILE_PACK, NS_ALARM_1_STAT_FORMAT, 
                       NS_ALARM_1_REL_PATH, NS_ALARM_1_OUTPUT_ENV, NS_ALARM_1_COMP, NS_ALARM_1_THR, NS_ALARM_1_DESC)
        ns_t.add_alarm(NS_ALARM_2, NS_ALARM_2_FILE_PACK, NS_ALARM_PACK_DIR + NS_ALARM_2_FILE_PACK, NS_ALARM_2_STAT_FORMAT,
                       NS_ALARM_2_REL_PATH, NS_ALARM_2_OUTPUT_ENV, NS_ALARM_2_COMP, NS_ALARM_2_THR, NS_ALARM_2_DESC)
        ns_t.add_alarm(NS_ALARM_3, NS_ALARM_3_FILE_PACK, NS_ALARM_PACK_DIR + NS_ALARM_3_FILE_PACK, NS_ALARM_3_STAT_FORMAT,
                       NS_ALARM_3_REL_PATH, NS_ALARM_3_OUTPUT_ENV, NS_ALARM_3_COMP, NS_ALARM_3_THR, NS_ALARM_3_DESC)
        ns_t.add_alarm(NS_ALARM_4, NS_ALARM_4_FILE_PACK, NS_ALARM_PACK_DIR + NS_ALARM_4_FILE_PACK, NS_ALARM_4_STAT_FORMAT,
                       NS_ALARM_4_REL_PATH, NS_ALARM_4_OUTPUT_ENV, NS_ALARM_4_COMP, NS_ALARM_4_THR, NS_ALARM_4_DESC)
        ns_t.add_alarm(NS_ALARM_5, NS_ALARM_5_FILE_PACK, NS_ALARM_PACK_DIR + NS_ALARM_5_FILE_PACK, NS_ALARM_5_STAT_FORMAT,
                       NS_ALARM_5_REL_PATH, NS_ALARM_5_OUTPUT_ENV, NS_ALARM_5_COMP, NS_ALARM_5_THR, NS_ALARM_5_DESC)
        ns_t.add_alarm(NS_ALARM_6, NS_ALARM_6_FILE_PACK, NS_ALARM_PACK_DIR + NS_ALARM_6_FILE_PACK, NS_ALARM_6_STAT_FORMAT,
                       NS_ALARM_6_REL_PATH, NS_ALARM_6_OUTPUT_ENV, NS_ALARM_6_COMP, NS_ALARM_6_THR, NS_ALARM_6_DESC)
        ns_t.add_instantiate_plan(NS_INSTAN_PLAN_FILE, PLAN_DIR + NS_INSTAN_PLAN_FILE, 'instantiation plan')
        '''
        ns_t.add_scaling_plan(NS_SCALE_PLAN_1, NS_SCALE_PLAN_1_FILE, PLAN_DIR + NS_SCALE_PLAN_1_FILE, NS_SCALE_PLAN_1)
        ns_t.add_scaling_plan(NS_SCALE_PLAN_2, NS_SCALE_PLAN_2_FILE, PLAN_DIR + NS_SCALE_PLAN_2_FILE, NS_SCALE_PLAN_2)

        ns_t.add_vnf_sharing_policy(NS_VSP_1, NS_VSP_1_TYPE, NS_VSP_1_VNF_NODE)

        ns_t.add_service_exposure_policy(NS_SEP_1, NS_SEP_1_NAME, NS_SEP_1_NAME)
        ns_t.add_exposed_service_member(NS_SEP_1, NS_SEP_1_MEMBER_1, 
                                        NS_SEP_1_MEMBER_1_VNF_N, NS_SEP_1_MEMBER_1_SERV)

        ns_t.add_scaling_policy(NS_SP_1, NS_SP_1_ALARM, NS_SP_1_HOOK, NS_SP_1_COOLDOWN, 
                                NS_SP_1_PLAN, NS_SP_1_DESC)
        ns_t.add_scaling_action_in_vnf(NS_SP_1, NS_SP_1_ACTION_1, NS_SP_1_ACTION_1_VNF, NS_SP_1_ACTION_1_OP)
        '''

        for vnfc in ['SPGW', 'MME', 'HSS']:
            ns_t.add_scaling_plan('%s_out_plan'%(vnfc), '%s_out.bpmn'%(vnfc), PLAN_DIR +'%s_out.bpmn'%(vnfc), '%s_out_plan'%(vnfc))
            ns_t.add_scaling_plan('%s_in_plan'%(vnfc), '%s_in.bpmn'%(vnfc), PLAN_DIR +'%s_in.bpmn'%(vnfc), '%s_in_plan'%(vnfc))
            ns_t.add_scaling_policy('%s_out_policy'%(vnfc), '%s_alarm_1'%(vnfc), 'rest', '60', '%s_out_plan'%(vnfc), '%s scaling out policy'%(vnfc))
            ns_t.add_scaling_policy('%s_in_policy'%(vnfc), '%s_alarm_2'%(vnfc), 'rest', '60', '%s_in_plan'%(vnfc), '%s scaling in policy'%(vnfc))
            if vnfc != 'SPGW':
                ns_t.add_scaling_action_in_vnf('%s_out_policy'%(vnfc), '%s_out_action'%(vnfc), 'MME-HSS-NODE', '%sScaleOut'%(vnfc))
                ns_t.add_scaling_action_in_vnf('%s_in_policy'%(vnfc), '%s_in_action'%(vnfc), 'MME-HSS-NODE', '%sScaleIn'%(vnfc))
            else:
                ns_t.add_scaling_action_in_vnf('%s_out_policy'%(vnfc), '%s_out_action'%(vnfc), 'SPGW-NODE', '%sScaleOut'%(vnfc))
                ns_t.add_scaling_action_in_vnf('%s_in_policy'%(vnfc), '%s_in_action'%(vnfc), 'SPGW-NODE', '%sScaleIn'%(vnfc))
        self.ns_type[NS_T] = ns_t

########## generate ns flavor design ############

    def add_ns_flavor_design(self):
        ns_f = NsFlavorDesign()
        ns_f.add_vnfc_deploy_flavor(NS_VNF_N_1, VNF1_VNFC_N_1, 'openstack','m1.large','spgw')
#        ns_f.add_vnfc_deploy_flavor(NS_VNF_N_1, VNF1_VNFC_N_2)

        ns_f.add_vnfc_deploy_flavor(NS_VNF_N_2, VNF2_VNFC_N_1, 'openstack','m1.large','mme')
        ns_f.add_vnfc_deploy_flavor(NS_VNF_N_2, VNF2_VNFC_N_2, 'openstack','m1.large','hss')
 #       ns_f.add_vnfc_deploy_flavor(NS_VNF_N_2, VNF2_VNFC_N_3)

        ns_f.set_ns_flavor_info(NS_F, NS_T, NS_T + ':' + NS_F)
        ns_f.add_sla_flavor(NS_F_SLA_1, NS_F_SLA_1_VALUE)
        ns_f.add_vnfc_config_flavor(NS_VNF_N_1, VNF1_VNFC_N_1, VNFC1_PROP_5, NS_F_VNFC_CONF_VALUE_1)
        ns_f.add_vnfc_config_flavor(NS_VNF_N_1, VNF1_VNFC_N_1, VNFC1_PROP_4, NS_F_VNFC_CONF_VALUE_6)

        ns_f.add_vnfc_config_flavor(NS_VNF_N_2, VNF2_VNFC_N_1, VNFC2_PROP_3, NS_F_VNFC_CONF_VALUE_2)
        ns_f.add_vnfc_config_flavor(NS_VNF_N_2, VNF2_VNFC_N_1, VNFC2_PROP_1, NS_F_VNFC_CONF_VALUE_7)

        #ns_f.add_vnfc_config_flavor(NS_VNF_N_1, VNF1_VNFC_N_1, VNFC3_PROP_2, NS_F_VNFC_CONF_VALUE_4)
        ns_f.add_vnfc_config_flavor(NS_VNF_N_2, VNF2_VNFC_N_2, VNFC3_PROP_3, NS_F_VNFC_CONF_VALUE_5)
        ns_f.add_vnfc_config_flavor(NS_VNF_N_2, VNF2_VNFC_N_2, VNFC3_PROP_1, NS_F_VNFC_CONF_VALUE_8)

        #ns_f.add_vnf_monitor_config_flavor(NS_VNF_N_2, VNF2_MONITOR_OPT_1, 
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
    gen.add_vnfc_relationship_types()
    gen.add_vnf_types()
    gen.add_vnf_relationship_types()
    gen.add_ns_type()
    gen.add_ns_flavor_design()
    gen.generate_yaml_json() 
