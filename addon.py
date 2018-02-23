# -*- coding: utf-8 -*-
import sys
import xbmcplugin
from resources.lib.helper import *

params = get_params()
log('Running with params: {0}'.format(params))

action = params.get("action")
id = params.get("id")

if action == None: 
  show_categories()
elif action == 'show_channels':
  show_channels(id)
elif action == 'show_streams':
  show_streams(id)
elif action == 'update_tvdb':
  update_tvdb()
else:
  play_channel(id)

xbmcplugin.endOfDirectory(int(sys.argv[1]))