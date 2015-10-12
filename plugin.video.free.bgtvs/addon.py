# -*- coding: utf-8 -*-


import re, sys, os.path, urllib, urllib2
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.channels import *

reload(sys)  
sys.setdefaultencoding('utf8')
_addon = xbmcaddon.Addon(id='plugin.video.free.bgtvs')
_language = _addon.getLocalizedString

def CATEGORIES():
	addDir('Канали на БНТ', 'http://tv.bnt.bg/bnt1/16x9/', 3, 'http://bnt.bg/newImages/newDesign/head/bnt-logo.png')
	for channel in channels:
		addLink(channel.name, channel.url, 2, channel.icon)

def PLAY(url):
	xbmc.log("[plugin.video.free.bgtvs] | Playing stream: " + url)
	li = xbmcgui.ListItem(iconImage=iconimage, thumbnailImage=iconimage, path=url)
	li.setInfo('video', { 'title': name })
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=url))

def BNT(url):
	for channel in bnt_channels:
		addLink(channel.name, channel.toString(), 2, channel.icon)
	
def addLink(name, url, mode, icon = ''):
	return addItem(name, url, mode, False, icon)

def addDir(name, url, mode, vbstart = ''):
	return addItem(name, url, mode, True, '', vbstart)

def addItem(name, url, mode, isDir, icon = '', vbstart = ''):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	liz.setProperty("IsPlayable" , "true")
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isDir)
	return ok
	
def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

params=get_params()
url=None
name=None
iconimage=None
mode=None
vbstart = '0'

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.unquote_plus(params["name"])
except:
	pass
try:
	iconimage = urllib.unquote_plus(params["iconimage"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass
	
if mode==None or url==None or len(url)<1:
	CATEGORIES()
    
elif mode==2:
	PLAY(url)
	
elif mode==3:
	BNT(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))