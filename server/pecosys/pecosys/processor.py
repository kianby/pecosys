#!/usr/bin/env python
#-*- coding:utf-8 -*-

import logging
import smtplib
import threading
import re
from datetime import datetime
from threading import Thread
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from queue import Queue
import sh
from sh import git
import pecosys

logger = logging.getLogger(__name__)
queue = Queue()

class Processor(Thread):

    def stop(self):
        logger.info("stop requested")
        self.is_running = False

    def run(self):

        self.is_running = True
        while self.is_running:
            req = queue.get()
            if req['type'] == 'comment':
                self.new_comment(req['author'], req['email'], req['site'], req['url'], req['article'], req['message'])
            elif req['type'] == 'reply_comment_email':
                self.reply_comment_email(req['From'], req['Subject'], req['Body'])
            else:
              logger.info("Dequeue unknown request " + req)

    def new_comment(self, author, email, site, url, article, message):

        try:
            logger.info("new comment received ")

            # Create comment
            now = datetime.now()
            comment_list = (
                'author: %s' % author,
                'email: %s' % email,
                'site: %s' % site,
                'date: %s' % now.strftime("%Y-%m-%d %H:%M:%S"),
                'url: %s' % url,
                'article: %s' % article,
                '',
                '%s' % message,
                ''
            )
            comment = '\n'.join(comment_list)

            logger.debug(comment)

            # Git 
            if pecosys.get_config("git", "remote"):
                git.pull()

            branch_name = now.strftime("%Y%m%d%H%M%S%f")
            try:
                git.checkout(branch_name)
            except:
                git.branch(branch_name)
                git.checkout(branch_name)

            comment_filename = 'comment-%s.md' % now.strftime("%Y%m%d-%H%M%S")
            comment_pathname = '%s/%s/%s' % (pecosys.get_config('git', 'comment_path'), now.year, comment_filename)
            with open(comment_pathname, 'a') as f:
                f.write('%s' % comment)
            git.add(comment_pathname)
            git.commit('-m', 'new comment')
            git.checkout('master')

            # Send email
            mail('[' + branch_name + ']',  "Reply to publish following comment or reply NO to reject comment\n\n%s" % comment)

            logger.debug("new comment processed ")
        except:
            logger.exception("new_comment failure")


    def reply_comment_email(self, from_email, subject, message):
        try:
            m = re.search('\[(\d+)\]', subject)
            branch_name = m.group(1)

            # positive logic: no answer or unknown answer is a go for publishing
            if message[:2].upper() == 'NO'.encode('UTF-8'):
                logger.info('discard comment: %s' % branch_name)
                mail('Re: [%s]' % branch_name, "comment discarded\n\n%s" % message.decode("latin-1"))
            else:
                git.merge(branch_name)
                if pecosys.get_config("git", "remote"):
                    git.push()                            
                logger.info('commit comment: %s' % branch_name)  
                mail('Re: [%s]' % branch_name, "comment published\n\n%s" % message.decode("latin-1"))
            git.branch("-D", branch_name)
        except:
            logger.exception("new email failure")
   
def mail(subject, *messages):

    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = pecosys.get_config('post', 'from_email')
    msg['To'] = pecosys.get_config('post', 'to_email')
    msg.preamble = subject

    for message in messages:
        part = MIMEText(message, 'plain')
        msg.attach(part)
    
    s = smtplib.SMTP(pecosys.get_config('smtp', 'host'), pecosys.get_config('smtp','port'))
    if( pecosys.get_config('smtp','starttls')):
        s.starttls()
    s.login(pecosys.get_config('smtp','login'), pecosys.get_config('smtp','password'))
    s.sendmail(pecosys.get_config('post','from_email'), pecosys.get_config('post','to_email'), msg.as_string())
    s.quit()

def enqueue(something):
    queue.put(something)

def start(config):
    proc = Processor()
    proc.start()


