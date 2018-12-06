#   model class for VNFC type definition

import re
import os
from collections import OrderedDict

from common.util.util import get_class_func_name

OS_VM_FLAVORS = ('m1.tiny', 'm1.small', 'm1.medium', 'm1.large', 'm1.xlarge')
CONFIG_PROPERTY_VALUE_TYPE_SET = ('string', 'num', 'list_string', 'list_num')
PACK_TYPE_SET = ('gzip', 'zip')
INTERFACE_SCOPE_SET = ('install', 'start', 'configure', 'stop')
IMAGE_TYPE_SET = ('qcow', 'raw', 'docker')

class VnfcType(object):
    
    def __init__(self):
        self.model = OrderedDict()
        self.model['Info'] = OrderedDict()
        self.model['DeploymentArtifact'] = OrderedDict()
        self.model['DeploymentFlavorConstraints'] = OrderedDict()
        self.model['DeploymentFlavorConstraints']['hostFlavorDesc'] = OrderedDict()
        self.model['EndPoints'] = OrderedDict()
        self.model['ConfigurableProperties'] = OrderedDict()
        self.model['Interfaces'] = OrderedDict()

    def set_vnfc_info(self, type_id, affi, 
                 desc, ver='1.0.0', vendor='iaa'):
        self.model['Info']['vnfcTypeId'] = type_id
        try:
            if affi.startswith('[') and affi.endswith(']'):
                self.model['Info']['vnfAffiliation'] = \
                [n.strip() for n in re.split(', |  ', affi.strip('[]'))]
            else:
                raise Exception('affiliation must be a list')
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['Info']['version'] = ver
        self.model['Info']['vendor'] = vendor
        self.model['Info']['description'] = desc
    
    def set_artifact(self, file_pack_name, pack_file,
                     image_type=None, image_name=None, image_file=None, pack_type='gzip',
                     root_dir='/usr/local/artifacts/'):
        self.model['DeploymentArtifact']['imageInfo'] = OrderedDict()
        try:
            if image_type and image_type not in IMAGE_TYPE_SET:
                raise Exception('unknown image type: %s' % image_type)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['DeploymentArtifact']['imageInfo']['imageType'] = image_type
        self.model['DeploymentArtifact']['imageInfo']['image'] = image_name
        self.model['DeploymentArtifact']['imageInfo']['getFile'] = image_file
        if image_file:
            if not os.path.exists(os.path.abspath(image_file)):
                os.mknod(os.path.abspath(image_file))
        
        self.model['DeploymentArtifact']['filePackInfo'] = OrderedDict()
        self.model['DeploymentArtifact']['filePackInfo']['filePack'] = file_pack_name
        self.model['DeploymentArtifact']['filePackInfo']['getFile'] = pack_file
        self.model['DeploymentArtifact']['filePackInfo']['packType'] = None
        self.model['DeploymentArtifact']['filePackInfo']['rootDir'] = None
        if pack_file:
            if not os.path.exists(os.path.abspath(pack_file)):
                os.mknod(os.path.abspath(pack_file))
            try:
                if pack_type not in PACK_TYPE_SET:
                    raise Exception('unknown file pack type: %s' % pack_type)
            except Exception, e:
                print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self.model['DeploymentArtifact']['filePackInfo']['packType'] = pack_type
            self.model['DeploymentArtifact']['filePackInfo']['rootDir'] = root_dir               

    def add_flavor_constraint(self, os_type='ubuntu14.04', vm_flavor='[ m1.tiny ]', 
                              vim_type='openstack'):
        self.model['DeploymentFlavorConstraints']['hostFlavorDesc']['vimType'] = vim_type
        try:
            if vm_flavor.startswith('[') and vm_flavor.endswith(']'):
                self.model['DeploymentFlavorConstraints']['hostFlavorDesc']['vmFlavor'] = \
                [n.strip() for n in re.split(', |  ', vm_flavor.strip('[]')) if n.strip() in OS_VM_FLAVORS]
            else:
                raise Exception('vm flavor constraints must be a list')
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        #self.model['DeploymentFlavorConstraints']['hostFlavorDesc']['osType'] = os_type

    def add_endpoint(self, ep_id, desc):
        self.model['EndPoints'][ep_id] = OrderedDict()
        self.model['EndPoints'][ep_id]['description'] = desc

    def add_config_property(self, p_id, desc, v_type='string', d_value=None):
        self.model['ConfigurableProperties'][p_id] = OrderedDict()
        try:
            if v_type not in CONFIG_PROPERTY_VALUE_TYPE_SET:
                raise Exception('unknown property value type: %s' % v_type)
        except Exception, e:
            print Exception, ":", e
        self.model['ConfigurableProperties'][p_id]['valueType'] = v_type
        self.model['ConfigurableProperties'][p_id]['defaultValue'] = d_value
        self.model['ConfigurableProperties'][p_id]['description'] = desc

    def add_interface(self, if_id, scope, order, fm, f_path, desc):
        self.model['Interfaces'][if_id] = OrderedDict()
        try:
            if scope not in INTERFACE_SCOPE_SET:
                raise Exception('unknown interface scope: %s' % scope)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['Interfaces'][if_id]['scope'] = scope
        self.model['Interfaces'][if_id]['order'] = order
        self.model['Interfaces'][if_id]['format'] = fm
        self.model['Interfaces'][if_id]['absPath'] = f_path
        self.model['Interfaces'][if_id]['description'] = desc        

    def load_model(self, model_dict):
        self.model = model_dict
    
    def get_model(self):
        return self.model
