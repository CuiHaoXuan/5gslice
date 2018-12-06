#   util

import inspect
import os

from ext.ftp.ftp_client import Xfer as FTP_C

#   configuration yaml file path
CONF_FILE = 'configure_files/conf.yaml'

#   context namespace involved
CONTEXT_NAMESPACE_VNF_RES = 'vnf resource'

#   event producer type involved
EVENT_PRODUCER_LOCAL_REST = 'local_rest_api'

#   event type involved
EVENT_TYPE_VNF_RES_DEPLOY = 'vnf_res_deploy_request'
EVENT_TYPE_VNF_RES_INFO_ACQ = 'vnf_res_info_acquire'

#   id namespace involved

#   job unit sequence involved
JOB_SEQ_VNF_RES_DEPLOY = 'vnf_res_deploy_job_seq'

#   remote service type involved
SERV_TYPE_VIM = 'vim'

#   thread pool config
TASK_THREADPOOL_SIZE = 20 # thread pool size used for task scheudler to start task
TASK_SHARED_THREADPOOL_SIZE = 20 # thread pool size used for all the tasks in a scheduler
TASK_OWN_THREADPOOL_SIZE = 5 # a pet task thread pool size if needed

#   other global variables
VNF_RES_STATUS_DEPLOYING = 'deploying'
VNF_RES_STATUS_COMPLETE = 'deployment completes'
VNF_RES_STATUS_FAIL = 'deployment fails'

PREFIX_VDU = 'VDU_'
PREFIX_CP = 'CP_'
PREFIX_INTERNAL_VL = 'internal_VL_'

SUFFIX_PRIVATE_IP = '_privateIp'
SUFFIX_PUBLIC_IP = '_publicIp'


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
    pack_name = pack_name.split('.')[0]
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
        ftp_c.ftp.cwd('~/')
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
