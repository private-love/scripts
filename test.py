#!/usr/bin/python
# -*- coding: UTF-8 -*-
i = int(raw_input('净利润:'))
arr = [1000000,600000,400000,200000,100000,0]
rat = [0.01,0.015,0.03,0.05,0.075,0.1]
txt = ['100万以上部分奖金为','60-100万部分奖金为','40-60万部分奖金为','20-40万部分奖金为','10-20万部分奖金为','0-10万部分奖金为']
r = 0
for idx in range(0,6):
    if i>arr[idx]:
        r+=(i-arr[idx])*rat[idx]
        print txt[idx],(i-arr[idx])*rat[idx]
#        print (i-arr[idx])*rat[idx]
        i=arr[idx]
print '总奖金为:',r
    smtpserver = 'smtp.163.com'
    user = '15150595954@163.com'
    password = "xinlu120394"
    sender = user
    receiver = "wangluxin@corp-ci.com"
    subject = 'k8s pod check'
    att = MIMEApplication(open(newReport, 'rb').read())
    att.add_header('Content-Disposition', 'attachment', filename=newReport[1])
    f = open(newReport, 'rb')
    mail_body = f.read()
    f.close()
    msg = MIMEText(mail_body, 'html', 'utf-8')
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot.attach(msg)
    msgRoot.attach(att)
    smtp = smtplib.SMTP_SSL()
    smtp.connect(smtpserver)
    smtp.login(user, password)
    smtp.sendmail(sender, receiver, msgRoot.as_string())
    smtp.quit()
