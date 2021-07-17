# -*- coding: utf-8 -*-
from .plugin import P
blueprint = P.blueprint
menu = P.menu
plugin_load = P.logic.plugin_load
plugin_unload = P.logic.plugin_unload
plugin_info = P.plugin_info
try:
    import xmltodict
except:
    from framework import app
    import os
    try: os.system(f"{app.config['config']['pip']} install xmltodict")
    except: pass
try:
    import lzstring
except:
    from framework import app
    import os
    try: os.system(f"{app.config['config']['pip']} install lzstring")
    except: pass
