#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import time
import datetime
import urllib2
import json
import redis
import threading

pwd = os.path.dirname(os.path.abspath(__file__))

db = redis.Redis()

class Job(dict):
    def __init__(self, path):
        self.path = path
        
    def __getattr__(self, key): 
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k
    
    def __setattr__(self, key, value): 
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k
    
    def __repr__(self):     
        return '<Crontab ' + dict.__repr__(self) + '>'


class UTC(datetime.tzinfo):
    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self._offset)

    def tzname(self, dt):
        return 'UTC %+d:00' % self._offset

    def dst(self, dt):
        return datetime.timedelta(hours=self._offset)

def now():
    now = datetime.datetime.now(UTC(8))
    if now.weekday() == 6:
        now_weekday = 0
    else:
        now_weekday = now.weekday() + 1
    now = {
        'minute': now.minute,
        'hour': now.hour,
        'day': now.day,
        'month': now.month,
        'weekday': now_weekday
    }
    return now

def sub_in(now, job):
    for key in now.keys():
        if now[key] not in job[key]:
            return False
    return True

def parse_job(node, sort, scope, job):
    if node == '*':
        job[sort] = range(*scope)
    elif '/' in node:
        node,  step = node.split('/')
        if '-' in node:
            scope = map(int, node.split('-'))
            scope = [scope[0], scope[1]+1]
        scope.append(int(step))
        job[sort] = range(*scope)
    elif '-' in node:
        scope = map(int, node.split('-'))
        scope = [scope[0], scope[1]+1]
        job[sort] = range(*scope)
    elif ',' in node:
        job[sort] = map(int, node.split(','))
    else:
        job[sort] = [int(node)]
    
def parse_tab(line):
    jobs = json.loads(db.get('cron.py'))
    cron, job = line[:5], Job(' '.join(line[5:]))
    parse_job(cron[0], 'minute', [0, 60], job)
    parse_job(cron[1], 'hour', [0, 24], job)
    parse_job(cron[2], 'day', [1, 32], job)
    parse_job(cron[3], 'month', [1, 13], job)
    parse_job(cron[4], 'weekday', [0, 7], job)
    jobs.append(job)
    db.set('cron.py', json.dumps(jobs))



def update_cron():
    db.set('cron.py', json.dumps([]))
    with open(os.path.join(pwd, 'cron.tab')) as cron_tab:
        for line in cron_tab.readlines():
            parse_tab(line.strip().split(' '))


def request(path, data=None):
    now = datetime.datetime.now()
    now = now.strftime('%d/%b/%Y %H:%M:%S')
    try:
        req = urllib2.Request(path)
        resp = urllib2.urlopen(req, data)
        return '[%s] %s - %s' % (now, path, resp.code)
    except Exception, ex:
        return '[%s] %s - %s' % (now, path, ex)     

def daemon_cron():
    while True:
        jobs = json.loads(db.get('cron.py'))
        for job in jobs:
            if sub_in(now(), job):
                print request(job.get('path'))
        time.sleep(59)

def add_task(path, data):
    tasks = json.loads(db.get('task.py') or '[]')
    tasks.append((path, data))
    db.set('task.py', json.dumps(tasks))

def pop_task():
    task = None
    tasks = json.loads(db.get('task.py') or '[]')
    if tasks:
        task = tasks.pop(0)
        db.set('task.py', json.dumps(tasks))
    return task

def daemon_task():
    while True:
        task = pop_task()
        if task:
            print request(*task)
        time.sleep(0.01)        

def run():
    update_cron()
    cron = threading.Thread(target=daemon_cron)
    task = threading.Thread(target=daemon_task)
    return cron, task
        
if __name__ == '__main__':
    cron, task = run()
    cron.start()
    task.start()
    cron.join()
    task.join()