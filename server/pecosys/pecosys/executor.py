#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import subprocess
import threading

logger = logging.getLogger(__name__)


def async_run(cmd_line):
    try:
        logger.info('start of execution: %s' % cmd_line)
        exitcode = subprocess.call([cmd_line], shell=True)
        if exitcode == 0:
            logger.info('end of execution: %s' % cmd_line)
        else:
            logger.warn('error during execution: %s => %d' % (cmd_line, exitcode))
    except:
        logger.exception("async run exception %s" % cmd_line)


def execute(cmd_line):
    logger.info("execute %s" % cmd_line)
    th = threading.Thread(target=async_run, args=(cmd_line,))
    th.start()
