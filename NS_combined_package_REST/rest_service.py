#!/env/bin/python

#   rest interface for the design files packaging

import os
from flask import *
from csar_packer import CsarPacker
from ns_combo_packer import NsComboPacker


app = Flask(__name__)

SERV_PORT = 8091
SERV_IP = '0.0.0.0'
ROOT_PATH = '/5gslm/iaa'
PACK_CREATOR= '/designerCreator/v1'
CSAR_CREATE = '/subns/csar/create/json'
NS_COMBO_CREATE = '/nscombo/subscribe/create/json'


@app.route(ROOT_PATH + PACK_CREATOR + CSAR_CREATE, methods=['POST'])
def create_subns_csar():
    if request.json:
        req = request.json
    if request.form:
        req = request.form
    desgin_files_dir = req['designFilesDir']
    user_uploads_dir = req['userUploadsDir']
    packer = CsarPacker(desgin_files_dir, user_uploads_dir)
    packer.gen_csar_pack()
    resp = {}
    resp['status'] = 'successful creation'
    resp['csarPackagePath'] = packer.get_csar_pack_path()
    resp_d = jsonify(resp)
    resp_d.headers['Access-Control-Allow-Origin'] = '*'

    return resp_d, 201


@app.route(ROOT_PATH + PACK_CREATOR + NS_COMBO_CREATE, methods=['POST'])
def create_ns_combo_pack():
    if request.json:
        req = request.json
    if request.form:
        req = request.form
    ns_combo_flavor_file = req['nsComboFlavorFile']
    ns_combo_sub_file = req['nsComboSubcribeFile']
    sub_ns_files = {}
    for sub_ns, v in req['subNsDesignFiles'].items():
        loc = sub_ns_files.setdefault(sub_ns, {})
        loc['designFilesDir'], loc['userUploadsDir'] = v['designFilesDir'], v['userUploadsDir']
    packer = NsComboPacker(ns_combo_flavor_file, ns_combo_sub_file, sub_ns_files)
    packer.gen_ns_combo_pack()
    resp = {'status':'successful creation'}
    resp['nsComboFlavorPackPath'] = packer.get_ns_combo_pack_path()
    resp_d = jsonify(resp)
    resp_d.headers['Access-Control-Allow-Origin'] = '*'
    return resp_d, 201


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
	'nsComboFlavorFile': '/code_phase_two/DesignFileCreate/ns_combo_design/ns_combo_design_files/vEPC-SERVICE_ns_combo_flavor_design.yaml',
	'nsComboSubcribeFile': '/code_phase_two/DesignFileCreate/ns_combo_design/ns_combo_design_files/vEPC-SERVICE_ns_combo_flavor_subscribe.yaml', 
	'subNsDesignFiles': {
            'vEPC-SUBNS-1': {
		'designFilesDir': '/code_phase_two/DesignFileCreate/web_lb_ns_design/design_files',
		'userUploadsDir': '/code_phase_two/DesignFileCreate/web_lb_ns_design/user_upload_files'
	    }
        } 
    }
    ns_combo_flavor_file = req['nsComboFlavorFile']
    ns_combo_sub_file = req['nsComboSubcribeFile']
    sub_ns_files = {}
    for sub_ns, v in req['subNsDesignFiles'].items():
        loc = sub_ns_files.setdefault(sub_ns, {})
        loc['designFilesDir'], loc['userUploadsDir'] = v['designFilesDir'], v['userUploadsDir']
    packer = NsComboPacker(ns_combo_flavor_file, ns_combo_sub_file, sub_ns_files)
    packer.gen_ns_combo_pack()
'''
