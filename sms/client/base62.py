#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import base64

def encode(s):
    s = str.encode(s, 'utf8')
    s = base64.encodestring(s)
    s = bytes([i+42 for i in s])
    s = base64.encodestring(s)
    return bytes.decode(s, 'utf8')
    
def decode(s):
    s = str.encode(s, 'utf8')
    s = base64.decodestring(s)
    s = bytes([i-42 for i in s])
    s = base64.decodestring(s)
    return bytes.decode(s, 'utf8')


def dumps(s):
    return encode(json.dumps(s))

def loads(s):
    return json.loads(decode(s))