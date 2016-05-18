#!/usr/bin/python
# -*- coding: utf-8 -*
import web
import core
import json

urls = (
    '/add_task', 'add_task',
    '/update_cron', 'update_cron',
)
        
class add_task:        
    def POST(self):
        data = json.loads(web.data())
        core.add_task(data['path'], data['data'])
        
class update_cron:
    def GET(self):
        core.update_cron()
        
app = web.application(urls, globals())

if __name__ == '__main__':
    cron, task = core.run()
    cron.start()
    task.start()
    app.run()
    cron.join()
    task.join()