#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import smtplib
import re
from datetime import datetime
from threading import Thread
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from queue import Queue
from sh import git
from tinydb import TinyDB, where
import chardet
from jinja2 import Environment, FileSystemLoader
import pecosys

logger = logging.getLogger(__name__)
queue = Queue()
proc = None


class Processor(Thread):

    def stop(self):
        logger.info("stop requested")
        self.is_running = False

    def run(self):

        # initialize Jinja 2 templating
        template_dir = pecosys.get_config('global', 'cwd') + '/pecosys/templates'
        logger.info("load templates from directory %s" % template_dir)
        self.env = Environment(loader=FileSystemLoader(template_dir))

        self.is_running = True
        while self.is_running:
            req = queue.get()
            if req['type'] == 'comment':
                self.new_comment(req['author'], req['email'], req['site'],
                                 req['url'], req['article'],
                                 req['message'], req['subscribe'])
            elif req['type'] == 'reply_comment_email':
                self.reply_comment_email(req['From'], req['Subject'], req['Body'])
            elif req['type'] == 'unsubscribe':
                self.unsubscribe_reader(req['email'], req['article'])
            else:
                logger.info("Dequeue unknown request " + req)

    def new_comment(self, author, email, site, url, article, message,
                    subscribe):

        try:
            logger.info("new comment received: author %s url %s subscribe %s"
                        % (author, url, subscribe))

            if site and site[:4] != "http":
                site = "http://" + site

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
            branch_name = now.strftime("%Y%m%d%H%M%S%f")
            if pecosys.get_config("git", "disabled"):
                logger.debug("GIT usage disabled (debug mode)")
            else:
                git.checkout('master')
                if pecosys.get_config("git", "remote"):
                    git.pull()

                try:
                    git.checkout(branch_name)
                except:
                    git.branch(branch_name)
                    git.checkout(branch_name)

                comment_filename = 'comment-%s.md' % now.strftime("%Y%m%d-%H%M%S")
                comment_pathname = '%s/%s/%s' % (pecosys.get_config('git', 'comment_path'),
                                                 now.year, comment_filename)
                with open(comment_pathname, 'wb') as f:
                    f.write(comment.encode('UTF-8'))
                git.add(comment_pathname)
                git.commit('-m', 'new comment')
                git.checkout('master')

            # Render email body template
            email_body = self.get_template('new_comment').render(url=url, comment=comment)

            # Send email
            self.mail(pecosys.get_config('post', 'from_email'), pecosys.get_config('post', 'to_email'),
                      '[' + branch_name + '-' + article + ']',  email_body)

            # reader subscribes to further comments
            if subscribe and email:
                self.subscribe_reader(email, article, url)

            logger.debug("new comment processed ")
        except:
            logger.exception("new_comment failure")

    def reply_comment_email(self, from_email, subject, message):
        try:
            m = re.search('\[(\d+)\-(\w+)\]', subject)
            branch_name = m.group(1)
            article = m.group(2)

            message = self.decode_best_effort(message)
            email_body = None

            # safe logic: no answer or unknown answer is a go for publishing
            if message[:2].upper() == 'NO':
                logger.info('discard comment: %s' % branch_name)
                email_body = self.get_template('drop_comment').render(original=message)
            else:
                if pecosys.get_config("git", "disabled"):
                    logger.debug("GIT usage disabled (debug mode)")
                else:
                    git.merge(branch_name)
                    if pecosys.get_config("git", "remote"):
                        git.push()
                    logger.info('commit comment: %s' % branch_name)
                email_body = self.get_template('approve_comment').render(original=message)
                self.notify_readers(article)

            if email_body:
                self.mail(pecosys.get_config('post', 'from_email'), pecosys.get_config('post', 'to_email'),
                          'Re: ' + subject, email_body)

            if pecosys.get_config("git", "disabled"):
                logger.debug("GIT usage disabled (debug mode)")
            else:
                git.branch("-D", branch_name)
        except:
            logger.exception("new email failure")

    def subscribe_reader(self, email, article, url):
        logger.info("subscribe reader %s to %s (%s)" % (email, article, url))
        db = TinyDB(pecosys.get_config('global', 'cwd') + '/db.json')
        db.insert({'email': email, 'article': article, 'url': url})

    def unsubscribe_reader(self, email, article):
        logger.info("unsubscribe reader %s from %s" % (email, article))
        db = TinyDB(pecosys.get_config('global', 'cwd') + '/db.json')
        db.remove((where('email') == email) & (where('article') == article))

    def notify_readers(self, article):
        logger.info('notify readers ' + article)
        db = TinyDB(pecosys.get_config('global', 'cwd') + '/db.json')
        for item in db.search(where('article') == article):
            logger.info(item)
            to_email = item['email']
            logger.info("notify reader %s for article %s" % (to_email, article))
            unsubscribe_url = pecosys.get_config('subscription', 'url') + '?email=' + to_email + '&article=' + article
            email_body = self.get_template('notify_reader').render(article_url=item['url'],
                                                                   unsubscribe_url=unsubscribe_url)
            subject = self.get_template('notify_message').render()
            self.mail(pecosys.get_config('subscription', 'from_email'), to_email, subject, email_body)

    def decode_best_effort(self, string):
        info = chardet.detect(string)
        if info['confidence'] < 0.5:
            return string.decode('utf8', errors='replace')
        else:
            return string.decode(info['encoding'], errors='replace')

    def mail(self, from_email, to_email, subject, *messages):

        # Create the container (outer) email message.
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        msg.preamble = subject

        for message in messages:
            part = MIMEText(message, 'plain')
            msg.attach(part)

        s = smtplib.SMTP(pecosys.get_config('smtp', 'host'),
                         pecosys.get_config('smtp', 'port'))
        if(pecosys.get_config('smtp', 'starttls')):
            s.starttls()
        s.login(pecosys.get_config('smtp', 'login'),
                pecosys.get_config('smtp', 'password'))
        s.sendmail(from_email, to_email, msg.as_string())
        s.quit()

    def get_template(self, name):
        return self.env.get_template(pecosys.get_config('global', 'lang') + '/' + name + '.tpl')


def enqueue(something):
    queue.put(something)


def get_processor():
    return proc


def start(config):
    global proc
    proc = Processor()
    proc.start()
