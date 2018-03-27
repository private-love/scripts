import datetime
import time
a=time.localtime()
b=time.strftime("%A",a)
c=time.strftime("%w",a)
print a
print b
print c
d=datetime.datetime.now().weekday()
#e=d.weekday()
print d
#print time.strftime("%Y-%m-%d %A %X %Z", time.localtime())
#anyday=datetime.datetime(2014,07,27).strftime("%w")
#print anyday 
