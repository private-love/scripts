#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import zipfile,os,datetime
import re,shutil
def ziplog(logzipname,logfile):
	logzip = zipfile.ZipFile(logzipname+'.gz', 'a')
	logzip.write(logfile)
	logzip.close()
def logback(logdir):
	newdir=[]
	os.chdir(logdir)
	print(os.getcwd())
	if not os.path.exists('./backup'):
		os.makedirs('./backup')
	for all in os.listdir('.'):
		if os.path.isdir('.'+'/'+all) and all != 'backup':
			newdir.append('.'+'/'+all)
		elif os.path.isdir('.'+'/'+all) and all == 'backup':
			continue
		else:
			if all.endswith(('tar.gz','gz')):
				print(all+' move to ./backup/')
				shutil.move(all,'./backup')
			else:
				if 'access' in all:
					date=re.match( r'(.*)access(.*)', all, re.M|re.I)			
					datenum=re.sub(r'\D', "",date.group(2))
					logtype=date.group(1)
					if datenum[-4:-2] == mouthnow:
						size=os.path.getsize(all)
						if size/1024/1024 > 200 and int(daynow)-7 > int(datenum[-2:]):
							zip='./backup/'+logtype+'access.'+datenum[:-2]
#							print(all+' gzip add to '+zip+'.gz')
							print("%-45s%-20s%s"%(all,' gzip add to ',zip+'.gz'))
							ziplog(zip,all)
							os.remove(all)
					else:
						zip='./backup/'+logtype+'access.'+datenum[:-2]
						print(all+' gzip add to '+zip+'.gz')
						ziplog(zip,all)
						os.remove(all)
	if newdir:	
		for i in newdir:
			logback(i)
			os.chdir('../')
if __name__ == '__main__':
	mouthnow=datetime.datetime.now().strftime('%m')
	yearnow=datetime.datetime.now().strftime('%Y')
	daynow=datetime.datetime.now().strftime('%d')
	logback('./logs')
