#coding:utf-8
import paramiko

#创建SSH对象
ssh = paramiko.SSHClient()
# 允许连接不在know_hosts文件中的主机
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 连接服务器
ssh.connect(hostname='192.168.0.241', port=22, username='root',key_filename='/root/.ssh/id_rsa')

# 执行命令
stdin, stdout, stderr = ssh.exec_command('ls')
# 获取命令结果
result = stdout.read()
print result
#print (str(result,encoding='utf-8'))
# 关闭连接
ssh.close()
