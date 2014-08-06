"""
CaCause plugin for Pelican
==========================

This plugin allows you to define a LICENSE setting and adds the contents of that
license variable to the article's context, making that variable available to use
from within your theme's templates.
"""

import sys
import os
import hashlib
import six
from pelican import signals
from pelican import readers
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
cacause_context = {}


def get_article_id(source_filename):
    m = hashlib.md5()
    m.update(source_filename)
    return m.hexdigest()


def read_comment(comment_file, header=True):

    content = None
    if comment_file[-4:] == '.rst':
        reader = readers.RstReader({})
        body, metadata = reader.read(comment_file)
        content = metadata if header else body
    elif comment_file[-3:] == '.md':
        reader = readers.MarkdownReader({'MD_EXTENSIONS':{}})
        body, metadata = reader.read(comment_file)
        content = metadata if header else body
    # return header or body
    return content


def read_comments(comment_dir):
    cacause_context['comments'] = {}
    for dirpath, dirs, files in os.walk(comment_dir):
        for filename in files:
            if filename.endswith(('.md','.rst')):
                absolute_comment_file = '/'.join([dirpath, filename])
                cfg = read_comment(absolute_comment_file)
                cfg['comment'] = absolute_comment_file
                article_id = cfg['article']
                if article_id:
                    if not article_id in cacause_context['comments']:
                        cacause_context['comments'][article_id] = []
                    cacause_context['comments'][article_id].append(cfg)


def build_comment_context(generator):

    if not 'comments' in cacause_context:
        if not 'CACAUSE_DIR' in generator.settings.keys():
            logger.error("cacause: can't find CACAUSE_DIR in pelicanconf.py")
            sys.exit(1)
        cacause_dir = generator.settings['CACAUSE_DIR']
        read_comments(cacause_dir)


def enhance_article(sender):

    source_path = sender.get_relative_source_path()
    if source_path.endswith(('.md','.rst')):
        article_id = get_article_id(source_path)
        logger.info("cacause: enhance article %s" % (source_path))
        if article_id in cacause_context['comments']:
            posts = []
            print cacause_context['comments'][article_id]
            sorted_posts = sorted(cacause_context['comments'][article_id], key
                    = lambda post: (post['date'] if 'date' in post else datetime.now()))
            #for post in cacause_context['comments'][article_id]:
            for post in sorted_posts:
                # convert Markup to HTML
                filename = post['comment']
                body = read_comment(filename, False)
                post['body'] = body
                # add Gravatar image
                email = post['email']
                email_bytes = six.b(email).lower()
                gravatar_url = "http://www.gravatar.com/avatar/%s" % \
                    hashlib.md5(email_bytes).hexdigest()
                post['gravatar'] = gravatar_url
                posts.append(post)
            logger.info("cacause: related comments count: %d" % len(posts))
            sender.cacause_comment = posts
        # store article id in article context 
        sender.cacause_article = article_id


def register():
    signals.initialized.connect(build_comment_context)
    signals.content_object_init.connect(enhance_article)
