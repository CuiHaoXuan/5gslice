#   util

import inspect
import os

from ext.ftp.ftp_client import Xfer as FTP_C

#   configuration yaml file path
CONF_FILE = 'configure_files/conf.yaml'

#   context namespace involved
CONTEXT_NAMESPACE_CSAR = 'csar'
CONTEXT_NAMESPACE_SLICE = 'slice'
CONTEXT_NAMESPACE_NS_COMBO = 'ns_combo'

#   event producer type involved
EVENT_PRODUCER_LOCAL_REST = 'local_rest_api'

#   event type involved
EVENT_TYPE_LOCAL_NS_COMBO_UPLOAD = 'local_ns_combo_upload_request'
EVENT_TYPE_NS_COMBO_ONBOARDING = 'ns_combo_onboarding_request'
EVENT_TYPE_NS_COMBO_INSTANTIATION = 'ns_combo_instantiation_request'
EVENT_TYPE_NS_COMBO_INFO_ACQ = 'ns_combo_info_acquire'

EVENT_TYPE_LOCAL_CSAR_UPLOAD = 'local_csar_upload_request'
EVENT_TYPE_CSAR_ONBOARDING = 'csar_onboarding_request'
EVENT_TYPE_CSAR_INFO_ACQ = 'csar_info_acquire'

EVENT_TYPE_SLICE_INSTANTIATION = 'slice_instantiation_request'
EVENT_TYPE_SLICE_INFO_ACQ = 'slice_info_acquire'

#   id namespace involved

#   job unit sequence involved
JOB_SEQ_LOCAL_NS_COMBO_UPLOAD = 'local_ns_combo_upload_job_seq'
JOB_SEQ_NS_COMBO_ONBOARDING = 'ns_combo_onboarding_job_seq'
JOB_SEQ_NS_COMBO_INSTANTIATION = 'ns_combo_instantiation_job_seq'

JOB_SEQ_LOCAL_CSAR_UPLOAD = 'local_csar_upload_job_seq'
JOB_SEQ_CSAR_ONBOARDING = 'csar_onboarding_job_seq'

JOB_SEQ_SLICE_INSTANTIATION = 'slice_instantiation_job_seq'

#   thread pool config
TASK_THREADPOOL_SIZE = 20 # thread pool size used for task scheudler to start task
TASK_SHARED_THREADPOOL_SIZE = 20 # thread pool size used for all the tasks in a scheduler
TASK_OWN_THREADPOOL_SIZE = 5 # a per task thread pool size if needed
SUB_NS_INSTAN_THREADPOOL_SIZE = 5 # a thread pool size used for the thread pool of executing sub slice instantiation

#   other global variables
PROTO_FTP = 'ftp'
PROTO_HTTP = 'http'

CSAR_STATUS_UPLOADING = 'upoloading'
CSAR_STATUS_UPLOADED = 'uploaded'
CSAR_STATUS_ONBOARDING = 'onboarding'
CSAR_STATUS_ONBOARDED = 'onboarded'

SLICE_STATUS_INIT = 'initiated'
SLICE_STATUS_RES_INISTANTIATING = 'resource instantiating'
SLICE_STATUS_RES_FAIL = 'resource instantiation fails'
SLICE_STATUS_RES_COMPLETE = 'resource instantiation completes'

SLICE_STATUS_CONF_INISTANTIATING = 'configuration instantiating'
SLICE_STATUS_CONF_FAIL = 'configuration instantiation fails'
SLICE_STATUS_CONF_COMPLETE = 'configuration instantiation completes'

SLICE_RES_STATUS_DEPLOYING = 'deploying'
SLICE_RES_STATUS_COMPLETE = 'deployment completes'
SLICE_RES_STATUS_FAIL = 'deployment fails'

VNF_MGMT_AGENT_VIM_TYPE = 'openstack'
VNF_MGMT_AGENT_FLAVOR_TYPE = 'm1.tiny'
VNF_MGMT_AGENT_OS_TYPE = 'ubuntu14.04'

