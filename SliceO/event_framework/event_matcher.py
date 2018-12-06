#   The class of the event matcher

from common.util import get_class_func_name
from uuid import NAMESPACE_DNS as NS, uuid3 as cal

CODE = 'utf-8'


__author__ = 'chenxin'    
__date__ = '2017-3-31'  
__version__ = 1.0


class EventMatcher(object):
    
    def __init__(self, target_e_data, target_keys_list, target_meta, target_meta_keys):
        
        '''
        Matcher class used to match a event uniquelly
        params:
            target_e_data: the data of the target event wanted
            target_keys_list: a list of key names indicating which values are concerned
            target_meta: the meta data of the target event wanted
            target_meta_keys: a list of key names indicating which meta are concerned
        '''
        self.target_keys = target_keys_list
        self.target_meta_keys = target_meta_keys
        try:
            t_data = [target_e_data[k] for k in target_keys_list]
            meta = [target_meta[k] for k in target_meta_keys]
            self.result = cal(NS, str(t_data + meta).encode(CODE))
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)

    def match(self, event_d, event_meta):
        
        '''
        trigger the current event via event listener
        params:
            event_d: the data of the check event
            event_meta: the meta of the check event
        
        '''
        try:
            t_data = [event_d.get(k, '') for k in self.target_keys]
            meta = [event_meta.get(k, '') for k in self.target_meta_keys]
            return self.result == cal(NS, str(t_data + meta).encode(CODE))
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            return False
