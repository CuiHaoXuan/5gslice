import paramiko
import re
from time import sleep


class sshAgent(object):
    def __init__(self, ip, username, password, timeout=300):
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout
        self.t = ''
        self.chan = ''
        self.try_times = 3

    def connect(self):
        while True:
            try:
                self.t = paramiko.Transport(sock=(self.ip, 22))
                self.t.connect(username=self.username, password=self.password)
                self.chan = self.t.open_session()
                self.chan.settimeout(self.timeout)
                self.chan.get_pty()
                self.chan.invoke_shell()
                print u'connected to %s successfully' % self.ip
                print self.chan.recv(65535).decode('utf-8')
                return
            except Exception, e1:
                if self.try_times != 0:
                    print u'connection %s failed,please try again' %self.ip
                    self.try_times -= 1
                else:
                    print u'failed three times , exit'
                    exit(1)

    def close(self):
        self.chan.close()
        self.t.close()

    def send(self, cmd):
        cmd += '\r'
        p = re.compile(r'~]#')

        result = ''
        self.chan.send(cmd)
        while True:
            sleep(0.5)
            ret = self.chan.recv(65535)
            ret = ret.decode('utf-8')
            result += ret
            if p.search(ret):
                return result

'''
if __name__ == '__main__':
    host = sshAgent('10.10.26.179', 'root', '123456')
    host.connect()
    host.send('. /demo-openrc')
    result = host.send('openstack stack create -t /autoscaling/test/heat_driver_test/2017-10-11-00-11SPGW-VNF01/vnf-2017-10-11-00-11@SPGW-VNF01.yaml stack4')
    print result
    result = result.decode("unicode-escape")
    print type(result)
    if result.find("CREATE_IN_PROGRESS") != -1 :
	print "CREATE_IN_PROGRESS"
    host.close()
'''
