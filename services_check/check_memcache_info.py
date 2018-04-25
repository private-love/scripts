#!/usr/bin python
#coding:utf-8

import paramiko
import re
import time
import string, os, sys  
from datetime import *
import json
import global_functions as func
import Excel
import MySQL

reload(sys)
sys.setdefaultencoding('utf-8')

class NewClient(paramiko.SSHClient):
    def call(self, command, bufsize=-1):
        chan = self._transport.open_session()
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        status = chan.recv_exit_status()
        return stdin, stdout, stderr, status
        
def check_memcache_info(Y,y,m,d):
	"""
	每日检查memcache信息 主体函数
	Y:完整年份 如：2015
	y:年份缩写 如：15
	m：月份
	d：天
	"""
	result = []
	result_mail = []
	list_pidname = []
	err_result = {}
	total_size = 0
	
	check_list = [xxx]

    	for item in check_list:
		hostport = item.split(":")
		host = hostport[0]
		port = int(hostport[1])
		# 检查主机信息
		key = ""
		user = ""
		passwd = ""

		day=datetime.now()
                nowday=day.weekday()
		if str(nowday) :
        		tc = NewClient()
        		tc.load_system_host_keys()
        		tc._policy = paramiko.AutoAddPolicy()
			isDebug = func.get_config('global_value','isDebug')
			try:
				if not os.path.exists(key):
					key = func.key_path
				if not user :
					user = func.key_user

                		tc.connect(host,port=port, username=user, password=passwd,key_filename=key, timeout=10) 
			
				ip_stdin, ip_stdout, ip_stderr, ip_status = tc.call("ifconfig | awk -F'addr:|Bcast' '/Bcast/{print $2}'|grep '192.168'|head -n 1")
				host_ip = ip_stdout.read().strip()
				stdin, stdout, stderr, status = tc.call("netstat -nltp|grep memcached")
				data = stdout.read()
				res = data.split("\n")
				for line in res :
					if line :
						tmp_list = re.split("[ ]+",line.strip())
						host_port = tmp_list[3]
                				software_name = tmp_list[6]
						if not str(software_name) in list_pidname :
                        				list_pidname.append(str(software_name))
							if software_name.split('/')[1] == "memcached" :
								memcache_stats = {}
                                				memcache_stats['host_port'] = host_port
                                				memcache_stats['host_ip'] = host_ip
                                				memcache_bind_ip = host_port.split(':')[0]
                                				if memcache_bind_ip == '0.0.0.0' :
                                        				memcache_bind_ip = host_ip

                                				memcache_bind_port = host_port.split(':')[1]
                                				nc_stdin, nc_stdout, nc_stderr, nc_status = tc.call("echo \"stats\"|nc -w 2 "+str(memcache_bind_ip)+" "+str(memcache_bind_port))
								memcache_stats_nc = nc_stdout.read()
                                				if memcache_stats_nc :
                                        				memcache_stats_list = memcache_stats_nc.split("\n")

                                				for stats in memcache_stats_list:
                                        				if stats.strip().startswith('STAT') :
                                                				stat_list = stats.strip().split()
                                                				memcache_stats[stat_list[1]] = stat_list[2]

								time_uptime = int(memcache_stats['time']) - int(memcache_stats['uptime'])
								diff_day,diff_hour,diff_minute,diff_sec = func.get_diff_time(times=time_uptime)
								runing_start_str = "%d天%d小时%d分钟%d秒"  %(diff_day,diff_hour,diff_minute,diff_sec)
								if int(memcache_stats['get_hits']) > 0 and int(memcache_stats['get_misses']) > 0 :
									hit_rate_d = float(memcache_stats['get_hits'])/(float(memcache_stats['get_hits']) + float(memcache_stats['get_misses'])) 
									hit_rate = round(hit_rate_d,2)*100
									miss_rate_d = float(memcache_stats['get_misses'])/( float(memcache_stats['get_hits']) + float(memcache_stats['get_misses']))
									miss_rate = round(miss_rate_d,2)*100
									hit_rate_dd = float(memcache_stats['get_hits'])/float(memcache_stats['uptime'])
									hit_rated = "%.2f"%(hit_rate_dd)
									miss_rate_dd = float(memcache_stats['get_misses'])/float(memcache_stats['uptime'])
									miss_rated = "%.2f"%(miss_rate_dd)
								else :
									hit_rate = 0
                                                			miss_rate = 0
                                                			hit_rated = 0
                                                			miss_rated = 0


								list = [str(host)+","+str(memcache_stats['host_port'])+","+str(memcache_stats['pid'])+","+str(memcache_stats['limit_maxbytes'])+","+str(memcache_stats['bytes'])+","+str(memcache_stats['curr_items'])+","+str(memcache_stats['total_items'])+","+str(memcache_stats['version'])+","+str(memcache_stats['uptime'])+","+str(runing_start_str)+","+str(hit_rate)+"%"+","+str(miss_rate)+"%"+","+str(hit_rated)+" req/s"+","+str(miss_rated)+" req/s"+","+str(memcache_stats['get_hits'])+","+str(memcache_stats['get_misses'])]
								diff_bytes = int(memcache_stats['limit_maxbytes'])-int(memcache_stats['bytes'])
								diff_bytes_str = func.convertBytes(float(diff_bytes))
								bytes_str = str(memcache_stats['bytes'])
                                        			stats_list = [str(host)+","+str(memcache_stats['host_port'])+","+str(int(hit_rate))+"%,"+str(int(miss_rate))+"%,"+str(func.convertBytes(float(memcache_stats['limit_maxbytes'])))+","+diff_bytes_str+","+bytes_str]
								if isDebug :
									print stats_list 
								result.append(list)
								result_mail.append(stats_list)
					
                	        stdout.close()
                	        stdin.close()
                	except Exception as err:
				print "error"+str(id)+"###"+str(err)
				err_result[host] = str(id)+"###"+str(err)
				continue

        	tc.close()
	if total_size :
		total_size_str = func.convertBytes(total_size)
	else :
		total_size_str = "0b"
	return result,result_mail,err_result,total_size_str

