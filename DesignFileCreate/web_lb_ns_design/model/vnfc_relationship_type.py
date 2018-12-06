#   model class for VNFC Relationship type definition

from collections import OrderedDict

from common.util.util import get_class_func_name

RELATION_STYLE_SET = ('connectTo', 'dependsOn')

class VnfcRelationshipType(object):
    
    def __init__(self):
        self.model = OrderedDict()
        self.model['Info'] = OrderedDict()
        self.model['SourceEndType'] = OrderedDict()
        self.model['TargetEndType'] = OrderedDict()

    def set_vnfc_relationship_info(self, type_id, desc, 
                 style='connectTo', ver='1.0.0', vendor='iaa'):
        self.model['Info']['vnfcRelationshipTypeId'] = type_id
        try:
            if style not in RELATION_STYLE_SET:
                raise Exception('unknown relationship type: %s' % style)
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
        self.model['Info']['relationshipStyle'] = style
        self.model['Info']['version'] = ver
        self.model['Info']['vendor'] = vendor
        self.model['Info']['description'] = desc
        
    
    def set_source_end(self, vnfc_t_id, vnfc_ep_id):
        self.model['SourceEndType']['vnfcTypeId'] = vnfc_t_id
        self.model['SourceEndType']['vnfcEndPointId'] = vnfc_ep_id               

    def set_target_end(self, vnfc_t_id, vnfc_ep_id):
        self.model['TargetEndType']['vnfcTypeId'] = vnfc_t_id
        self.model['TargetEndType']['vnfcEndPointId'] = vnfc_ep_id                

    def load_model(self, model_dict):
        self.model = model_dict
    
    def get_model(self):
        return self.model
