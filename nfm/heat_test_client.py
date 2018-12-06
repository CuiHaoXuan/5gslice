import urllib2
import httplib
import json


if __name__=="__main__":
    file_object = open("MME-HSS-NODE_vnfd.yaml")
    req = "http://localhost:8093/5gslm/iaa/driver/heat/v1/vnf/management/create/json"
    try:
        content = file_object.read()
        data = {
                'sliceResId' : 'slice0',
                'vnfNodeId' : 'WEB',
                'vnfdContent' : content,
                'dcResId' : 'myDcResId'
                }
        data_urlencode = json.JSONEncoder().encode(data)
        request = urllib2.Request(req, data_urlencode)
        result = eval( urllib2.urlopen(request).read() )
        print result['vnfResId']
    finally:
        file_object.close()

    get_res_req = "http://localhost:8093/driver/heat/v1/vnf/" + result['vnfResId'] + "/resource/json"
    
    request = urllib2.Request(get_res_req)
    result = eval( urllib2.urlopen(request).read() )
    print result

