# -*- coding: utf-8 -*-
import xbmcplugin
from resources.lib.helper import *

params = get_params()
id = params.get("id")
mode = params.get("mode")

if mode == None: 
  show_categories()
elif mode == 'show_channels':
  show_channels(id)
elif mode == 'show_streams':
  show_streams(id)
elif mode == 'update_tvdb':
  update_tvdb()
else:
  play_channel(id)

xbmcplugin.endOfDirectory(int(sys.argv[1]))