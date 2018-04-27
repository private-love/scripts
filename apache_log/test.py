#!/usr/bin/env python
#coding=UTF-8
import urllib2
import re
import os

def gethtml(url):
    page=urllib2.urlopen(url)
    html=page.read()
    print html
    with open('test.html','wt') as f:
	f.write(html)
    return html
    #print html

def getimg(html):
    reg=r'(公司简介)'
    imgre=re.compile(reg)
    imglist=imgre.findall(html)
    print imglist
    return imglist

html=gethtml("http://f10.eastmoney.com/f10_v2/CompanySurvey.aspx?code=sh600231")
a=getimg(html)
print a[0].decode('utf-8')