LOCAL_SERVICE_CSAR_UPLOAD = 'csar_upload'
LOCAL_SERVICE_CSAR_ONBOARDING = 'csar_onboarding'
LOCAL_SERVICE_SUBSLICE_INSTANTIATION = 'subslice_instantiation'

COMPONENT_NAME_E2E_RES_MGR = 'e2eResourceMgr'
SERVICE_SLICE_RES_DEPLOY = 'slice_resource_deploy'
SERVICE_SLICE_RES_ACQUIRE = 'slice_resource_acquire'

COMPONENT_NAME_NF_MGR = 'networkFunctionMgr'
SERVICE_SLICE_INTF_REGISTER = 'slice_intf_register'

COMPONENT_NAME_PLAN_ENGINE = 'planEngine'
SERVICE_SLICE_PLAN_REGISTER = 'slice_plans_register'
SERVICE_SLICE_PLAN_ACQ = 'slice_plans_acquire'
SERVICE_SLICE_INSTAN_PLAN_EXEC = 'slice_instan_plan_exec'


def get_class_func_name(cls):

    '''
    return the class name and the on calling function's name

    '''
    return (cls.__class__.__name__, inspect.stack()[1][3])

def unpack(pack_local_path=None):

    '''
    this func is used to unpack a pack file.
    this func accept inputs as follows:
        'pack_local_path': the local path of the pack file
    this func outputs as follows:
        'unpack_target_dir': the target dir where the unpack files are put
    '''
    curr_dir = os.getcwd()
    unpack_target_dir = os.path.abspath(os.path.join(curr_dir, 'unpack_tmp', ''))
    if not os.path.exists(unpack_target_dir):
        os.mkdir(unpack_target_dir)
    local_dir, pack_name = os.path.split(pack_local_path)
    os.chdir(unpack_target_dir)
    os.system('tar -xzvf ' + pack_local_path)
    os.chdir(curr_dir)
    pack_name = pack_name.replace('.tar.gz', '').replace('.zip', '')
    unpack_target_dir = os.path.join(unpack_target_dir, pack_name, '')
    return unpack_target_dir

def cata_upload(ip_addr, t_port, pro, usr, passwd, 
                             local_files_dir=None, target_upload_path=None):

    '''
    this func is used to upload files to the catalogue.
    this func accept inputs as follows:
        'ip_addr': ip address of the catalogue server
        't_port': port of the csatalogue server
        'pro': protocal used for transporting
        'usr': username of the csatalogue server
        'passwd': password of the csatalogue server
        'local_files_dir': the local dir of the files wanted to be uploaded
        'target_upload_path': the target path where the files will be uploaded to in the catalogue
    '''
    if pro == PROTO_FTP:
        ftp_c = FTP_C()
        ftp_c.setFtpParams(ip_addr, usr, passwd, t_port)
        ftp_c.initEnv()
        dir_path = target_upload_path.split('/')
        for d in dir_path:
            try:
                ftp_c.ftp.cwd(d)
            except Exception, e:
                ftp_c.ftp.mkd(d)
                ftp_c.ftp.cwd(d)
        ftp_c.clearEnv()
        ftp_c.dirUpload(local_files_dir, target_upload_path)

def cata_download(ip_addr, t_port, pro, usr, passwd, 
                             local_file_path=None, target_file_path=None):

    '''
    this func is used to download a file from the catalogue.
    this func accept inputs as follows:
        'ip_addr': ip address of the catalogue server
        't_port': port of the csatalogue server
        'pro': protocal used for transporting
        'usr': username of the csatalogue server
        'passwd': password of the csatalogue server
        'local_file_path': the local path of the file to store the download file
        'target_file_path': the catalogue path of the target file will be downloaded
    '''
    if pro == PROTO_FTP:
        ftp_c = FTP_C()
        ftp_c.setFtpParams(ip_addr, usr, passwd, t_port)
        ftp_c.downloadFile(target_file_path, local_file_path)

def del_dir_or_file(del_local_path=None):

    '''
    this func is used to delete a dir or a file.
    this func accept inputs as follows:
        'del_local_path': the local path of the dir or the file be wanted to deleted
    '''
    os.system('rm -rf ' + os.path.abspath(del_local_path))
