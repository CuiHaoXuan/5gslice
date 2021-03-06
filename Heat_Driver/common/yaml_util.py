#   util for yaml

import yaml
import json
import os
import logging
from collections import OrderedDict

# logging.basicConfig(filename='yamlUtil.log', 
#                     format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
# log = logging.getLogger('yamlUtil')

if hasattr(yaml, 'CSafeLoader'):
    yaml_loader = yaml.CSafeLoader
else:
    yaml_loader = yaml.SafeLoader

if hasattr(yaml, 'CSafeDumper'):
    yaml_dumper = yaml.CSafeDumper
else:
    yaml_dumper = yaml.SafeDumper

def yaml_ordered_dump(data, stream=None, Dumper=yaml_dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)
    
def yaml_ordered_load(stream, Loader=yaml_loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
    return yaml.load(stream, OrderedLoader)

def json_ordered_load(stream):
    return json.load(stream, object_pairs_hook=OrderedDict)

def json_ordered_dump(data, stream):
    return json.dump(data, stream, object_pairs_hook=OrderedDict)

def json_ordered_loads(json_str):
    return json.loads(json_str, object_pairs_hook=OrderedDict)

def json_ordered_dumps(data):
    return json.dumps(data, object_pairs_hook=OrderedDict)
