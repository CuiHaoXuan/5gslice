import urllib2
import json

if __name__ == '__main__':
    url = 'http://192.168.0.20:8080/ServiceMgr/hello'
    body = {'flag': 'test','ss': 'nice'}
    body = json.dumps(body)
    http_req = urllib2.Request(url=url,data=body)
    http_req.add_header('Content-type', 'application/json')
    urllib2.urlopen(http_req)
