# -*- coding: utf-8 -*-
import re, sys, os.path, urllib, urllib2
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.helper import *
		
reload(sys)  
sys.setdefaultencoding('utf8')

params = GetParams()

def Categories():
	for i in range (0, len(clist)):
		AddItem(clist[i]['name'].encode('utf-8'), i, GetIcon(clist[i]))

def AddItem(name, index, icon):
	u = sys.argv[0] + "?index=" + str(index) + "&mode=1&name=" + urllib.quote_plus(name)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
	liz.setInfo( type = "Video", infoLabels = { "Title" : name } )
	liz.setProperty("IsPlayable" , "true")
	ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = False)
	return ok

def Play(index):
	url = GetStream(index)
	xbmc.log("plugin.video.free.bgtvs | Playing stream: " + str(clist[index]['url']))
	li = xbmcgui.ListItem(iconImage = iconimage, thumbnailImage = iconimage, path = url)
	li.setInfo('video', { 'title': name })
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = url))
		
index = None
try: index = int(params["index"])
except: pass

name = None
try: name = urllib.unquote_plus(params["name"])
except: pass

iconimage = None
try: iconimage = urllib.unquote_plus(params["iconimage"])
except: pass

mode = 0
try: mode = int(params["mode"])
except: pass
	
if mode == 0:
	Categories()
elif mode == 1:
	Play(index)

xbmcplugin.endOfDirectory(int(sys.argv[1]))