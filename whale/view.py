#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import web
import time
import json
import random
import utils
import store
import traceback
from datetime import datetime
from tasks import add_task
    
urls = (
    '/?', 'index',
    '/work', 'work',
    '/check', 'check',
    '/greet', 'greet',
    '/send', 'send',
    '/learn', 'learn',
    '/talk', 'talk',
    '/hello', 'hello',
    '/push', 'push',
    '/cmd', 'cmd', 
    '/debug', 'debug'
)


def _Error():
    referer = web.ctx.env.get('HTTP_REFERER', web.ctx.home)
    store.trace.insert(referer, traceback.format_exc())
    return web.internalerror('internalerror')

class index:
    def GET(self):
        return 'hello, fanfou'

class work:                   
    def GET(self):
        last_call = store.ctx.last_call or 0
        if time.time() - last_call < 600: return
        
        if utils.stage() != store.ctx.stage:
            add_task(web.ctx, '/whale/hello', utils.stage())
        if utils.stage() != 'sleep':
            add_task(web.ctx, '/whale/greet', utils.stage())
        
class check:
    def GET(self):
        resp = utils.client.request1('/account/notification', 'GET', {'mode': 'lite'})
        data = json.loads(resp.read())
        if data['direct_messages']:
            add_task(web.ctx, '/whale/learn', 'to learn')
        if data['mentions']:
            add_task(web.ctx, '/whale/talk', str(data['mentions']))
            
class greet:
    def filter(self, data):
        for item in data:
            text = utils.htmlec(item['text'])
            user_id = item['user']['id']
            raw_id = utils.get_raw_id(item)
            msg_id = utils.get_msg_id(item)
            if utils.not_ori_post(item) or store.sent.select(msg_id):
                continue
            if utils.is_self(user_id) or store.cust_block.select(user_id):
                continue 
            greet_type = None
            whale_json = utils.get_whale_json()
            for key, val in whale_json['keywords'].items():
                for kw in val:
                    if kw in text:
                        greet_type = key
                        break
            if not greet_type:
                continue
                
            store.sent.insert(msg_id)
            reply_text = utils.get_reply_text(greet_type, user_id)
            user_name = item['user']['name']
            status = u'%s 转@%s %s' % (reply_text, user_name, text)
            yield {'status': status, 'repost_status_id': msg_id, 'mode': 'lite'}

    
    def POST(self):
        self.stage = web.data()
        store.ctx.last_call = time.time()
        try:
            resp = utils.request(utils.request_url, 'GET', {'count': 60, 'mode': 'lite'})
            data = json.loads(resp.read())
            for body in self.filter(data):
                add_task(web.ctx, '/whale/send', json.dumps(body))
        finally:
            if self.stage != utils.stage(): 
                add_task(web.ctx, '/whale/hello', self.stage)
            else:
                time.sleep(4)
                add_task(web.ctx, '/whale/greet', self.stage)

class send:
    def POST(self):
        body = json.loads(web.data())
        body['status'] = body.get('status').encode('utf-8')
        utils.client.request1('/statuses/update', 'POST', body)

class learn:
    def POST(self):
        resp = utils.client.request1('/direct_messages/inbox', 'GET', {'count': 60, 'mode': 'lite'})
        for item in json.loads(resp.read()):
            text = utils.htmlec(item['text'])
            idx1, idx2 = [text.find(i) for i in ('Q:', 'A:')]
            if -1 in [idx1, idx2]: 
                continue
            else:
                user_id = item['sender']['id'].encode('utf-8')
                resp = utils.client.request2('/users/show/:id', 'GET', {'id': user_id})
                data = json.loads(resp.read())
                if utils.fanli(data) > 10:
                    ask = text[idx1+2:idx2].strip()
                    ans = text[idx2+2:].strip()
                    store.talk.insert(ask, ans)
                utils.client.request1('/direct_messages/destroy', 'POST', {'id': item['id']})
                body = {
                    'user': user_id,
                    'text': '我学会啦（%s）' % text.encode('utf-8'),
                    'mode': 'lite'
                }
                utils.client.request1('/direct_messages/new', 'POST', body)

        
