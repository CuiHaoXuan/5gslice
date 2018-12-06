#!/env/bin/python

#   test rest interface for the heat driver

import os
import yaml
from flask import *

class plan_id_gen(object):

    def __init__(self):
        
        self.plan_id = 1

    def plan_id_incre(self):

        self.plan_id += 1

app = Flask(__name__)

id_gen = plan_id_gen()

SERV_PORT = 8094
SERV_IP = '0.0.0.0'
ROOT_PATH = '/5gslm/iaa'
NFM = '/nfm/v1'
PLAN_ENGINE = '/plan_engine/v1'

IF_REGISTER = '/interface/deployment/json'
PLAN_REGISTER = '/repository/deployments'
PLAN_ACQ = '/repository/process-definitions'
PLAN_EXEC = '/runtime/process-instances'

@app.route(ROOT_PATH + NFM + IF_REGISTER, methods=['POST'])
def register_interfaces():
    if request.json:
        req = request.json
    if request.form:
        req = request.form
    
    print '#### NFMTestRest: get interfaces register:'
    print yaml.dump(req, default_flow_style=False)
    r_data = {'status': 'request accepted'}
    resp_d = jsonify(r_data)

    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 201


@app.route(ROOT_PATH + PLAN_ENGINE + PLAN_REGISTER, methods=['POST'])
def register_plans():
    
    print '#### PlanEngineTestRest: get plan register:'
    print request.get_data()
    resp_d = jsonify({'id': 'deployment_' + str(id_gen.plan_id)})
    id_gen.plan_id_incre()
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 201


@app.route(ROOT_PATH + PLAN_ENGINE + PLAN_ACQ, methods=['GET'])
def acquire_plan():
    
    resp_d = {}
    resp_d['data'] = []
    for i in range(1, 9):
        resp_d['data'].append({'id': 'process_' + str(i), 'deploymentId': 'deployment_' + str(i)})
    resp_d = jsonify(resp_d)
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 200


@app.route(ROOT_PATH + PLAN_ENGINE + PLAN_EXEC, methods=['POST'])
def exec_plans():
    if request.json:
        req = request.json
    if request.form:
        req = request.form
    
    print '#### PlanEngineTestRest: get plan execution:'
    print yaml.dump(req, default_flow_style=False)
    resp_d = jsonify({'plan_id': 'deployment_xxxx'})
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 201



@app.errorhandler(500)
def error_occur(error):
    resp = jsonify({'error': 'unknown error'})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return make_response(resp, 500)

def plan_id_incre():
    plan_id += 1

if __name__ == '__main__':
    
    app.run(host=SERV_IP, port=SERV_PORT)
