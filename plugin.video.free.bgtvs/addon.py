# -*- coding: utf-8 -*-
import re, sys, os.path, urllib, urllib2
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.helper import *		

reload(sys)  
sys.setdefaultencoding('utf8')

params = GetParams()

def Categories():
	for i in range (0, len(clist)):
		if Enabled(i):
			AddItem(i)

def AddItem(i):
	name = GetName(i)
	icon = GetIcon(i)
	li = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
	li.setInfo( type = "Video", infoLabels = { "Title" : name } )
	if clist[i]['id'] != 'separator':
		li.setProperty("IsPlayable", 'True')
	u = "%s?i=%s&mode=Play" % (sys.argv[0], i)
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, li, False)

def Play(i):
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = GetStream(i)))
		
i = None
try: i = int(params["i"])
except: pass

mode = None
try: mode = params["mode"]
except: pass
	
if mode == None: Categories()
else: Play(i)

xbmcplugin.endOfDirectory(int(sys.argv[1]))