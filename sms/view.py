#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import web
import time
import json
import store
import fanfou
import base62
import datetime
import traceback


def _Error():
    referer = web.ctx.env.get('HTTP_REFERER', web.ctx.home)
    store.trace.insert(referer, traceback.format_exc())
    return web.internalerror('internalerror')
        
def now():
    now = datetime.datetime.now()
    return now.strftime('%y/%m/%d %H:%M')
        
def get_mobile():
    return store.sign.select_by_token(web.ctx.session.sms_token)

    
def notice():
    tmp = web.ctx.session.notice
    web.ctx.session.notice = ''
    return tmp
    
urls = (
    '/?', 'index',
    '/help', 'help',
    '/suicide', 'suicide',
    '/upload', 'upload',
    '/__sync', '__sync',
    '/callback', 'callback',
    '/authorize', 'authorize',
    '/debug', 'debug',
)


class index:
    def GET(self):
        return render.index()
        
    def POST(self):
        raw_mobile = get_mobile()
        new_mobile = web.input().get('mobile')
        if re.match(r'\d{11}', new_mobile):
            if raw_mobile:
                store.sign.delete(raw_mobile)
                store.sync.insert(raw_mobile, 'del')
            store.sign.insert(new_mobile, web.ctx.session.sms_token)
            store.sync.insert(new_mobile, 'add')
            web.ctx.session.notice = '手机号码绑定成功，欢迎试用'
        else:
            web.ctx.session.notice = '请输入正确的手机号码'
        raise web.seeother('/')
        
class help:
    def GET(self):
        return render.help()

class suicide:
    def GET(self):
        return render.suicide()
    
    def POST(self):
        if web.input().get('user-suicide'):
            raw_mobile = get_mobile()
            store.sign.delete(raw_mobile)
            store.sync.insert(raw_mobile, 'del')
            web.ctx.session.notice = '手机号码解绑成功，感谢使用'
        raise web.seeother('/')

class __sync:
    def POST(self):
        data = base62.loads(web.data())
        for item in data:
            store.sync.delete(item)
        return base62.dumps(store.sync.fetchall()) 
        
class upload:
    def POST(self):
        data = base62.loads(web.data())
        mobile = data['mobile']
        token = store.sign.select(mobile)
        if token:
            client = fanfou.OAuth(store.consumer, token)
            body = {'status': data['text'].encode('utf8')}
            resp = client.request('/statuses/update', 'POST',  body)
            store.sent.insert(json.loads(resp.read())['id'])
            return resp.code
                
class authorize:
    def GET(self):
        http_host = web.ctx.env.get('HTTP_HOST')
        callback = 'http://%s/sms/callback' % http_host
        client = fanfou.OAuth(store.consumer, callback=callback)
        web.ctx.session.request_token = client.request_token()
        raise web.seeother(client.authorize_url)

class callback:
    def GET(self):
        request_token = web.ctx.session.request_token
        if request_token:
            client = fanfou.OAuth(store.consumer, request_token)
            web.ctx.session.sms_token = client.access_token()
            web.ctx.session.request_token = None
            raise web.seeother('/')
        else:
            raise web.seeother('/authorize')

class debug:
    def GET(self):
        return store.sign.fetchall()

web.config.debug = True
app = web.application(urls, locals())

#app.internalerror = _Error
curdir = os.path.dirname(os.path.abspath(__file__))
render = web.template.render(os.path.join(curdir, 'templates'), globals=globals())

if __name__ == '__main__':
    app.run()
