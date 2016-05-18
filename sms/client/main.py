import os
import sys
import sl4a
import time
import sqlite3
import base62
from urllib import request

droid = sl4a.Android()
curdir = '/storage/emulated/0/com.hipipal.qpyplus/projects3/fanfou.sms/'
#curdir = os.path.dirname(os.path.abspath(__file__))
running = 0

class DB:
    def __init__(self):
        self.db =  os.path.join(curdir, 'fanfou.sms.db')
        if os.path.exists(self.db):
            self.cx = sqlite3.connect(self.db)
            self.cu = self.cx.cursor()
        else:
            self.cx = sqlite3.connect(self.db)
            self.cu = self.cx.cursor()
            self.cu.execute("CREATE TABLE sent (_id char(128))")
            self.cu.execute("CREATE TABLE sign (mobile char(128))")
            self.cu.execute("CREATE TABLE sync (mobile char(128))")
            self.cx.commit()

    def __del__(self):
        self.cx.close()

class Sent(DB):
    def __contains__(self, _id):
        data = self.cu.execute("SELECT _id FROM sent WHERE _id='%s'"%_id).fetchone()
        return bool(data) 
 
    def insert(self, _id):
        if _id not in self:
            self.cu.execute("INSERT INTO sent (_id) VALUES ('%s')"%_id)
            self.cx.commit()
sent = Sent()
    
class Sign(DB):
    def __contains__(self, mobile):
        data = self.cu.execute("SELECT mobile FROM sign WHERE mobile='%s'"%mobile).fetchone()
        return bool(data) 
 
    def insert(self, mobile):
        if mobile not in self:
            self.cu.execute("INSERT INTO sign (mobile) VALUES ('%s')"%mobile)
            self.cx.commit()
            
    def delete(self, mobile):
        self.cu.execute("DELETE FROM sign WHERE mobile='%s'"%mobile)
        self.cx.commit()
sign = Sign()
    
class Sync(DB):
    def __contains__(self, mobile):
        data = self.cu.execute("SELECT mobile FROM sync WHERE mobile='%s'"%mobile).fetchone()
        return bool(data) 
 
    def insert(self, mobile):
        if mobile not in self:
            self.cu.execute("INSERT INTO sync (mobile) VALUES ('%s')"%mobile)
            self.cx.commit()
            
    def fetchall(self):
        data = self.cu.execute("SELECT mobile FROM sync").fetchall()
        return [item[0] for item in data]
            
    def cleanup(self):
        self.cu.execute("DELETE FROM sync")
        self.cx.commit()
sync = Sync()

def __sync():
    body = sync.fetchall()
    sync.cleanup()
    body = str.encode(base62.dumps(body), 'utf8')
    resp = request.urlopen('http://fanfou.club/sms/__sync', data=body)
    data = base62.loads(bytes.decode(resp.read(), 'utf8'))
    for mode, mobile in data:
        if mode == 'add':
            sign.insert(mobile)
        else:
            sign.delete(mobile)
        sync.insert(mobile)

def upload():
    sms0 = droid.smsGetMessages(True, 'inbox').result
    sms1 = droid.smsGetMessages(False, 'inbox').result
    data = sorted(sms0+sms1, key=lambda d: d['_id'])
    for item in data:
        try:
            global running; running += 1
            mobile = item['address'][-11:]
            sms_id = item['_id']
            if sms_id not in sent and mobile in sign:
                body = {'mobile': mobile, 'text': item['body']}
                body = str.encode(base62.dumps(body), 'utf8')
                resp = request.urlopen('http://fanfou.club/sms/upload', data=body)
                if resp.read() in [b'200', b'201']:
                    sent.insert(sms_id)
                print('\n%s: the sms (%s) has sent.' % (running, sms_id))
            else:
                print('\r%s: there is nothing to do.' % running, end='')
                sys.stdout.flush()
        except (Exception) as ex:
            print("\nException: %s" % repr(ex))
                
if __name__ == '__main__':
    while True:
        try:
            __sync()
            upload()
        except (Exception) as ex:
            print("Exception: %s" % repr(ex))
        time.sleep(8)