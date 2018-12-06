from ext.ftp.ftp_client import Xfer as FTP_C
import inspect
import os

def test():
    if (1>0) :
        ftp_c = FTP_C()
        ftp_c.setFtpParams('127.0.0.1', 'root', 'iaa','21' )
        ftp_c.initEnv()
	target_upload_path = 'csar_packs/f2232c21-4ea1-32bb-84e1-6cd2c2163392/vEPC-SUBNS-1_vEPC-FLAVOR_vEPC-NS_csar/'
	local_files_dir = '/code_phase_two/SliceO/unpack_tmp/vEPC-SUBNS-1_vEPC-FLAVOR_vEPC-NS_csar/'
        dir_path = target_upload_path.split('/')
        for d in dir_path:
            try:
                ftp_c.ftp.cwd(d)
            except Exception, e:
                ftp_c.ftp.mkd(d)
                ftp_c.ftp.cwd(d)
        ftp_c.clearEnv()
        ftp_c.dirUpload(local_files_dir, target_upload_path)

if __name__ == '__main__':
    test()