if __name__ == '__main__':
        is_auto = False

        if len(sys.argv) == 5:
                is_auto = False
                Y = sys.argv[1]
                y = sys.argv[2]
                m = sys.argv[3]
                d = sys.argv[4]
        else:
                is_auto =True
                Y = (datetime.now()).strftime('%Y')
                y = (datetime.now()).strftime('%y')
                m = (datetime.now()).strftime('%m')
                d = (datetime.now()).strftime('%d')

	h = (datetime.now()).strftime('%H')
	M = (datetime.now()).strftime('%M')
	S = (datetime.now()).strftime('%S')

	isSendMail=func.get_config('global_value','isSendMail')
	#主题调用函数
	result,result_mail,err_result,total_size_str = check_memcache_info(Y,y,m,d)

	if len(result) > 1 :
		att_filename = "xls/memcache_list_"+str(Y)+"-"+str(m)+"-"+str(d)+"_"+str(h)+str(M)+str(S)+".xlsx"
		hdngs = ['服务器IP','服务端口','进程ID','总内存','已用内存','当前个数','总个数','版本','在线时间','在线天数','命中比','丢失比','命中率','丢失率','命中数','丢失数']
		exc_ins = Excel.Excel(att_filename,sheet_name='ciSheet', encoding='utf-8')
		exc_ins.backup_xlsx_write(hdngs, result)

	if is_auto and isSendMail == 'yes' and len(result_mail) > 1 :
		hdngs_mail = ['服务器IP','服务端口','命中率','丢失率','总内存','剩余内存','已用内存']
		content=func.toHtml(hdngs_mail,result_mail,total_size_str)
		sub="memcache服务每日统计("+str(Y)+'-'+str(m)+'-'+str(d)+")"
		func.sendMail(sub,content,func.mailto_list,att_filename)
	else:
		print json.dumps('suc!')

	if len(err_result) > 0 and isSendMail == 'yes' :
		err_sub = "memcache服务检查存在错误("+str(Y)+'-'+str(m)+'-'+str(d)+")"
		err_content = func.toErrHtml(err_result)
		func.send_mail(func.mailto_list, err_sub, err_content)
	
