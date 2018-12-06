import os
import logging
import json
import threading
import uuid
import urllib2
import yaml
from flask import Flask
from flask import request
from tosca import tosca
from api.api_gateway import api_gateway

app = Flask(__name__)
@app.route('/5gslm/iaa/driver/heat/v1/vnf/management/create/json', methods = ['POST'])
def create_vnf():
    if request.json:
        data = request.json
	print 'json'
    elif request.form:
        data = request.form
	print 'form'
    print data['sliceResId']
    my={'stack_id':'ss'}
    return str(my)

if __name__=='__main__':
        app.run(host = '0.0.0.0',port = 8193)

