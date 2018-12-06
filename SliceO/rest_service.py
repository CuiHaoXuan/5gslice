#!/env/bin/python

#   rest interface for the slice manager

import os
from flask import *

from common.util import *
from common.yaml_util import json_ordered_dumps
from slice_mgr_configurers.slice_mgr_configurer import SliceMgrConfigurer
from event_framework.context_store import ContextStore


app = Flask(__name__)

SERV_PORT = 8090
SERV_IP = '0.0.0.0'
ROOT_PATH = '/5gslm/iaa'
SLICE_MGR = '/sliceOM/v1'

NS_COMBO_UPLOAD = '/nscombo/upload/json'
NS_COMBO_ONBOARDING = '/nscombo/<ns_combo_id>/onboarding/json'
NS_COMBO_INSTANTIATE = '/nscombo/<ns_combo_id>/lcm/instantiate/json'
NS_COMBO_INFO = '/nscombo/info/json'

CSAR_UPLOAD = '/csar/upload/json'
CSAR_INFO = '/csar/info/json'
CSAR_ONBOARDING = '/csar/<csar_id>/onboarding/json'

SUBSLICE_INSTANTIATE = '/subslice/<sub_slice_id>/lcm/instantiate/json'
SUBSLICE_INFO = '/subslice/info/json'

SCHEDULER_NS_COMBO_PROCESSOR = 'ns_combo_processor'
SCHEDULER_CSAR_PROCESSOR = 'csar_processor'
SCHEDULER_SLICE_PROCESSOR = 'slice_processor'

#  read the JobUnitSequences part in the conf.yaml, and initiate the conf
conf = SliceMgrConfigurer()

ns_combo_ctx_store = ContextStore()
csar_ctx_store = ns_combo_ctx_store
slice_ctx_store = csar_ctx_store
ns_combo_sch = conf.get_task_scheduler_instance(SCHEDULER_NS_COMBO_PROCESSOR, ns_combo_ctx_store)
csar_sch = conf.get_task_scheduler_instance(SCHEDULER_CSAR_PROCESSOR, csar_ctx_store)
slice_sch = conf.get_task_scheduler_instance(SCHEDULER_SLICE_PROCESSOR, slice_ctx_store)



@app.route(ROOT_PATH + SLICE_MGR + NS_COMBO_UPLOAD, methods=['OPTIONS'])
def upload_ns_combo_options():
    resp_d = jsonify()
    resp_d.headers['Access-Control-Allow-Origin'] = '*'
    return resp_d, 201

@app.route(ROOT_PATH + SLICE_MGR + NS_COMBO_UPLOAD, methods=['POST'])
def upload_ns_combo():
    if request.json:
        req = request.json
    if request.form:
        req = request.form
    event_d = {}
    event_d['packLocalPath'] = req['packLocalPath']
    event_d['nsComboPackName'] = req['nsComboPackName']
    event_d['description'] = req['description']
    event_d['tenantId'] = req['tenantId']
    event_d['tradeId'] = req['tradeId']
    # first parameter is JobUnitSequence object about local_ns_combo_upload_job_seq , second parameter
    # is local_rest_api, third parameter is event_d
    event = ns_combo_sch.event_generator.get_event(ns_combo_sch.get_event_type(EVENT_TYPE_LOCAL_NS_COMBO_UPLOAD), 
                                               ns_combo_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST), 
                                               event_d)
    event.trigger_event()
    resp_d = jsonify(event.get_event_return_data())
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 201

@app.route(ROOT_PATH + SLICE_MGR + NS_COMBO_ONBOARDING, methods=['OPTIONS'])
def onboarding_ns_combo_options():
    resp_d = jsonify()
    resp_d.headers['Access-Control-Allow-Origin'] = '*'
    return resp_d, 201

@app.route(ROOT_PATH + SLICE_MGR + NS_COMBO_ONBOARDING, methods=['POST'])
def onboarding_ns_combo(ns_combo_id):

    event_d = {'ns_combo_id': ns_combo_id}
    event = ns_combo_sch.event_generator.get_event(ns_combo_sch.get_event_type(EVENT_TYPE_NS_COMBO_ONBOARDING), 
                                               ns_combo_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST), 
                                               event_d)
    event.trigger_event()
    resp_d = jsonify(event.get_event_return_data())
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 201

@app.route(ROOT_PATH + SLICE_MGR + NS_COMBO_INSTANTIATE, methods=['OPTIONS'])
def instantiate_ns_combo_options():
    resp_d = jsonify()
    resp_d.headers['Access-Control-Allow-Origin'] = '*'
    return resp_d, 201

@app.route(ROOT_PATH + SLICE_MGR + NS_COMBO_INSTANTIATE, methods=['POST'])
def instantiate_ns_combo(ns_combo_id):

    event_d = {'ns_combo_id': ns_combo_id}
    event = ns_combo_sch.event_generator.get_event(ns_combo_sch.get_event_type(EVENT_TYPE_NS_COMBO_INSTANTIATION), 
                                               ns_combo_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST), 
                                               event_d)
    event.trigger_event()
    resp_d = jsonify(event.get_event_return_data())
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 201


