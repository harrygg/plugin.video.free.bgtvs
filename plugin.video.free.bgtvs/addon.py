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
elif mode == 'show_streams':
	show_streams(id)
else:
	play_stream(id)

xbmcplugin.endOfDirectory(int(sys.argv[1]))