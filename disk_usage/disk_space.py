#!/usr/bin/env python
#coding=utf-8
#作用：使用zabbix api进行磁盘空间增长量查询统计
#pyzabbix项目地址:https://github.com/blacked/py-zabbix

import sys
import os
import re
import math
import time
from datetime import datetime,timedelta
from pyzabbix import ZabbixAPI
from sendEmail import sendMail
import xlsxwriter

reload(sys)
sys.setdefaultencoding('utf-8')

def convertBytes(bytes,lst=['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']):
	"""
	将文件字节大小转换成可读性更高的单位
	"""
	if bytes == 0:
		return '0 Bytes'
	else:
		i = int(math.floor(math.log(bytes, 1024)))
		if i >= len(lst):
			i = len(lst) - 1
		return ('%.2f' + " " + lst[i]) % (bytes/math.pow(1024, i))

def writeToExcel(title,data,filename):
	totalspace = 0
	totalfree = 0
	totalusage = 0
	workbook = xlsxwriter.Workbook(filename)
	worksheet = workbook.add_worksheet()
	worksheet.set_column(0,len(title)-1,24)
	merge_format = workbook.add_format({'align':'center',
										'valign':'vcenter',
										'border':1})
	warn_format = workbook.add_format({'align':'center',
										'valign':'vcenter',
										'border':1,
										'bg_color':'red'})
	row = 0
	col = 0
	for name in title:
		worksheet.write(row,col,name,merge_format)
		col += 1
	row = 1
	for ip,pathinfo in data.items():
		nextIProw = row + len(pathinfo)-1
		if row == nextIProw:
			worksheet.write(row,0,ip,merge_format)
		else:
			worksheet.merge_range(row,0,nextIProw,0,ip,merge_format)
		for info in pathinfo:
			totalspace = totalspace + info['total']
			totalusage = totalusage + info['usage']
			totalfree = totalfree + info['free']	
			col = 1
			worksheet.write(row,col,info['path'],merge_format)
			col += 1
			worksheet.write(row,col,convertBytes(info['total']),merge_format)
			col += 1
			worksheet.write(row,col,convertBytes(info['free']),merge_format)
			col += 1
			if info['usage'] < 0 :
				#清理磁盘空间导致为负数
				print 'usage is fu'
				usage = convertBytes(abs(info['usage']))
				usage = '-' + usage
			else:
				usage = convertBytes(info['usage'])
			worksheet.write(row,col,usage,merge_format)
			col += 1
			worksheet.write(row,col,info['inode'],merge_format)
			row += 1
		row = nextIProw + 1
	totalinfo = ('总空间：' + convertBytes(totalspace) +
				' 剩余空间：' + convertBytes(totalfree) + 
			   ' 日使用空间：' + convertBytes(totalusage))
	worksheet.merge_range(row,0,row,len(title)-1,totalinfo,merge_format)
	workbook.close()

def infoToHtml(info):
	#转换成html格式
	totalspace = 0
	totalfree = 0
	totalusage = 0
	html = ""
	html += "<table width=\"650\" border=\"1\" cellspacing=\"0\" cellpadding=\"2\">"
	html += "<tr style=\"text-align:center;\">"
	html += "<th>" + "服务器地址" +"</th>" + "<th>" +  "目录" + "</th>" + "<th>总空间</th>" + "<th>" + \
   			"剩余空间" + "</th>" + "<th>" + "日使用量"  + "</th>" + "<th>" + "inodes百分比" + "</th>" +"</tr>"
	#html += "<tr style=\"text-align:center;\">"
	if not info:
		exit()
	for key,values in info.items() :
		#print html
		html += "<tr>"
		html += "<td  rowspan=\"" + str(len(values)) + "\">" + str(key) + "</td>"
		for i in values:
			usage = i['usage']
			totalusage += usage
			if usage < 0 :
				#清理磁盘空间导致为负数
				print 'usage is fu'
				usage = convertBytes(abs(usage))
				usage = '-' + usage
			else:
				usage = convertBytes(usage)
			html += ("<td>" + i['path'] + "</td>" + "<td>" + convertBytes(i['total']) +  "</td>"+"<td>" + 
					convertBytes(i['free'])  + "</td>" + 
					"<td>" + usage + "</td>" + "<td>" + str(i['inode']) + "</td>" + "</tr>" + "<tr>")
			totalfree += int(i['free'])
			totalspace += int(i['total'])
		html += "</tr>" 
	html += ("<tr><td>存储资源汇总：</td> " + "<td colspan=5> 总空间：" + convertBytes(totalspace) + 
			" 剩余空间：" + convertBytes(totalfree) + 
			" 日使用空间：" + convertBytes(totalusage) +
			"</td></tr>" + "</table>")
	print html
	return html

def get_item_history(zapi,hostid,path,gettime,filter,type=3):
	"""通过filter指定过滤需要查找的item值"""
	inodeinfo = zapi.do_request('item.get',{'hostids':hostid,
											'output':['itemid','key_'],
											'filter':filter})
	inodeinfo = inodeinfo['result']
	print inodeinfo
	item = inodeinfo[0]['itemid']
	inodefree = zapi.do_request('history.get',{
												'history':type,
												'hostids':hostid,
												'itemids':item,
												'time_from':gettime,
												'limit':1	
												})
	inodefree = inodefree['result']
	if len(inodefree) == 0:
		return 0
	else:
		return inodefree[0]['value']

def get_itemid(zapi,hostid,output,filter):
	#获取指定的itemid
	#output为list
	#filter为dict
	itemsinfo = zapi.do_request('item.get',{'hostids':hostid,
											'output':output,
											'filter':filter
								})
	itemsinfo = itemsinfo['result']
	print itemsinfo
	return itemsinfo

