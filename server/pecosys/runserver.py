#!/usr/bin/env python
#-*- coding:utf-8 -*-

from pecosys import app
app.run(host=app.config['pecosys']['post']['host'], port=app.config['pecosys']['post']['port'], debug=True, use_reloader=False)