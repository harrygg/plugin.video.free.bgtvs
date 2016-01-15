# -*- coding: utf-8 -*-
import re, sys, os.path, urllib, urllib2
from resources.lib.helper import *		

reload(sys)  
sys.setdefaultencoding('utf8')

params = GetParams()

i = None
try: i = int(params["i"])
except: pass

s = None
try: s = int(params["s"])
except: pass

mode = None
try: mode = params["mode"]
except: pass
	
if mode == None: ListChannels()
else: Play(i,s)

xbmcplugin.endOfDirectory(int(sys.argv[1]))