# -*- coding: utf-8 -*-
import sys, xbmcplugin
from resources.lib.helper import *

reload(sys)  
sys.setdefaultencoding('utf8')

params = get_params()

try: id = params["id"]
except: id = None

try: mode = params["mode"]
except: mode = None
	
if mode == None: 
	show_categories()
elif mode == 'show_channels':
	show_channels(id)
elif mode == 'show_streams':
	show_streams(id)
else:
	play_channel(id)

xbmcplugin.endOfDirectory(int(sys.argv[1]))