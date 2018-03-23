#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import datetime
import time
import re
import xlwt
import xlrd
import smtplib
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import mimetypes
import email.MIMEImage
reload(sys)
sys.setdefaultencoding('utf-8')
def podcheck ():
	time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S 第%W周 %A/%w')
	#os.system("kubectl get pods --all-namespaces -o wide|grep -v 'STATUS' > podstatus.txt")
	logfile = open("pod.log","a+")	
	podfile = open("podstatus.txt","r")
	podname = [];podnames = [];podnameok = [];podnamebad = [];podnamenew = []
	podnamespaces = [];podnamespacess = [];podnamespacesok = [];podnamespacesbad = [];podnamespacesnew = []
	podstatus = [];podstatuss = [];podstatusok = [];podstatusbad = [];podstatusnew = []
	podip = [];podips = [];podipok = [];podipbad = [];podipnew = []
	podnode = [];podnodes = [];podnodeok = [];podnodebad = [];podnodenew = []
	status1 = ['NAMESPACE','NAME','STATUS','IP','NODE']
	a = 'Running'
	ok = time_now + '      All pod are' + a
	bad = time_now + '      Some of the pod error'
	for pod in podfile:
	   line = pod.strip()
	   if a in line:
			continue
	   else:
			b = re.split(r" +",line)
			podname.append(b[1]);podnamespaces.append(b[0]);podstatus.append(b[3]);podip.append(b[6]);podnode.append(b[7])
	if podname:
		podfile.close()
		logfile.write(bad+'\n')
		podnamelen = len(podname) - 1
		time.sleep(60)
		#os.system("kubectl get pods --all-namespaces -o wide|grep -v 'STATUS' > podstatus.txt")
		podfiles = open("podstatus.txt","r")
		time_nows = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S 第%W周 %A/%w')
		oks = time_nows + '      error pod have recovered Running'
		bads = time_nows + '      Some of the pod still error'
		for pod in podfiles:
			line = pod.strip()
			if a in line:
				continue
			else:
				b = re.split(r" +",line)
				podnames.append(b[1]);podnamespacess.append(b[0]);podstatuss.append(b[3]);podips.append(b[6]);podnodes.append(b[7])
		if podname:
			logfile.write(bads+'\n')
		else:
			logfile.write(oks+'\n')
		podfiles.close()
		l = len(podname)
		ls = len(podnames)
		for i in range(0,l):
			if podname[i] in podnames:
				podnamebad.append(podname[i]);podnamespacesbad.append(podnamespaces[i]);podstatusbad.append(podstatus[i]);podipbad.append(podip[i]);podnodebad.append(podnode[i])
			else:
				podnameok.append(podname[i]);podnamespacesok.append(podnamespaces[i]);podstatusok.append(podstatus[i]);podipok.append(podip[i]);podnodeok.append(podnode[i])
		for i in range(0,ls):
			if podnames[i] in podname:
				continue
			else:
				podnamenew.append(podnames[i]);podnamespacesnew.append(podnamespacess[i]);podstatusnew.append(podstatuss[i]);podipnew.append(podips[i]);podnodenew.append(podnodes[i])
	else:
		logfile.write(ok+'\n')
	podfile.close()
	logfile.close()
	if podnamebad or podnamenew or podnameok:
		#print podnamebad
		xls=xlwt.Workbook(encoding='utf-8')
		sheet = xls.add_sheet('podstatus_check',cell_overwrite_ok=True)
		x = 1;y = 0
		borders = xlwt.Borders();borders.left = xlwt.Borders.THIN;borders.right = xlwt.Borders.THIN;borders.top = xlwt.Borders.THIN;borders.bottom = xlwt.Borders.THIN
		alignment = xlwt.Alignment();alignment.horz = xlwt.Alignment.HORZ_CENTER;alignment.vert = xlwt.Alignment.VERT_CENTER
		pattern = xlwt.Pattern();pattern.pattern = xlwt.Pattern.SOLID_PATTERN;pattern.pattern_fore_colour = 5
		style1 = xlwt.XFStyle();style = xlwt.XFStyle();style2 = xlwt.XFStyle()
		style1.borders = borders;style1.alignment = alignment;style1.pattern = pattern
		style.borders = borders
		style2.borders = borders;style2.alignment = alignment
		if podnameok:
			sheet.write_merge(0,0,0,4,'在检查期间恢复的Running的pod信息',style1)
			sheet.write(x,0,status1[0],style2);sheet.write(x,1,status1[1],style2);sheet.write(x,2,status1[2],style2);sheet.write(x,3,status1[3],style2);sheet.write(x,4,status1[4],style2)
			x += 1
			for i in range (0,len(podnameok)):
				sheet.write(x,0,podnamespacesok[i],style);sheet.write(x,1,podnameok[i],style);sheet.write(x,2,podstatusok[i],style2);sheet.write(x,3,podipok[i],style2);sheet.write(x,4,podnodeok[i],style2)
				x += 1
		else:
			sheet.write_merge(0,0,0,4,'在检查期间没有pod恢复Running',style1)
		if podnamebad:
			sheet.write_merge(x,x,0,4,'仍然error的pod信息',style1)
			x += 1
			sheet.write(x,0,status1[0],style2);sheet.write(x,1,status1[1],style2);sheet.write(x,2,status1[2],style2);sheet.write(x,3,status1[3],style2);sheet.write(x,4,status1[4],style2)
			x += 1
			for i in range (0,len(podnamebad)):
				sheet.write(x,0,podnamespacesbad[i],style);sheet.write(x,1,podnamebad[i],style);sheet.write(x,2,podstatusbad[i],style2);sheet.write(x,3,podipbad[i],style2);sheet.write(x,4,podnodebad[i],style2)
				x += 1
		else:
			sheet.write_merge(x,x,0,4,'之前error的pod已经恢复Running',style1)	
			x += 1
		if podnamenew:
			sheet.write_merge(x,x,0,4,'检查期间出现新的error pod',style1)
			x += 1
			sheet.write(x,0,status1[0],style2);sheet.write(x,1,status1[1],style2);sheet.write(x,2,status1[2],style2);sheet.write(x,3,status1[3],style2);sheet.write(x,4,status1[4],style2)
			x += 1
			for i in range (0,len(podnamenew)):
				sheet.write(x,0,podnamespacesnew[i],style);sheet.write(x,1,podnamenew[i],style);sheet.write(x,2,podstatusnew[i],style2);sheet.write(x,3,podipnew[i],style2);sheet.write(x,4,podnodenew[i],style2)
				x += 1
		else:
			sheet.write_merge(x,x,0,4,'检查期间没有出现新的error pod',style1)
			x += 1
		sheet.col(3).width = 14 *256;sheet.col(2).width = 14 * 256;sheet.col(4).width = 14 *256
		d = 20
		for c in podname:
			for s in podnames:
				if len(s) > d:
					d = len(s)
			if len(c) > d:
				d = len(c)
		sheet.col(1).width = d * 256
		d = 14
		for c in podnamespaces:
			for s in podnamespacess:
				if len(s) > d:
					d = len(s)
			if len(c) > d:
				d = len(c)
		sheet.col(0).width = d * 256

		xls.save('pod.xls')
		#print len(podip[0])
		
################################
podcheck ()
