#   util

import inspect

def get_class_func_name(cls):

    '''
    return the class name and the on calling function's name

    '''
    return (cls.__class__.__name__, inspect.stack()[1][3])