def get_history(zapi,hostid,itemid,gettime,type=3):
	diskinfo = zapi.do_request('history.get',{
											'history':type,
											'hostids':hostid,
											'itemids':itemid,
											'time_from':gettime,
											'limit':1
											})
	diskinfo = diskinfo['result']
	if len(diskinfo) == 0:
		return {'itemid':itemid,'value':0}
	else:
		return diskinfo[0]

def get_disk_history(zapi,hostlist,gettime):
	global diskitems
	hostdiskinfo = {}
	for hostinfo in hostlist:
		#磁盘item获取
		print '开始获取' + str(hostinfo['host'])
		ip = str(hostinfo['host'])
		hostdiskinfo[ip] = []
		hostid = hostinfo['hostid']
		itemsinfo = get_itemid(zapi,hostid,
								output=['itemid','key_'],
								filter={'name':['Free disk space on $1']}
								)
		itemids = [diskinfo['itemid'] for diskinfo in itemsinfo]
		print itemids
		for diskinfo in itemsinfo:
			diskpath = re.split('[\[,]',diskinfo['key_'])[1]
			print diskinfo['itemid']
			print diskpath
			diskitems[diskinfo['itemid']] = diskpath
		print diskitems
		print itemids
		itemvalues = {}
		'''
		history有4种数据类型类型，对应4张history表，
		可通过item_get的结果获取value_type类型
		'''
		for item in itemids:
			print hostid
			print item
			print diskitems.keys()
			diskinfo = get_history(zapi,hostid,item,gettime)
			print diskinfo
			itemvalues[item] = diskinfo['value']
		hostdiskinfo[ip] = itemvalues
	return hostdiskinfo


def main(argv):
	global diskitems
	global groupname
	global zurl
	global zuser
	global zpasswd
	global sendto
	global serverinfo
	yestday = datetime.today() - timedelta(days=1)
	yestday = datetime.strptime(yestday.strftime('%Y-%m-%d') + ' 00:00:00','%Y-%m-%d %H:%M:%S')
	yestday = time.mktime(yestday.timetuple())
	today = datetime.strptime(datetime.today().strftime('%Y-%m-%d' + ' 00:00:00'),'%Y-%m-%d %H:%M:%S')
	today = time.mktime(today.timetuple())
	print '查询范围：' + str(yestday) + ' - ' + str(today)  
	zapi = ZabbixAPI(url = zurl, user = zuser, password=zpasswd)
	#获取Storage Servers主机组id
	grouplist = zapi.do_request('hostgroup.get',{'filter':{'name':groupname}})
	groupids = []
	for groupinfo in  grouplist['result']:
		groupids.append(groupinfo['groupid'])
	print groupids
	#指定组id，屏蔽一些host，mysql之类的主机
	hostlist = zapi.do_request('host.get',{'groupids':groupids,
											'output':['hostid','host'],
											'status':1})
	hostlist = hostlist['result']
	hostdict = {}
#for host in hostlist:
#		hostdict[host['host']] = host['hostid']
#	print hostdict
	olddiskinfo = get_disk_history(zapi,hostlist,yestday)
	newdiskinfo = get_disk_history(zapi,hostlist,today)

	print olddiskinfo
	print newdiskinfo
	diskusage = {}
	for host in hostlist:
		print str(host['host'])
		ip = host['host']
		diskusage[ip] = []
		print olddiskinfo[ip]
		iteminfo = []
		for itemid in olddiskinfo[ip].keys():
			path = diskitems[itemid]
			free = int(newdiskinfo[ip][itemid])
			usage = int(olddiskinfo[ip][itemid]) - free
			filter = {'name':['Free inodes on $1 (percentage)'],
						'key_':'vfs.fs.inode[' + path+ ',pfree]'}
			ifree = get_item_history(zapi,host['hostid'],path,today,filter,type=0)
			filter = {'name':['Total disk space on $1'],
						'key_':'vfs.fs.size[' + path + ',total]'}
			disktotal = get_item_history(zapi,host['hostid'],path,today,filter,type=3)
			iteminfo.append({'path':path,'usage':usage,'free':free,'inode':ifree,'total':int(disktotal)})
		diskusage[ip] = iteminfo
	print diskusage
	"""
	diskusage数据类型{ip:['path':'/','usage':1234,'free':1111,'inode':99,
						  'path':'/data1','usage':1234,'free':1111,'inode':99],
					ip2:[]}
	"""
	yestday = datetime.today() - timedelta(days=1)
	htmlinfo = infoToHtml(diskusage)
	title = ['服务器地址','目录','总空间','剩余空间','日使用量','inodes百分比']
	filename = 'xls/disk_usage' + yestday.strftime('%Y-%m-%d') + '.xlsx'
	writeToExcel(title,diskusage,filename)
	sendMail(yestday.strftime('%Y-%m-%d') + "磁盘空间信息", htmlinfo, sendto, serverinfo,filename)
	return 0

if __name__ == '__main__':
	#diskitems和inodeitems用于存放item：path映射关系
	diskitems = {}
	#此处设置需要查询信息的组名
	groupname = ["Storage Servers"]
	#groupname = ["Linux servers"]
	zurl = "http://monitor.ciurl.cn"
	zuser = "Admin"
	zpasswd = "fuyuanzabbix"
	serverinfo = {'mail_host':'smtp.163.com',
		        'mail_user':'ci123webserver@163.com',
				'mail_pass':'ci123webserver12'}
	sendto = ['cjy@corp-ci.com']

	sys.exit(int(main(sys.argv)))
