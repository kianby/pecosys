#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from clize import clize, run

@clize
def pecosys_server(config_pathname):
    
    os.environ['CONFIG_PATHNAME'] = config_pathname
    from pecosys import app
    app.run(host=app.config['pecosys']['post']['host'], port=app.config['pecosys']['post']['port'], debug=True, use_reloader=False)

if __name__ == '__main__':
    run(pecosys_server)


