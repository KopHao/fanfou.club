#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import poplib
import email
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

import store

class Inbox:
    def __init__(self):
        self.conn = poplib.POP3_SSL('pop.qq.com')
        self.conn.user('your mail')
        self.conn.pass_('pop3 pass_')
        self.mails = []
        self.inbox = []
   
    def fetch(self):
        resp, mails, octets = self.conn.uidl()
        mail_ids = [mail.split(' ')[1] for mail in mails]
        for mail_id in mail_ids:
            if not store.sent.select(mail_id):
                pos = mail_ids.index(mail_id) + 1
                resp, lines, octets = self.conn.retr(pos)
                self.mails.append({'mail_id': mail_id, 'mail': '\r\n'.join(lines)})
        self.conn.quit()
        for mail in self.mails:
            self.parse(mail)
        return self.inbox
        
    def parse(self, mail):
        msg = Parser().parsestr(mail.get('mail'))
        text = None
        reply_to = msg.get('reply-to')
        _from = parseaddr(msg.get('from'))[1]
        public = 'public@fanfou.club' in msg.get('to')
        subject = self.decode_str(msg.get('subject'))
        for part in msg.walk():
            if not part.is_multipart():
                if part.get_content_type() in ('text/plain', 'text/html'):
                    content = part.get_payload(decode=True)
                    charset = self.get_charset(part)
                    if charset: content = content.decode(charset)
        templates = (
            ur'Hi, I\'m reading this book, and wanted to share this quote with you\.[\r\n]+"([\s\S]+)" \(from',
            ur'Hi, I\'m reading this book, and wanted to share this quote with you\.[\r\n]+《([\s\S]+)》\(摘自由',
            ur'嗨，我正在读这本书，想跟您分享一句名言。[\r\n]+"([\s\S]+)" \(from',
            ur'嗨，我正在读这本书，想跟您分享一句名言。[\r\n]+《([\s\S]+)》\(摘自由',
            ur'您好，我觉得这本书值得一读，您怎么看？[\r\n]+"([\s\S]+)" by',            
        )
        for template in templates:
            matching =  re.search(template, content)
            if matching:
                text = matching.group(1)
                break
        if text:
            self.inbox.append({'address': reply_to, 'text': text, 'mail_id': mail['mail_id'], 'public': public})
        
    def get_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    def decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

if __name__ == '__main__':
    inbox = Inbox()
    print inbox.fetch()