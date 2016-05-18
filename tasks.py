#!/usr/bin/python
# -*- coding: utf-8 -*
import web
import json
import urllib2

def add_task(ctx, path, data):
    req = urllib2.Request('http://localhost:4096/add_task')
    data = {'path': ctx.homedomain+path, 'data': data}
    resp = urllib2.urlopen(req, json.dumps(data))
    return resp.code