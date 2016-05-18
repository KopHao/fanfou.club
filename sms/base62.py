#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import base64

def encode(s):
    s = base64.encodestring(s)
    s = ''.join([chr(ord(i)+42) for i in s])
    return base64.encodestring(s)
    
def decode(s):
    s = base64.decodestring(s)
    s = ''.join([chr(ord(i)-42) for i in s])
    return base64.decodestring(s)

def dumps(s):
    return encode(json.dumps(s))

def loads(s):
    return json.loads(decode(s))