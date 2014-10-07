#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from clize import clize, run

@clize
def pecosys_server(config_pathname,no_git=False):
    
    os.environ['CONFIG_PATHNAME'] = config_pathname
    if no_git:
        os.environ['NO_GIT'] = str(no_git)
    else:
        os.environ['NO_GIT'] = ''

    from pecosys import app
    app.run(host=app.config['pecosys']['post']['host'], port=app.config['pecosys']['post']['port'], debug=True, use_reloader=False)

if __name__ == '__main__':
    run(pecosys_server)


