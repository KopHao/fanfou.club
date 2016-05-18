#!/usr/bin/python
# -*- coding: utf-8 -*-
import web
import redis

mask = 'webpy_session_'

class RedisStore(web.session.Store):
    def __init__(self, timeout=86400, initial_flush=False):
        self.db = redis.Redis(db=8)
        self.timeout = timeout
        if initial_flush:
            self.db.flushdb()
    
    def __contains__(self, key):
        return bool(self.db.get(mask+key))

    def __getitem__(self, key):
        data = self.db.get(mask+key)
        if data:
            self.db.expire(mask+key, self.timeout)
            return self.decode(data)
        else:
            raise KeyError

    def __setitem__(self, key, value):
        self.db.set(mask+key, self.encode(value))
        self.db.expire(mask+key, self.timeout)
                
    def __delitem__(self, key):
        self.db.delete(mask+key)

    def cleanup(self, timeout):
        # Nothing to do
        pass