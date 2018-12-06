#   model class for VNF Relationship type definition

from collections import OrderedDict

from common.util.util import get_class_func_name

RELATION_STYLE_SET = ('connectTo', 'dependsOn')

class VnfRelationshipType(object):
    
    def __init__(self):
        self.model = OrderedDict()
        self.model['Info'] = OrderedDict()
        self.model['SourceEndType'] = OrderedDict()
        self.model['TargetEndType'] = OrderedDict()

    def set_vnf_relationship_info(self, type_id, desc, 
                 style='connectTo', ver='1.0.0', vendor='iaa'):
        self.model['Info']['vnfRelationshipTypeId'] = type_id
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
        
    
    def set_source_end(self, vnf_t_id, vnf_ep_id):
        self.model['SourceEndType']['vnfTypeId'] = vnf_t_id
        self.model['SourceEndType']['vnfEndPointId'] = vnf_ep_id               

    def set_target_end(self, vnf_t_id, vnf_ep_id):
        self.model['TargetEndType']['vnfTypeId'] = vnf_t_id
        self.model['TargetEndType']['vnfEndPointId'] = vnf_ep_id                

    def load_model(self, model_dict):
        self.model = model_dict
    
    def get_model(self):
        return self.model