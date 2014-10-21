#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)

from pecosys import postcomment
from pecosys import processor
from pecosys import scanemail


def load_config():
    """ load global config from json file
    """
    config_path = os.environ['CONFIG_PATHNAME']
    logger.info("Load config from %s" % config_path)
    with open(config_path, 'rt') as config_file:
        config = json.loads(config_file.read())
        return config


def configure_logging(level):

    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)


def get_entire_config():
    return config


def get_config(section, param, value=None):
    try:
        value = config[section][param]
    except:
        logger.warn("missing config param %s.%s" % (section, param))
    return value

# configure logging
logger = logging.getLogger(__name__)
configure_logging(logging.DEBUG)

# configure flask

config = load_config()
config["git"]["disabled"] = bool(os.environ['NO_GIT'])
config["global"]["cwd"] = os.getcwd()
app.config["pecosys"] = config

# i18n
default_locale = config['global']['lang']
logger.debug("Locale: %s" % default_locale)

# start processor thread
processor.start(config)

# start email scanner thread
scanemail.start(config)

# initialize postcomment
postcomment.init()

# change dir to GIT repository
os.chdir(get_config('git', 'repo_path'))

app.wsgi_app = ProxyFix(app.wsgi_app)

logger.info("Start Pecosys application")
