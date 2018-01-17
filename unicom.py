#! /usr/bin/env python
# coding:utf-8

import cookielib
import json
import sys
import urllib
import urllib2
import execjs,os
import logging
import time

reload(sys)
sys.setdefaultencoding('utf8')

class UnicomSign:

    login_header = {
        'User-Agent': 'Mozilla/5.0 (Linux; HFWSH_USER Android 7.0; SM-G9350 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.111 Mobile Safari/537.36'}
    signin_header = {
        'User-Agent': 'Mozilla/5.0 (Linux; HFWSH_USER Android 7.0; SM-G9350 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.111 Mobile Safari/537.36',
        'X-Requested-With': 'com.ailk.main.flowassistant', 
		'Content-Length': 0, 
		'Origin': 'https://ll.fj10010.com/',
        'Referer': 'https://ll.fj10010.com/faWapNew/login/login.html?url=https://ll.fj10010.com/faWap/myFlow!index.action'}
    phone = ''
    pwd = ''
    phone_encode = ''
    pwd_encode = ''
    cookie = None
    cookieFile = './cookie.dat'
    ctx = None
    enctyptedParam = ''

    def loadJs(self,path):
        if not os.path.exists(path):
            logging.info(time.ctime() + "file no exist %s %r" + path)
            return
        f = open(path, 'r')
        line = f.readline()
        jsstr = ''
        while line:
            jsstr = jsstr + line
            line = f.readline()
        self.ctx = execjs.compile(jsstr.decode('utf8'))

    def rsaEnctytedString(self,param):
        postdata = {}
        postdata = urllib.urlencode(postdata)
        req = urllib2.Request(url='https://ll.fj10010.com/login!keyPair.action', data=postdata, headers=self.login_header)
        data = urllib2.urlopen(req).read()
        data = json.loads(data)
        exponent = data["modulus"]["exponent"];
        modulus = data["modulus"]["modulus"];
        if param.strip() :
            #publicKey = self.ctx.call('RSAUtils.getKeyPair',exponent, '', modulus) #RSAUtils.getKeyPair(exponent, '', modulus);
            return self.ctx.call('rsaEnctytedString',exponent, modulus, param)
        else:
            return param

    def __init__(self, username, pwd, logType):
        self.phone = username
        self.pwd = pwd
        self.logType = logType
        self.cookie = cookielib.LWPCookieJar()
        #self.cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        urllib2.install_opener(opener)
        paths = os.path.dirname(__file__)
        #print paths
        dir = paths + "./js/security.js"
        self.loadJs(dir)
        self.phone_encode = self.rsaEnctytedString(self.phone)
        self.pwd_encode = self.rsaEnctytedString(self.pwd)

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename="auto_sign.log",
                            filemode='a')

    def login(self):
        print 'login...'
        #self.password = "08714487761be3e8588d1b1a8faa6f2f6ab0bf39d26b7c8f8095f6de326282a7bce9479f266801c869fe688e7483311e672a7b7fe28fbe2b03c5c3260dece1114b7c5920ba857ece905e86369cb1c2da454916e1924e4026f31b2fc6ec70c39a8f076b7bcae820e94f9f7d302449795d726bd955fc45eeab359e6074b23693eb"
        postdata = {'loginName': self.phone_encode, 'code': self.pwd_encode, 'logType': '3'}
        postdata = urllib.urlencode(postdata)
        req = urllib2.Request(url='https://ll.fj10010.com/faWap/faLogin!login.action', data=postdata, headers=self.login_header)
        result = urllib2.urlopen(req).read()
        #result = json.loads(result)
        self.cookie.save(self.cookieFile)
        result = str(result).decode('utf-8')#.encode('gbk')

        if result.find(u'签到有礼') != -1:
            logging.info(time.ctime() + "登入成功")
            print 'Login successfully!'
        else:
            logging.info(time.ctime() + "登入失败")
            print 'Login failed due to Email or Password error...'
            sys.exit()

    def signIn(self):
        postdata = {}
        postdata = urllib.urlencode(postdata)
        print 'signing...'
        req = urllib2.Request(url='https://ll.fj10010.com/app/sign!sign.action', data=postdata, headers=self.signin_header)
        result = urllib2.urlopen(req).read()
        data = json.loads(result)
        if data['code'] == '0000':
            print self.phone,'have signed', 'signDay',data['signDay'],  'todayNum:',data['todayNum'],'signList',data['signList']
            logging.info(time.ctime() +' phoneNo:'+ self.phone + '  have signed signDay:' + data['signDay'] + '  todayNum:' + data['todayNum'] + '  signList:' + data['signList'])
        else:
            print 'signing failed code:', data['code'],'错误消息:',data['msg']
            logging.info(time.ctime() + ' signing failed code:'+ data['code'] + '错误消息:' + data['msg'])

if __name__ == '__main__':
    user = UnicomSign('你的联通号码', '密码',3)
    user.login()
    user.signIn()
    logging.info(time.ctime() + '---------------------------执行完毕---------------------------')
    logging.shutdown()