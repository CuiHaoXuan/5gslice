#!/env/bin/python

#   rest interface for the e2e resource manager

import os
from flask import *

from common.util import *
from common.yaml_util import json_ordered_dumps
from e2e_res_mgr_configurers.e2e_res_mgr_configurer import E2EResMgrConfigurer
from event_framework.context_store import ContextStore


app = Flask(__name__)

SERV_PORT = 8092
SERV_IP = '0.0.0.0'
ROOT_PATH = '/5gslm/iaa'
E2E_RES_MGR = '/e2eResOM/v1'

SLICE_RES_DEPLOY = '/slice/management/create/json'
SLICE_RES_INFO = '/slice/<slice_res_id>/resource/json'


SCHEDULER_SLICE_RES_PROCESSOR = 'slice_res_processor'

conf = E2EResMgrConfigurer()
slice_res_ctx_store = ContextStore()
slice_res_sch = conf.get_task_scheduler_instance(SCHEDULER_SLICE_RES_PROCESSOR, slice_res_ctx_store)


@app.route(ROOT_PATH + E2E_RES_MGR + SLICE_RES_DEPLOY, methods=['POST'])
def deploy_slice_resource():
    if request.json:
        req = request.json
    if request.form:
        req = request.form
    
    event = slice_res_sch.event_generator.get_event(slice_res_sch.get_event_type(EVENT_TYPE_SLICE_RES_DEPLOY), 
                                               slice_res_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST), 
                                               req)
    event.trigger_event()
    resp_d = jsonify(event.get_event_return_data())

    return resp_d, 201


@app.route(ROOT_PATH + E2E_RES_MGR + SLICE_RES_INFO, methods=['GET'])
def acquire_slice_resource_info(slice_res_id):
    
    event_d = {'slice_res_id': slice_res_id}
    event = slice_res_sch.event_generator.get_event(slice_res_sch.get_event_type(EVENT_TYPE_SLICE_RES_INFO_ACQ), 
                                               slice_res_sch.get_event_producer(EVENT_PRODUCER_LOCAL_REST), event_d)
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
