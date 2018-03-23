#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import datetime
import time
import re
def podcheck ():
	time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S 第%W周 %A/%w')
	#os.system("kubectl get pods --all-namespaces -o wide|grep -v 'STATUS' > podstatus.txt")
	logfile = open("pod.log","a+")	
	podfile = open("podstatus.txt","r")
	podname = []
	podnamespaces = []
	podstatus = []
	podip = []
	podnode = []
	a = 'Running'
	ok = time_now + '      All pod are' + a
	oks = time_now + '      error pod have recovered Running'
	bad = time_now + '      Some of the pod are not in the Running'
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
	if podname:
		print podname
		podfile.close()
		logfile.write(bad+'\n')
		podnamelen = len(podname) - 1
		time.sleep(5)
		#os.system("kubectl get pods --all-namespaces -o wide|grep -v 'STATUS' > podstatus.txt")
		podfiles = open("podstatus.txt","r")
		podnames = []
		podnamespacess = []
		podstatuss = []
		podips = []
		podnodes = []
		for pod in podfiles:
			line = pod.strip()
			if a in line:
				continue
			else:
				b = re.split(r" +",line)
				podnames.append(b[1])
				podnamespacess.append(b[0])
				podstatuss.append(b[3])
				podips.append(b[6])
				podnodes.append(b[7])
		if podname:
			print podnames
			logfile.write(bad+'\n')
		else:
			logfile.write(oks+'\n')
		podfiles.close()
	else:
		logfile.write(ok+'\n')
	podfile.close()
	logfile.close()
################################
podcheck ()
