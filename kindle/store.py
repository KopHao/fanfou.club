#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import web
import time
import uuid
import kvdb
import base64
import cPickle as pickle


consumer = {'key': '', 'secret': ''}
public_token = {'key': '', 'secret': ''}


class Sign:
    def select(self, address):
        return kvdb.select('kindle_sign', address)
        
    def select_by_token(self, token):
        res = kvdb.select_all('kindle_sign')
        for key, val in res.items():
            if token == val: return key

    def insert(self, address, token):
        kvdb.insert('kindle_sign', address, token)
    
    def delete(self, address):
        kvdb.delete('kindle_sign', address)

    def fetchall(self):
        return kvdb.select_all('kindle_sign')
        
    def cleanup(self):
        kvdb.drop_node('kindle_sign')
sign = Sign()


class Sync:        
    def insert(self, val):
        kvdb.insert('kindle_sync', str(uuid.uuid1()), val)

    def fetchall(self):
        return kvdb.select_all('kindle_sync').values()
        
    def cleanup(self):
        kvdb.drop_node('kindle_sync')
sync = Sync()


class Sent:
    def select(self, mail_id):
        return kvdb.select('kindle_sent', mail_id)
        
    def insert(self, mail_id, statuses_id):
        kvdb.insert('kindle_sent', mail_id, statuses_id)

    def fetchall(self):
        return kvdb.select_all('kindle_sent')

    def cleanup(self):
        kvdb.drop_node('kindle_sent')
sent = Sent()


class Trace:
    def select(self, idx=0):
        res = kvdb.select_all('kindle_trace')
        keys = sorted(res, reverse=True) 
        return res.get(keys[idx])
        
    def insert(self, referer, format_exc):
        kvdb.insert('kindle_trace', time.time(), {'atime': time.time(), 'referer': referer, 'format_exc': format_exc})

    def fetchall(self):
        return kvdb.select_all('kindle_trace').values()
    
    def cleanup(self):
        kvdb.drop_node('kindle_trace')
trace = Trace()