#!/usr/bin/python
# -*- coding: utf-8 -*-
import web
import time
import kvdb
import random

class Ctx:
    def __getattr__(self, key):
        return kvdb.select('whale_ctx', key)
        
    def __setattr__(self, key, val): 
        kvdb.insert('whale_ctx', key, val)
ctx = Ctx()


class Sent:
    def insert(self, msg_id):
        kvdb.insert('whale_sent', msg_id, time.time())
        
    def select(self, msg_id):
        return kvdb.select('whale_sent', msg_id)

    def delete(self, msg_id):
        kvdb.delete('whale_sent', msg_id)

    def cutted(self):
        tmp = kvdb.select_all('whale_sent')
        for key, val in tmp.items():
            if time.time() - val > 86400:
                self.delete(key)
                
    def fetchall(self):
        return kvdb.select_all('whale_sent')
sent = Sent()


class Custom:
    def insert(self, user_id):
        kvdb.insert('whale_custom', user_id, time.time())
        
    def select(self, user_id):
        return kvdb.select('whale_custom', user_id)
        
    def delete(self, user_id):
        kvdb.delete('whale_custom', user_id)
        
    def fetchall(self):
        return kvdb.select_all('whale_custom')
custom = Custom()

    
class Cust_nick:
    def insert(self, user_id, nick_name):
        kvdb.insert('whale_nick', user_id, nick_name)
        
    def select(self, user_id):
        return kvdb.select('whale_nick', user_id)
        
    def delete(self, user_id):
        kvdb.delete('whale_nick', user_id)
        
    def fetchall(self):
        return kvdb.select_all('whale_nick')
cust_nick = Cust_nick()


class Cust_morn:
    def insert(self, user_id, resp):
        kvdb.insert('whale_morn', user_id, resp)
        
    def select(self, user_id):
        return kvdb.select('whale_morn', user_id)
        
    def delete(self, user_id):
        kvdb.delete('whale_morn', user_id)
        
    def fetchall(self):
        return kvdb.select_all('whale_morn')
cust_morn = Cust_morn()


class Cust_night:
    def insert(self, user_id, resp):
        kvdb.insert('whale_night', user_id, resp)
        
    def select(self, user_id):
        return kvdb.select('whale_night', user_id)
        
    def delete(select, user_id):
        kvdb.delete('whale_night', user_id)
        
    def fetchall(self):
        return kvdb.select_all('whale_night')
cust_night = Cust_night()


class Cust_lang:
    # mode is like or dislike
    def insert(self, user_id, mode, lang):
        kvdb.insert('whale_lang', user_id, (mode, lang))
        
    def select(self, user_id):
        return kvdb.select('whale_lang', user_id)
        
    def delete(self, user_id):
        kvdb.delete('whale_lang', user_id)
        
    def fetchall(self):
        return kvdb.select_all('whale_lang')
cust_lang = Cust_lang()


class Cust_block:
    def insert(self, user_id):
        kvdb.insert('whale_block', user_id, time.time())
        
    def select(self, user_id):
        return kvdb.select('whale_block', user_id)
        
    def delete(self, user_id):
        kvdb.delete('whale_block')

    def fetchall(self):
        return kvdb.select_all('whale_block')
cust_block = Cust_block()   


class Talk:
    def insert(self, ask, ans):
        res = self.select(ask) or []
        res.append(ans)
        kvdb.insert('whale_talk', ask, res)
        
    def select(self, ask):
        return kvdb.select('whale_talk', ask)
        
    def fetchall(self):
        return kvdb.select_all('whale_talk')
talk = Talk()


class Trace:
    def select(self, idx=0):
        res = kvdb.select_all('whale_trace')
        keys = sorted(res, reverse=True) 
        return res.get(keys[idx])
        
    def insert(self, referer, format_exc):
        kvdb.insert('whale_trace', time.time(), {'atime': time.time(), 'referer': referer, 'format_exc': format_exc})

    def fetchall(self):
        return kvdb.select_all('whale_trace').values()
    
    def cleanup(self):
        kvdb.drop_node('whale_trace')
trace = Trace()