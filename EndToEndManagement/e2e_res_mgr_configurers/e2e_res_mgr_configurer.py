#   The class of the e2e resource management configurer

from collections import OrderedDict
import os

from common.util import get_class_func_name, CONF_FILE
from event_framework.configurer import Configurer


__author__ = 'chenxin'    
__date__ = '2017-4-18'  
__version__ = 1.0

class E2EResMgrConfigurer(Configurer):
    
    '''
    this configurer is used for configuration of the E2E Res O&M service.
    the endpoint info of other services like Heat Driver will be 
    depicted in the Others section in the conf.yaml file, consists as:

    '''
    
    def __init__(self):
        
        f_p = os.path.join(*[os.getcwd(), CONF_FILE])
        super(E2EResMgrConfigurer, self).__init__(f_p)

    def _init(self):
        
        '''
        init method of the configurer, 
        derived configurer class could override this method
        
        '''
        pass
