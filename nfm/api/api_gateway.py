
class api_gateway(object):

    nfm_driver_root = {'ansible': "/nfm_driver/ansible/v1"}

    root = {
            'nfm_root' : "/nfm/v1", \
            'nfm_driver_root':"/nfm_driver/v1", \
            'plan_engin_root':"/plan_engin/v1" \
            }

    nfm_interfaces = { \
			'root':"http://127.0.0.1:5000/nfm/v1", \
            'file_deployment':"/interface/deployment/json", \
            'interface_invoking':"/interface/invoking/json", \
			'interfaces_invoking':"/interfaces/invoking/json", \
            'file_deployment_response':"/nfm_driver/file_deployment/response/json",\
            'interface_invoking_response':"/5gslm/iaa/nfm_driver/interface_invoking/response/json" \
            }

    plan_engin_interfaces = {
			'root':"http://127.0.0.1:8080/plan_engin/v1",
            'plan_deployment':"/repository/deployments",\
            'plan_delete':"/repository/deployments/",\
            'plan_exec':"/runtime/process-instances" ,\
			'interface_invoking_response':"/5gslm/iaa/nfm/interface_invoking/response/"
            }
    nfm_driver_interfaces = \
            {'drivers':
                {\
                    'ansible': {\
						'root':"http://127.0.0.1:8888/nfm_driver/ansible/v1",\
                        'file_deployment':"/interface/deployment/json",\
                        'interface_invoking':"/interface/invoking/json", \
						'interfaces_invoking':"/interfaces/invoking/json" \
                        }\
                }\
                
            }
    sliceOM = { \
			'root':"http://127.0.0.1:5000/sliceOM/v1",\
            'file_deployment_response':"/interface/deployment_resp/json", \
            'interface_invoking_response':"/interface/invoking_resp/json" \
			}
            
    url = { \
            'nfm': nfm_interfaces, \
            'plan_engin': plan_engin_interfaces, \
            'nfm_driver': nfm_driver_interfaces, \
			'sliceOM':sliceOM
            }


    def getUrl(self, url_info):
        '''
        url_info = {
            'module':nfm/plan_engin/nfm_driver
            'interface':
            'metadata':
                'plan_id':
                'driver_name':
        '''
        if url_info['module'] == 'nfm_driver':
            driver_name = url_info['metadata']['driver_name']
            interface = url_info['interface']
            url_root = self.nfm_driver_interfaces['drivers'][driver_name]['root']
            url_interface = self.nfm_driver_interfaces['drivers'][driver_name][interface]
        else:
            url_root = self.url [url_info['module'] ]['root']
            url_interface = self.url [ url_info['module']][url_info ['interface']]
        request_url = url_root + url_interface

        if url_root == 'plan_engin' and url_interface == 'plan_delete':
            request_url  = request_url + url_info['meta_data']['plan_id']
        
        print "api gateway receives a message, request url information is ", url_info, "result_url is ",request_url

        return request_url
     
