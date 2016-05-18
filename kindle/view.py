#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import web
import json
import time
import mail
import store
import fanfou
import urllib2
import datetime
import traceback
from tasks import add_task

def _Error():
    referer = web.ctx.env.get('HTTP_REFERER', web.ctx.home)
    store.trace.insert(referer, traceback.format_exc())
    return web.internalerror('internalerror')
        
def now():
    now = datetime.datetime.now()
    return now.strftime('%y/%m/%d %H:%M')
        
def get_email():
    return store.sign.select_by_token(web.ctx.session.kindle_token)

    
def notice():
    tmp = web.ctx.session.notice
    web.ctx.session.notice = ''
    return tmp
    
urls = (
    '/?', 'index',
    '/work', 'work',
    '/help', 'help',
    '/suicide', 'suicide',
    '/upload', 'upload',
    '/callback', 'callback',
    '/authorize', 'authorize',
    '/debug', 'debug',
)

class index:
    def GET(self):
        return render.index()
        
    def POST(self):
        raw_address = get_email()
        new_address = web.input().get('email').strip()
        if re.match(r'.+@.+', new_address):
            if raw_address:
                store.sign.delete(raw_address)
                store.sync.insert({'mode': 'sign-del', 'val': (raw_address,)})
            store.sign.insert(new_address, web.ctx.session.kindle_token)
            store.sync.insert({'mode': 'sign-add', 'val': (new_address, web.ctx.session.kindle_token)})
            web.ctx.session.notice = '邮件地址绑定成功，欢迎试用'
        else:
            web.ctx.session.notice = '请输入正确的邮件地址'
        raise web.seeother('/')
        
class help:
    def GET(self):
        return render.help()

class suicide:
    def GET(self):
        return render.suicide()
    
    def POST(self):
        if web.input().get('user-suicide'):
            raw_address = get_email()
            store.sign.delete(raw_address)
            store.sync.insert({'mode': 'sign-del', 'val': (raw_address,)})
            web.ctx.session.notice = '邮件地址解绑成功，感谢使用'
        raise web.seeother('/')
        
class work:
    def GET(self):
        add_task(web.ctx, '/kindle/work', 'home2')
        
    def POST(self):
        for item in mail.Inbox().fetch():
            if item['public'] or store.sign.select(item['address']):
                add_task(web.ctx, '/kindle/upload', json.dumps(item))

class upload:
    def split(self, text):
        if len(text) > 140:
            chunks = [text[i:i+134] for i in range(0, len(text), 134)]
            for i, v in enumerate(chunks):
                yield '[%s/%s] %s' % (i+1, len(chunks), v)
        elif len(text) <= 138:
            yield '「%s」' % text        
        else:
            yield text
        
    def POST(self):
        data = json.loads(web.data())
        address = data['address']
        mail_id = data['mail_id']
        if store.sent.select(mail_id):
            return 'Nothing to do.'
        if data['public']:
            token = store.public_token
        else:
            token = store.sign.select(address)
        client = fanfou.OAuth(store.consumer, token)
        for text in self.split(data['text']): 
            body = {'status': text.encode('utf8')}
            resp = client.request('/statuses/update', 'POST',  body)
            statuses_id = json.loads(resp.read())['id']
            store.sent.insert(mail_id, statuses_id)
            store.sync.insert({'mode': 'sent-add', 'val': (mail_id, statuses_id)})
            time.sleep(0.5)
                
class authorize:
    def GET(self):
        http_host = web.ctx.env.get('HTTP_HOST')
        callback = 'http://%s/kindle/callback' % http_host
        client = fanfou.OAuth(store.consumer, callback=callback)
        web.ctx.session.request_token = client.request_token()
        raise web.seeother(client.authorize_url)

class callback:
    def GET(self):
        request_token = web.ctx.session.request_token
        if request_token:
            client = fanfou.OAuth(store.consumer, request_token)
            web.ctx.session.kindle_token = client.access_token()
            web.ctx.session.request_token = None
            raise web.seeother('/')
        else:
            raise web.seeother('/authorize')

class debug:
    def GET(self):
        return store.sent.fetchall()
        
web.config.debug = True
app = web.application(urls, locals())

#app.internalerror = _Error
curdir = os.path.dirname(os.path.abspath(__file__))
render = web.template.render(os.path.join(curdir, 'templates'), globals=globals())

if __name__ == '__main__':
    app.run()