class talk:
    def filter(self, data):
        for item in data:
            text = utils.htmlec(item['text']).strip()
            user_id = item['user']['id']
            msg_id = item['id']
            if store.sent.select(msg_id) or item['is_self'] or item.get('repost_status_id'):
                continue
            if utils.is_cmd(text):
                add_task(web.ctx, '/whale/cmd', json.dumps(item))
                store.sent.insert(msg_id)
            else:
                talk_ans = None
                for ask, ans in store.talk.fetchall().items():
                    if ask in text:
                        talk_ans = random.choice(ans)
                if talk_ans:
                    store.sent.insert(msg_id)
                    msg = u'@%s %s' % (item['user']['name'], talk_ans)
                    yield {'status': msg, 'in_reply_to_status_id': msg_id, 'mode': 'lite'}
                    
    def POST(self):
        amount = int(web.data())
        count = 60 if amount > 20 else 20
        pages = amount / count + 2
        for page in range(1, pages):
            body = {'count': count, 'page': page, 'mode': 'lite'}
            resp = utils.client.request1('/statuses/mentions', 'GET', body)
            data = json.loads(resp.read())
            for body in self.filter(data):
                add_task(web.ctx, '/whale/send', json.dumps(body))

class hello:
    def POST(self):
        msg = None
        stage = web.data()
        now = datetime.now()
        whale_json = utils.get_whale_json()
        if now.hour in [6, 22]:
            msg = whale_json.get('welcome').get(stage)
        elif now.hour in [9, 1]:
            msg = whale_json.get('goodbey').get(stage)
        if msg:
            body = {'status': msg.encode('utf-8'), 'mode': 'lite'}
            utils.client.request1('/statuses/update', 'POST', body)
            store.ctx.stage = stage

class cmd:
    def POST(self):
        data = json.loads(web.data())
        text = data['text'].encode('utf-8')[12:].strip()
        user_id = data['user']['id']
        user_name = data['user']['name']
        raw_id = utils.get_raw_id(data)
        flag = None
        if text.startswith('--dislike-'):
            lang = text[10:].strip()
            if lang in ['en', 'jp', 'zh']:
                store.cust_lang.insert(user_id, 'dislike', lang)
                store.custom.insert(user_id)
                flag = 'done'
        elif text.startswith('--like-'):
            lang = text[7:].strip()
            if lang in ['en', 'jp', 'zh']:
                store.cust_lang.insert(user_id, 'like', lang)
                store.custom.insert(user_id)
                flag = 'done'
        elif text.startswith('--def-'):
            mode, val = re.search(r'--def-([^ ]*)(.*)', text).groups()
            if mode in [u'morn', u'night', u'nick']:
                getattr(store, 'cust_%s' % mode).insert(user_id, val.strip())
                store.custom.insert(user_id)
                flag = 'done'
        elif text.startswith('--block'):
            if store.cust_block.select(user_id):
                store.cust_block.delete(user_id)
            else:
                store.cust_block.insert(user_id)
            store.custom.insert(user_id)
            flag = 'done'
        elif text.startswith('--del'):
            if raw_id:
                resp = utils.client.request1('/statuses/show', 'GET', {'id': raw_id, 'mode': 'lite'}) 
                data = json.loads(resp.read())
                ori_po_user = data.get('repost_user_id', '') or data.get('in_reply_to_user_id', '')
                if user_id in (ori_po_user, u'home2'):
                    utils.client.request1('/statuses/destroy', 'POST', {'id': raw_id, 'mode': 'lite'})
                    flag = 'done'
        elif text.startswith('--reset'):
            store.custom.delete(user_id)
            flag = 'done'
            
        if flag:
            msg = u'@%s 我记住啦 %s'%(user_name, utils.emoji())
            body = {'status': msg.encode('utf-8'), 'mode': 'lite', 'in_reply_to_status_id': data['id']}
            utils.client.request1('/statuses/update', 'POST', body)
            
 
class debug:
    def GET(self):
        return 'debug'

        
class push:
    def POST(self):
        msg = u'接受注册邀请，为小鲸鱼续一秒 ～ http://t.cn/RqAY1W9（规则 http://t.cn/RbgUyQ2）'
        body = {'status': msg.encode('utf-8'), 'mode': 'lite'}
        utils.client.request1('/statuses/update', 'POST', body)


web.config.debug = True
web.config.debug_sql = False
app = web.application(urls, locals())

#app.internalerror = _Error
curdir = os.path.dirname(os.path.abspath(__file__))
render = web.template.render(os.path.join(curdir, 'templates'), globals=globals())

if __name__ == '__main__':
    app.run()