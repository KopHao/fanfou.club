#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import web
import store
from poems import view as poems
from sms import view as sms
from kindle import view as kindle
from whale import view as whale

urls = (
    '/?', 'index',
    '/poems', poems.app,
    '/sms', sms.app,
    '/kindle', kindle.app,
    '/whale', whale.app
)

class index:
    def GET(self):
        return 'hello, fanfou'


web.config.debug = True
app = web.application(urls, globals())

if web.config.get('_session'):
    session = web.config._session
else:
    session = web.session.Session(app, store.RedisStore())
    web.config._session = session
    
def session_hook():
    web.ctx.session = session
app.add_processor(web.loadhook(session_hook))

if __name__ == '__main__':
    app.run()
