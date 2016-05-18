#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import uuid
import base64
import json
import redis

db = redis.Redis()

def create_key(name):
    return base64.b64encode(uuid.uuid5(uuid.NAMESPACE_OID, name).bytes)[:-2]

def create_node(name):
    root = db.get('table_index') or '{}'
    root = json.loads(root)
    root[name] = create_key(name)
    db.set('table_index', json.dumps(root))
    return root[name]

def select_node(name):
    root = db.get('table_index') or '{}'
    root = json.loads(root)
    name = root.get(name) or create_node(name)
    node = db.get(name) or '{}'
    return name, json.loads(node)

def commit_node(name, node):
    db.set(name, json.dumps(node))

def drop_node(name):
    root = db.get('table_index') or '{}'
    root = json.loads(root)
    node = root.get(name)
    try:
        db.delete(node)
        del root[name]
        db.set('table_index', json.dumps(root))
    except KeyError, k:
        raise AttributeError, k

def select(name, key):
    name, node = select_node(name)
    return node.get(key)

def insert(name, key, val):
    name, node = select_node(name)
    node[key] = val
    commit_node(name, node)

def update(name, key, val):
    name, node = select_node(name)
    node[key] = val
    commit_node(name, node)

def delete(name, key):
    name, node = select_node(name)
    try:
        del node[key]
        commit_node(name, node)
    except KeyError, k:
        raise AttributeError, k

def select_all(name):
    name, node = select_node(name)
    return node

if __name__ == '__main__':
    print 'table_index --> %s' % db.get('table_index')
    for name, index in json.loads(db.get('table_index') or '{}').items():
        print '%s\n%s (%s) --> %s' % ('-' * 20, index, name, db.get(index))