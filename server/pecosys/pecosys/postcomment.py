#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import logging
from flask import Flask, redirect, request
from pecosys import app
from pecosys import processor

logger = logging.getLogger(__name__)

@app.route("/postcomment", methods=['POST'])
def postcomment():

    logger.info("new comment !!!!")
    source_url = request.headers.get('referer', '')
    url = app.config["pecosys"]["post"]["redirect_url"]
    try:

        if app.config["pecosys"]["post"]["redirect_referer"]:
            url = app.config["pecosys"]["post"]["redirect_url"] + '?referer=' + request.headers.get('referer', '')
        else:
            url = request.headers.get('referer', app.config["pecosys"]["post"]["redirect_url"])

        # get form values and create comment file
        author = request.form['author']
        email = request.form['email']
        site = request.form['site']
        article = request.form['article']
        message = request.form['message']
        # honeypot for spammers
        captcha = ""
        if "captcha" in request.form:
            captcha = request.form['captcha']            
        if captcha:
            logger.warn("discard spam: captcha %s author %s email %s site %s article %s message %s" % (captcha, author, email, site, article, message))
        else:
            req = { 'type':'comment', 'author':author, 'email':email, 'site':site, 'article':article, 'message':message, 'url':source_url}
            processor.enqueue(req)

    except:
        logger.exception("postcomment failure")

    return redirect(url)
