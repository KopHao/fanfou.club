#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import web
import time
import random
import math
import json
import urllib2
import kvdb
import store
import fanfou
import datetime


class UTC(datetime.tzinfo):
    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self._offset)

    def tzname(self, dt):
        return 'UTC %+d:00' % self._offset

    def dst(self, dt):
        return datetime.timedelta(hours=self._offset)    

def stage():
    now = datetime.datetime.now(UTC(8))
    if now.hour in [6, 7, 8]:
        st = 'morn'
    elif now.hour in [22, 23, 0]:
        st = 'night'
    else:
        st = 'sleep'
    return st


class Client:
    def __init__(self):
        self.client1 = fanfou.OAuth(
            {'key': '', 'secret': ''},
            {'key': '', 'secret': ''}
        )
        self.client2 = fanfou.OAuth(
            {'key': '', 'secret': ''},
            {'key': '', 'secret': ''}
        )

    def request1(self, url, method='GET', body={}, headers={}):
        return self.client1.request(url, method, body, headers)

    def request2(self, url, method='GET', body={}, headers={}):
        return self.client2.request(url, method, body, headers)
client = Client()

request = client.request1 if random.random() > 0.50 else client.request2

request_url = '/statuses/home_timeline' if random.random() > 0.50 else '/statuses/public_timeline'


def created_days(s):
    created_at = datetime.datetime.strptime(s, '%a %b %d %H:%M:%S +0000 %Y')
    return (datetime.datetime.utcnow() - created_at).days
     
def fanli(item):
    # fanli, http://spacekid.me/spacefanfou/
    a = item['followers_count']
    b = created_days(item['created_at'])
    y = item['statuses_count'] / float(b)
    K = 0.75 if item['protected'] else 1.0
    A = K if y>20 else ((-y*y+40*y)/400.0)*K
    I = A*((a+b)/100.0)+10*math.sqrt(a)/math.log(b+100.0, math.e)
    return round(I)
   
def htmlec(s):
    el = {'&lt;': '<', '&gt;': '>', '&quot;': '"', '&amp;': '&'}
    for k, v in el.items():
        s = s.replace(k, v)
    return s

def get_raw_id(item):
    return item.get('repost_status_id', '') or item.get('in_reply_to_status_id', '')

def get_msg_id(item):
    return get_raw_id(item) or item.get('id')

def not_ori_post(item):
    return get_raw_id(item)
    
def is_cmd(text):
    cmds = ['--like-', '--dislike-', '--block', '--del', '--def-', '--reset']
    text = text[12:].strip()
    tmp = [1 if text.startswith(cmd) else 0  for cmd in cmds]
    return bool(sum(tmp))

def is_self(user_id):
    return user_id == 'TestByTse'
    
def emoji():
    emojis = [':)', ':-)', ';-)']
    res = kvdb.select('whale_ctx', 'emoji')
    emojis.remove(res) if res in emojis else ''
    res = random.choice(emojis)
    kvdb.insert('whale_ctx', 'emoji', res)
    return res
    

def get_whale_json():
    abspath = os.path.dirname(os.path.abspath(__file__))
    return json.loads(open(os.path.join(abspath, 'whale.json')).read())
    

def get_random_reply(reply_list):
    all_reply = []
    for node in reply_list.values():
        all_reply.extend(node)
    return random.choice(all_reply)

def get_reply_text(greet_type, user_id):
    reply_list = get_whale_json().get(greet_type)
    reply_text = None
    if not store.custom.select(user_id):
        reply_text = get_random_reply(reply_list)
    else:
        cust_nick = store.cust_nick.select(user_id)
        cust_lang = store.cust_lang.select(user_id)
        cust_morn = store.cust_morn.select(user_id)
        cust_night = store.cust_night.select(user_id)
        if greet_type == 'morn' and cust_morn:
            reply_text = cust_morn
            cust_nick = None
        elif greet_type == 'night' and cust_night:
            reply_list = cust_night
            cust_nick = None
        elif cust_lang:
            for key in reply_list.keys():
                if cust_lang[0] == 'dislike' and key == cust_lang[1]:
                    del reply_list[key]
                elif cust_lang[0] == 'like' and key == cust_lang[1]:
                    reply_list = {key: reply_list[key]}
            
        if not reply_text:
            reply_text = get_random_reply(reply_list)
        if cust_nick:
            reply_text = cust_nick + '，' + reply_text
    return reply_text
