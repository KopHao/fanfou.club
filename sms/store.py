#!/usr/bin/python
# -*- coding: utf-8 -*-
import web
import time
import kvdb

consumer = {'key': '', 'secret': ''}


class Sign:
    def select(self, mobile):
        return kvdb.select('sms_sign', mobile)
        
    def select_by_token(self, token):
        res = kvdb.select_all('sms_sign')
        for key, val in res.items():
            if token == val: return key

    def insert(self, mobile, token):
        kvdb.insert('sms_sign', mobile, token)
    
    def delete(self, mobile):
        kvdb.delete('sms_sign', mobile)

    def fetchall(self):
        return kvdb.select_all('sms_sign')
        
    def cleanup(self):
        kvdb.drop_node('sms_sign')
sign = Sign()


class Sync:
    def select(self, mobile):
        return kvdb.select('sms_sync', mobile)
        
    def insert(self, mobile, mode='add'):
        kvdb.insert('sms_sync', mobile, {'mobile': mobile, 'mode': mode})
    
    def delete(self, mobile):
        kvdb.delete('sms_sync', mobile)
    
    def fetchall(self):
        res = kvdb.select_all('sms_sync').values()
        return [(item['mode'], item['mobile']) for item in res]
        
    def cleanup(self):
        kvdb.drop_node('sms_sync')
sync = Sync()


class Sent:
    def insert(self, statuses_id):
        kvdb.insert('sms_sent', statuses_id, None)

    def cleanup(self):
        kvdb.drop_node('sms_sent')
sent = Sent()


class Trace:
    def select(self, idx=0):
        res = kvdb.select_all('sms_trace')
        keys = sorted(res, reverse=True) 
        return res.get(keys[idx])
        
    def insert(self, referer, format_exc):
        kvdb.insert('sms_trace', time.time(), {'atime': time.time(), 'referer': referer, 'format_exc': format_exc})

    def fetchall(self):
        return kvdb.select_all('sms_trace').values()
    
    def cleanup(self):
        kvdb.drop_node('sms_trace')
trace = Trace()