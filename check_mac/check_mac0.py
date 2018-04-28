#coding: utf-8
import MySQLdb,os,multiprocessing
import time
def dbsql(getid,getip):
    timenow = int(time.time())
    db = MySQLdb.connect("192.168.0.238", "ipcheck", "fuyuan1906", "ip", charset='utf8' )
    cursor = db.cursor()
    sqlinsert = "INSERT INTO ipv4_0 (id,ip) VALUES ('%s','%s')" %(getid,getip)
    mac = os.popen("arping -I em1 -f -w 1 " + getip + "|grep Unicast|awk '{print $5}'|awk -F '[' '{print $2}'|awk -F ']' '{print $1}'")
    getmac = mac.read().strip()
    if getmac:
        sqlselect = "select mac from ipv4_0 where id =%s" %(getid)
        sqlupdate = "update ipv4_0 set mac='%s' where id=%s" %(getmac,getid)
        sqlupdatetime = "update ipv4_0 set date=%s where id=%s" %(timenow,getid)
        print 0 
        try:
            cursor.execute(sqlselect)
            results = cursor.fetchone()
        except:
            print "Error: unable to fecth data"
        if getmac != results[0]:
            print(sqlupdate)
            try:
                cursor.execute(sqlupdate)
                cursor.execute(sqlupdatetime)
                db.commit()
            except:
                db.rollback()
        else:
            print(sqlupdatetime)
            try:
                cursor.execute(sqlupdatetime)
                db.commit()
            except:
               db.rollback()
            print(0)
        db.close()
    else:
         print(0)
def check():
    p = multiprocessing.Pool(processes=254)
    for i in range(2,254):
        ip = "192.168.0." + str(i)
        p.apply_async(dbsql,args=(i,ip,))
    p.close()
    p.join()
if __name__ == '__main__':
    check()
