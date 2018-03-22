#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import datetime
import time
import re
def podcheck ():
	time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S 第%W周 %A/%w')
	#podstatus = os.system("kubectl get pods --all-namespaces -o wide|grep -v 'STATUS' > podstatus.txt")
	logfile = open("check.log","a+")	
	podfile = open("podstatus.txt","r")
	podname = []
	podnamespaces = []
	podstatus = []
	podip = []
	podnode = []
	a = 'Running'
	ok = time + '      All pod is' + a
	bad = time + '      Some of the pod are not in the Running'
	for pod in podfile:
		line = pod.strip()
		if a in line:
			continue
		else:
			b = re.split(r" +",line)
			podname.append(b[1])
			podnamespaces.append(b[0])
			podstatus.append(b[3])
			podip.append(b[6])
			podnode.append(b[7])
			time.sleep(10)
			
	if podname:
		logfile.write(bad+'\n')
		print podname
		print podnamespaces
		print podstatus
		print podip
		print podnode
	else:
		logfile.write(ok+'\n')
	podfile.close()
	logfile.close()
################################
podcheck ()
