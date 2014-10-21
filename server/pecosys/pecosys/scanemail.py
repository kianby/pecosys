#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from threading import Thread
import logging
import re
import pecosys
from pecosys import imap
from pecosys import processor

logger = logging.getLogger(__name__)


class EmailScanner(Thread):

    def stop(self):
        logger.info("stop requested")
        self.is_running = False

    def run(self):

        self.is_running = True

        while self.is_running:

            try:
                with imap.Mailbox(pecosys.get_entire_config()) as mbox:
                    for num in range(mbox.get_count()):
                        msg_num = num + 1
                        msg = mbox.fetch_simple_message(msg_num)
                        self.process(mbox, msg_num, msg)
                        break

                    time.sleep(30)

            except:
                logger.exception("main loop exception")

            # exit on crash
            time.sleep(10)
        self.is_running = False

    def process(self, mbox, msg_num, msg):

        # log message
        logger.info('%s Message %d %s' % ('-' * 30, msg_num, '-' * 30))
        for key in msg.keys():
            logger.info('%s = %s' % (key, msg[key]))

        if self.is_reply_comment(msg):
            msg['type'] = 'reply_comment_email'
            processor.enqueue(msg)

        # delete message
        mbox.delete_message(msg_num)

    def is_reply_comment(self, msg):
        return re.match(".*\[.*\]", msg["Subject"])


def start(config):
    scanner = EmailScanner()
    scanner.start()
