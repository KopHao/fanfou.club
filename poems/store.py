#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import web
import time
import random
import base64
import redis
import kvdb

def emoji():
    emojis = [':)', ':-)', ';-)']
    res = kvdb.select('poems_ctx', 'emoji')
    emojis.remove(res) if res in emojis else ''
    res = random.choice(emojis)
    kvdb.insert('poems_ctx', 'emoji', res)
    return res


class User:
    def insert(self, user_id, user_name):
        kvdb.insert('poems_user', user_id, user_name) 
                
    def delete(self, user_id):
        kvdb.delete('poems_user', user_id)
        
    def select(self, user_id):
        return kvdb.select('poems_user', user_id)
        
    def update(self, user_id, user_name):
        kvdb.update('poems_user', user_id, user_name) 
        
    def fetchall(self):
        return kvdb.select_all('poems_user')
user = User()


class Sent:
    def select(self, msg_id):
        return kvdb.select('poems_sent', msg_id)
        
    def insert(self, msg_id):
        kvdb.insert('poems_sent', msg_id, msg_id)
        
    def drop(self):
        kvdb.drop_node('poems_sent')
sent = Sent()    

    
class Poems:
    def __init__(self):
        self.poems = kvdb.select('poems_ctx', 'poems')
        if not self.poems:
            filepath = os.path.dirname(os.path.abspath(__file__))
            self.poems = open(os.path.join(filepath,'poems.txt')).readlines()
            kvdb.insert('poems_ctx', 'poems', self.poems)
    
    def one(self):
        return random.choice(self.poems)
poems = Poems()