@app.route(ROOT_PATH + SLICE_MGR + NS_COMBO_INFO, methods=['GET'])
def acquire_ns_combo_info():
    
    event = ns_combo_sch.event_generator.get_event(ns_combo_sch.get_event_type(EVENT_TYPE_NS_COMBO_INFO_ACQ), 
                                               ns_combo_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST))
    event.trigger_event()
    resp_d = jsonify(event.get_event_return_data())
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 200

@app.route(ROOT_PATH + SLICE_MGR + CSAR_UPLOAD, methods=['OPTIONS'])
def upload_csar_option():
    resp_d = jsonify()
    resp_d.headers['Access-Control-Allow-Origin'] = '*'
    return resp_d, 201

@app.route(ROOT_PATH + SLICE_MGR + CSAR_UPLOAD, methods=['POST'])
def upload_csar():
    if request.json:
        req = request.json
    if request.form:
        req = request.form
    print "csar upload req"
    print req
    event_d = {}
    event_d['csarLocalPath'] = req['csarLocalPath']
    event_d['csarName'] = req['csarName']
    event_d['nsComboId'] = req['nsComboId']
    event_d['subNsNodeId'] = req['subNsNodeId']
    event_d['tenantId'] = req['tenantId']
    event_d['tradeId'] = req['tradeId']
    event = csar_sch.event_generator.get_event(csar_sch.get_event_type(EVENT_TYPE_LOCAL_CSAR_UPLOAD), 
                                               csar_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST), 
                                               event_d)
    event.trigger_event()
    resp_d = jsonify(event.get_event_return_data())
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 201

@app.route(ROOT_PATH + SLICE_MGR + CSAR_ONBOARDING, methods=['OPTIONS'])
def onboarding_options():
    resp_d = jsonify()
    resp_d.headers['Access-Control-Allow-Origin'] = '*'
    return resp_d, 201

@app.route(ROOT_PATH + SLICE_MGR + CSAR_ONBOARDING, methods=['POST'])
def onboarding_csar(csar_id):

    event_d = {'csar_id': csar_id}
    event = csar_sch.event_generator.get_event(csar_sch.get_event_type(EVENT_TYPE_CSAR_ONBOARDING), 
                                               csar_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST), 
                                               event_d)
    event.trigger_event()
    resp_d = jsonify(event.get_event_return_data())
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 201


@app.route(ROOT_PATH + SLICE_MGR + CSAR_INFO, methods=['GET'])
def acquire_csar_info():
    
    event = csar_sch.event_generator.get_event(csar_sch.get_event_type(EVENT_TYPE_CSAR_INFO_ACQ), 
                                               csar_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST))
    event.trigger_event()
    resp_d = jsonify(event.get_event_return_data())
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 200



@app.route(ROOT_PATH + SLICE_MGR + SUBSLICE_INSTANTIATE, methods=['OPTIONS'])
def instantiate_slice_options():
    resp_d = jsonify()
    resp_d.headers['Access-Control-Allow-Origin'] = '*'
    return resp_d, 201

@app.route(ROOT_PATH + SLICE_MGR + SUBSLICE_INSTANTIATE, methods=['POST'])
def instantiate_slice(sub_slice_id):

    event_d = {'slice_id': sub_slice_id}
    event = slice_sch.event_generator.get_event(slice_sch.get_event_type(EVENT_TYPE_SLICE_INSTANTIATION), 
                                               slice_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST), 
                                               event_d)
    event.trigger_event()
    resp_d = jsonify(event.get_event_return_data())
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 201


@app.route(ROOT_PATH + SLICE_MGR + SUBSLICE_INFO, methods=['GET'])
def acquire_slice_info():
    
    event = slice_sch.event_generator.get_event(slice_sch.get_event_type(EVENT_TYPE_SLICE_INFO_ACQ), 
                                               slice_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST))
    event.trigger_event()
    resp_d = jsonify(event.get_event_return_data())
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 200

@app.errorhandler(500)
def error_occur(error):
    resp = jsonify({'error': 'unknown error'})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return make_response(resp, 500)

if __name__ == '__main__':
    
    app.run(host=SERV_IP, port=SERV_PORT)

'''
if __name__ == '__main__':
    req = {
	"nsComboPackName" : "vEPC-SERVICE_1.0.0_iaa_tenant-1_2017-09-14@16:05:39.tar.gz",
	"tenantId" : "admin",
	"tradeId" : "1",
	"description" : "vEPC",
	"packLocalPath" : "/code_phase_two/NS_combined_package_REST/ns_combo_pack/vEPC-SERVICE_1.0.0_iaa_tenant-1_2017-09-14@16:05:39.tar.gz"
    }

    event_d = {}
    event_d['packLocalPath'] = req['packLocalPath']
    event_d['nsComboPackName'] = req['nsComboPackName']
    event_d['description'] = req['description']
    event_d['tenantId'] = req['tenantId']
    event_d['tradeId'] = req['tradeId']
    event = ns_combo_sch.event_generator.get_event(ns_combo_sch.get_event_type(EVENT_TYPE_LOCAL_NS_COMBO_UPLOAD), 
                                               ns_combo_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST), 
                                               event_d)
    event.trigger_event()
'''
