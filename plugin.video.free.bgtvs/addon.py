# -*- coding: utf-8 -*-
import sys, xbmcplugin
from resources.lib.helper import *

reload(sys)  
sys.setdefaultencoding('utf8')

params = get_params()

try: id = int(params["id"])
except: id = None

try: mode = params["mode"]
except: mode = None
	
if mode == None: show_channels()
else: show_streams(id)

xbmcplugin.endOfDirectory(int(sys.argv[1]))