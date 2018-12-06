#   The class of the slice plans register job unit


import os
from collections import OrderedDict
import urllib2

from common.util import get_class_func_name, cata_download, del_dir_or_file, \
                            CONTEXT_NAMESPACE_SLICE, \
                            COMPONENT_NAME_PLAN_ENGINE, SERVICE_SLICE_PLAN_REGISTER, SERVICE_SLICE_PLAN_ACQ
from common.yaml_util import yaml_ordered_load as yaml_load, yaml_ordered_dump as yaml_dump, json_ordered_loads as json_loads
from event_framework.job_unit import JobUnit
from event_framework.event import META_EVENT_TYPE, META_EVENT_PRODUCER


__author__ = 'chenxin'    
__date__ = '2017-6-17'  
__version__ = 1.0



class SlicePlanRegisterJob(JobUnit):
    
    '''
    this job is used to register the plans of the slice to the plan engine.
    this job get inputs:
        slice_id:
    the works done by this job are:
        read the plan info in the slice meta and download the plan files from the catalogue
        read the plan files, and send to the plan engine component to register
        record the plan id returned into the slice ctx
        acquire the process info of the registered plans and record the process id

    '''
    
    
    def __init__(self, task_unit, job_n, **params):
        
        '''
        params:
            task_unit: the task unit instance this job unit belongs to
            job_n: the name of this job given in the job unit sequence
            params: other parameters may used for extension
        '''
        super(SlicePlanRegisterJob, self).__init__(task_unit, job_n, **params)

    def execute_job(self, **params):

        '''
        called by the task unit to start the execution of this job.
        derived job unit class should override this method to deploy own processing logic

        '''
        
        try:
            self.slice_id = params['slice_id']

            self.sch = self.task_unit.task_scheduler
            self.cata_ip = self.sch.get_catalogue_serv_ip()
            self.cata_port = self.sch.get_catalogue_serv_port()
            self.cata_proto = self.sch.get_catalogue_serv_proto()
            self.cata_usr = self.sch.get_catalogue_serv_username()
            self.cata_passwd = self.sch.get_catalogue_serv_password()

            self._gen_local_download_tmp_dir()
            self._register_plans()
            self._execution_finish()
        except Exception, e:
            print Exception, ':', e, \
                      ' in %s:%s' % get_class_func_name(self)
            self._execution_exception(Exception, e)      

    
    
    def _gen_local_download_tmp_dir(self):

        '''
        generate a tmp local dir to put the download plan files

        '''
        if not os.path.exists('plan_download_tmp'):
            os.mkdir('plan_download_tmp')
        cur_dir = os.path.abspath(os.getcwd())
        os.chdir('plan_download_tmp')
        if os.path.exists(self.slice_id):
            os.system('rm -r ' + self.slice_id)
        os.mkdir(self.slice_id)
        self.plan_local_dir = os.path.abspath(self.slice_id)
        os.chdir(cur_dir)
        
    def _register_plans(self):
        
        '''
        download and read the plan files
        send to the plan engine to register
        record the plan id returned into the slice ctx plan info
        acquire the plan process info and record the plan process id
        the slice ctx plan info constructs as:
            planInfo:
                instanPlan:
                    rtPlanId:
                    rtProcessId:
                scalingPlans:
                    (planId):
                        rtPlanId:
                        rtProcessId:

        '''
        ctx_store = self.task_unit.task_scheduler.context_store
        ctx_h = ctx_store.get_context_item_process_handler(CONTEXT_NAMESPACE_SLICE, self.slice_id)
        slice_ctx = ctx_h.get_context_item()
        csar_cata_dir = slice_ctx['csarCataDir']
        plan_info_meta = slice_ctx['metadata']['planInfo']
        plan_ctx = slice_ctx.setdefault('planInfo', OrderedDict())
        rt_plan_dict = {}

        ######   register the instantiate plan to the plan engine ########
        instan_plan_ctx = plan_ctx.setdefault('instanPlan', {})
        
        #   download and read the instantiate plan file
        plan_name = plan_info_meta['instantiatePlan']['planFile']
        plan_cata_path = os.path.join(csar_cata_dir, plan_info_meta['instantiatePlan']['csarFilePath'])
        plan_local_path = os.path.join(self.plan_local_dir, plan_name)
        cata_download(self.cata_ip, self.cata_port, self.cata_proto, self.cata_usr, self.cata_passwd, 
                             plan_local_path, plan_cata_path)

        #   send the instantiate plan to the plan engine to register
        instan_plan_ctx['rtPlanId'] = self._send_plan_file(plan_local_path)
        instan_plan_ctx['rtProcessId'] = None
        rt_plan_dict[instan_plan_ctx['rtPlanId']] = instan_plan_ctx
        #   print '#### SlicePlanRegisterJob: instan plan register completes'
        del_dir_or_file(plan_local_path)

        ###### register the scaling plan to the plan engine #######
        scale_plan_ctx = plan_ctx.setdefault('scalePlan', OrderedDict())
        for plan_id, v in plan_info_meta.get('scalingPlans', {}).items():
            scale_plan_ctx[plan_id] = {}
            
            plan_name = v['planFile']
            plan_cata_path = os.path.join(csar_cata_dir, v['csarFilePath'])
            plan_local_path = os.path.join(self.plan_local_dir, plan_name)
            cata_download(self.cata_ip, self.cata_port, self.cata_proto, self.cata_usr, self.cata_passwd, 
                             plan_local_path, plan_cata_path)

            #   scale_plan_ctx[plan_id]['rtPlanId'] = self._send_plan_file(plan_local_path)
            #   scale_plan_ctx[plan_id]['rtProcessId'] = None
            #   rt_plan_dict[scale_plan_ctx[plan_id]['rtPlanId']] = scale_plan_ctx[plan_id]
            del_dir_or_file(plan_local_path)

        #   acquire the process info of the deployed plans
        rt_plan_process_info = self.task_unit.task_scheduler.\
                         req_remote_serv(COMPONENT_NAME_PLAN_ENGINE, SERVICE_SLICE_PLAN_ACQ, None)
        print '!!!!!!!DEBUG: the response plan info: ', rt_plan_process_info
        for p_info in rt_plan_process_info['data']:
            rt_plan_dict.get(p_info['deploymentId'], {})['rtProcessId'] = p_info['id']
        
        print '#### SlicePlanRegisterJob: slice plan registration complete: '
        print yaml_dump(plan_ctx, default_flow_style=False)

        ctx_h.process_finish()

    def _send_plan_file(self, plan_local_path):

        '''
        send plan file to the plan engine and return the plan id

        '''

        f = open(plan_local_path, 'rb')
        #   l_list = []
        plan_txt = ''
        txt_bound = '------planbound'
        data = []
        for line in f.readlines():
            #   l_list.append(line)
            #   txt_bound = line
            plan_txt = plan_txt + line
        f.close()
        #   txt_bound = txt_bound.split(' ')[-1]
        #   print '#### SlicePlanfRegisterJob: the lines in plan txt: '
        #   print l_list
        data.append('--%s' % txt_bound)
        data.append('Content-Disposition : form-data; name="deployment"; filename="ns-web-lb-instantiate.bpmn"\r\nContent-Type: application/octet-stream\r\nContent-Transfer-Encoding : binary\r\n')
        data.append(plan_txt)
        data.append('--%s--\r\n ' % txt_bound)
        plan_txt = '\r\n'.join(data)
        plan_engin_info = self.sch.other_info['remoteServices'][COMPONENT_NAME_PLAN_ENGINE]
        comp_ip = plan_engin_info['ip']
        comp_port = plan_engin_info['port']
        serv_url = 'http://' + comp_ip + ':' + str(comp_port) + plan_engin_info['services'][SERVICE_SLICE_PLAN_REGISTER]['url']
        
        headers = {'Content-type':'multipart/form-data; boundary=' + txt_bound}
        #   headers = {'Accept': 'application/json', 'Content-type':'multipart/form-data'}
        req = urllib2.Request(serv_url, plan_txt, headers)
        
        #   print '#### SlicePlanfRegisterJob: the text of the plan: ' + plan_txt
        
        plan_id = json_loads(urllib2.urlopen(req).read())['id']

        #   print '#### SlicePlanfRegisterJob: get the plan id: ' + plan_id

        return plan_id
