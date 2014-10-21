#!/usr/bin/env python
# -*- coding:utf-8 -*-

import imaplib
import email
import logging


class Mailbox(object):

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        host = self.config["imap"]["host"]
        port = self.config["imap"]["port"]
        use_ssl = self.config["imap"]["ssl"]
        if use_ssl:
            self.imap = imaplib.IMAP4_SSL(host, port)
        else:
            self.imap = imaplib.IMAP4(host, port)
        login = self.config["imap"]["login"]
        password = self.config["imap"]["password"]
        self.imap.login(login, password)
        return self

    def __exit__(self, type, value, traceback):
        self.imap.close()
        self.imap.logout()

    def get_count(self):
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'ALL')
        return sum(1 for num in data[0].split())

    def fetch_message(self, num):
        self.imap.select('Inbox')
        status, data = self.imap.fetch(str(num), '(RFC822)')
        email_msg = email.message_from_bytes(data[0][1])
        return email_msg

    def fetch_simple_message(self, num):
        simple_msg = {"Imap": num}
        msg = self.fetch_message(num)
        for key in ('Date', 'From', 'To', 'Subject'):
            simple_msg[key] = msg[key]
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type and content_type == 'text/plain':
                body = part.get_payload(decode=True)
                simple_msg['Body'] = body
        self.logger.debug(simple_msg)
        return simple_msg

    def delete_message(self, num):
        self.imap.select('Inbox')
        self.imap.store(str(num), '+FLAGS', r'\Deleted')
        self.imap.expunge()

    def delete_all(self):
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'ALL')
        for num in data[0].split():
            self.imap.store(num, '+FLAGS', r'\Deleted')
            self.imap.expunge()

    def print_msgs(self):
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'ALL')
        for num in reversed(data[0].split()):
            status, data = self.imap.fetch(num, '(RFC822)')
            self.logger.debug('Message %s\n%s\n' % (num, data[0][1]))
