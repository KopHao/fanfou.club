#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import web
import json
import time
import fanfou
import store
import datetime
from tasks import add_task

urls = (
    '/?', 'index',
    '/work', 'work',
    '/send', 'send',
    '/info', 'info',
    '/check', 'check',
    '/update', 'update',
    '/debug', 'debug',
)


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


class UTC(datetime.tzinfo):
    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self._offset)

    def tzname(self, dt):
        return 'UTC %+d:00' % self._offset

    def dst(self, dt):
        return datetime.timedelta(hours=self._offset)


class index:
    def GET(self):
        return 'hello, fanfou'


class work:
    def GET(self):
        now, path = datetime.datetime.now(UTC(8)), None
        if now.hour == 8 and now.minute < 5:
            path = '/poems/send'
        elif now.hour == 4 and now.minute < 5:
            path = '/poems/update'
            
        if path:
            for item in store.user.fetchall().items():
                add_task(web.ctx, path, json.dumps(item))

class send:
    def POST(self):
        user_id, user_name = json.loads(web.data())
        status = u'@%s %s' % (user_name, store.poems.one())
        body = {
            'status': status.encode('utf-8'),
            'in_reply_to_user_id': user_id.encode('utf-8'),
            'mode': 'lite'
        }
        client.request1('/statuses/update', 'POST', body)
        time.sleep(3.0)


class info:
    def POST(self):
        user_id, user_name, act = json.loads(web.data())
        msg = {'-join': '欢迎加入', '-quit': '退出成功'}.get(act)
        body = {
            'status': '@%s %s %s' % (user_name.encode('utf-8'), msg, store.emoji()),
            'in_reply_to_user_id': user_id.encode('utf-8'),
            'mode': 'lite'
        }
        client.request2('/statuses/update', 'POST', body)
        time.sleep(1.5)


class check:
    def argv(self, text):
        m = re.match(r'^@{1}.+ +(?P<act>-\w+)\s*$', text)
        if m: return m.group('act')
    
    def GET(self):
        resp = client.request1('/account/notification', 'GET', {'mode': 'lite'})
        data = json.loads(resp.read())
        amount = data['mentions']
        count = 60 if amount > 20 else 20
        pages = amount / count + 2
        for page in range(1, pages):
            body = {'count': count, 'page': page, 'mode': 'lite'}
            resp = client.request1('/statuses/mentions', 'GET', body)
            for item in json.loads(resp.read()):
                act = self.argv(item['text'])
                user_id = item['user']['id']
                user_name = item['user']['name']
                if store.sent.select(item['id']):
                    continue
                if act == '-join' and not store.user.select(user_id):
                    store.user.insert(user_id, user_name)
                    store.sent.insert(item['id'])
                    body = (user_id, user_name, act)
                    add_task(web.ctx, '/poems/info', json.dumps(body))
                elif act == '-quit' and store.user.select(user_id):
                    store.user.delete(user_id)
                    store.sent.insert(item['id'])
                    body = (user_id, user_name, act)
                    add_task(web.ctx, '/poems/info', json.dumps(body))


class update:
    def POST(self):
        user_id, user_name = json.loads(web.data())
        body = {'id': user_id.encode('utf-8'), 'mode': 'lite'}
        resp = client.request1('/users/show/:id', 'GET', body)
        user_name = json.loads(resp.read())['name']
        store.user.update(user_id, user_name)
        time.sleep(3.0)


class debug:
    def GET(self):
        user_id = web.input().get('user_id')
        if user_id:
            store.user.insert(user_id, 'null')
        return user_id


web.config.debug = True
app = web.application(urls, locals())

if __name__ == '__main__':
    app.run()
