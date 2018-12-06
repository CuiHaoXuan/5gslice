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

def yaml_to_json(yaml_file):
    try:
        yaml_file_name = os.path.basename(yaml_file)
        if not yaml_file_name.endswith('.yaml'):
            raise Exception('the input file must be a yaml file')
        json_file_name = yaml_file_name.replace('.yaml', '.json')
        json_file = os.path.join(os.path.dirname(yaml_file), json_file_name)
        os.system('yaml2json ' + yaml_file + ' ' + json_file)
    except Exception, e:
        print Exception, ":", e

def json_to_yaml(self, json_file):
    try:
        json_file_name = os.path.basename(json_file)
        if not json_file_name.endswith('.json'):
            raise Exception('the input file must be a json file')
        yaml_file_name = json_file_name.replace('.json', '.yaml')
        yaml_file = os.path.join(os.path.dirname(json_file), yaml_file_name)
        os.system('json2yaml ' + json_file + ' ' + yaml_file)
    except Exception, e:
        print Exception, ":", e