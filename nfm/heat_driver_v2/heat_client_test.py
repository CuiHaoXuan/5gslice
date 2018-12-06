import requests
import json


if __name__=="__main__":
    file_object = open("MME-HSS-NODE_vnfd.yaml")
    req = "http://192.168.0.9:8193/5gslm/iaa/driver/heat/v1/vnf/management/create/json"
    try:
        content = file_object.read()
        data = {
                'sliceResId' : 'slice0',
                'vnfNodeId' : 'WEB',
                'vnfdContent' : content,
                'dcResId' : 'myDcResId'
                }
	headers = {'content-type': 'application/json'}
        data_urlencode = json.dumps(data)
        result = requests.post(req, data=data_urlencode,headers=headers)
	print type(result.text)
        print result.text
    finally:
        file_object.close()

