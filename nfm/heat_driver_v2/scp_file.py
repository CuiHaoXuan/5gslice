import os

scp_put = '''  
spawn scp -r %s %s@%s:%s  
expect "(yes/no)?" {  
send "yes\r"  
expect "password:"  
send "%s\r"  
} "password:" {send "%s\r"}  
expect eof  
exit''' 

if __name__ == '__main__':
    os.system("echo '%s' > scp_put.cmd" % (scp_put % ('/uploadfile', 'root', '192.168.0.21', '/', '123456', '123456')))
    os.system('expect scp_put.cmd')
    os.system('rm scp_put.cmd')
