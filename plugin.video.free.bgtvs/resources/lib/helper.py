# -*- coding: utf-8 -*-
import urllib, urllib2, re, xbmc, sys, json, os, xbmcaddon, xbmcgui, xbmcplugin, base64
from datetime import datetime, timedelta	

clist = []
id = 'plugin.video.free.bgtvs'
addon = xbmcaddon.Addon(id=id)
showDisabled =  True if addon.getSetting('show_disabled') == "true" else False
aName = 'assets.json'
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
afp = os.path.join(profile, aName)
ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
cookie = None
#Settings
showDisabledAssets =  True if addon.getSetting('show_disabled') == "true" else False
debug =  True if addon.getSetting('debug') == "true" else False
useRemoteAssets = True if addon.getSetting('listType') == "0" else False
remoteAssetsUrl =  addon.getSetting('url')
localAssetsPath =  addon.getSetting('file')

def Request(url, ref = ''):
	req = urllib2.Request(url)
	if ref == '': 
		ref = url
	xbmc.log("%s | Request() | url=%s, ref=%s" % (id, url, ref))
	req.add_header('Referer', ref)
	req.add_header('User-Agent', ua)
	res = urllib2.urlopen(req)
	global cookie
	cookie = res.info().getheader('Set-Cookie')
	if cookie != None:
		cookie = urllib.quote(cookie)
	r = res.read()
	res.close()
	return r

def Log(msg, level = xbmc.LOGERROR):
	xbmc.log(" | " + id + " | " + str(msg), level)
	
def GetNewAssetsList():
	try:
		if useRemoteAssets == True:
			res = Request(remoteAssetsUrl)
			global clist, categories
			clist = json.loads(res)['assets']
			categories = json.loads(res)['categories']
			if not os.path.exists(os.path.dirname(afp)):
				try:
					os.makedirs(os.path.dirname(afp))
				except OSError as exc: 
					pass # Guard against race condition
					if exc.errno != errno.EEXIST: 
						raise
			with open(afp, "w") as f:
				f.write(res)
		else:
			LoadAssets(localAssetsPath)
	except Exception, er:
		Log(str(er))
		if debug:
			Log("\rSERVER RESPONSE: " + res )
		LoadAssets(os.path.join(os.path.dirname(os.path.realpath(__file__)), aName))

def LoadAssets(file = ""):
	df = open(file) 
	global clist, categories
	content = json.load(df)
	categories = content['categories']
	clist = content['assets']
	df.close()
	
#load assets
try:
	if os.path.exists(afp):
		#check if the file is too old
		treshold = datetime.now() - timedelta(hours=12)
		file_modified = datetime.fromtimestamp(os.path.getmtime(afp))
		if file_modified < treshold: #file is more than a day old
			GetNewAssetsList()
		else: #file is new
			LoadAssets(afp)
	else: #file does not exist, perhaps first run
		GetNewAssetsList()
except Exception, er:
	Log(er)
	xbmc.executebuiltin('Notification(%s,%s,10000,%s)'%('Free BG TVs', 'Неуспешно зареждане на списъка с канали',''))          

def GetStream(i,n):
	if 'pl' in clist[i]['s'][n].keys():
		stream = GetStreamFromSource(clist[i]['s'][n])
	else:
		s = clist[i]['s'][n]['u']
		s = base64.b64decode(s)
		if '3583019' in s: # BiT
			stream = GetLiveStream(clist[i]['s'][0])
		else: # else return the url
			stream = s
	xbmc.log("%s | GetStream() returned %s" % (id, stream))
	return stream

def GetStreamFromSource(stream):
	try:
		pl = base64.b64decode(stream['pl'])
		pa = base64.b64decode(stream['pa'])
		res = Request(pl, pa)
		m = re.compile('video.+src[=\s"\']+(.+?)[\s"\']+', re.DOTALL).findall(res)
		src = "" if len(m) == 0 else m[0]
		#travelhd wrong stream name hack
		if 'playerCommunity' in pl:
			src.replace('/community/community', '/travel/community')	
		return src
	except:
		return base64.b64decode(stream['u'])

def GetLiveStream(url):
	r = Request(url)
	json_res = json.loads(r)
	pl = json_res['stream_info']['m3u8_url']
	r = Request(pl)	
	m = re.compile('(http.+av\-p\.m3u8.+)').findall(r)
	if len(m) > 0:
		p = m[0] + '|User-Agent=' + ua
		if cookie != '' :
			p = p + '&Cookie=' + cookie
		return p

def GetParams():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?','')
		if (params[len(params)-1] == '/'):
			params = params[0:len(params) - 2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				param[splitparams[0]] = splitparams[1]
	return param

def GetName(i, n):
	name = base64.b64decode(clist[i]['n']).encode('utf-8')
	if n > 0:
		try: 
			hd = clist[i]['s'][n]['hd']
			if hd == 1: hd = 'HD' 
		except: hd = ''
		#type = base64.b64decode(clist[i]['s'][n]['u']).split(':')[0]
		indent = '     '
		if len(str(i)) > 1: indent = indent + '   ' #increase the indentation
		name = '%s%s %s (стрийм %s)' % (indent, name, hd, n + 1)
	else:
		name = "%s. %s" % (val.next(), name)
	return name

def GetNumber():
	for i in range(1, len(clist) + 1):
		yield i
		
val = GetNumber()

def Enabled(i):
	return False if 'd' in clist[i].keys() and clist[i]['d'] == "1" else True 

def AddItem(i, n):
	name = GetName(i, n)
	if not Enabled(i): #change color of disabled channel
		name = '[COLOR brown]' + name + '[/COLOR]'
	icon = base64.b64decode(clist[i]['l'])
	li = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
	li.setInfo( type = "Video", infoLabels = { "Title" : name } )
	li.setProperty("IsPlayable", 'True')
	u = "%s?i=%s&s=%s&mode=Play" % (sys.argv[0], i, n)
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, li, False)

def Play(i,s):
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = GetStream(i,s)))
	#u = "%s" % (sys.argv[0])
	#builtin = 'Container.Update(%s)' % (u)
	#xbmc.executebuiltin(builtin)

def AddSeparator(cat):
	name = '---------------------------------------    %s    -----------------------------' % cat
	li = xbmcgui.ListItem(name, iconImage = '', thumbnailImage = '')
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), '', li, False)

def ListChannels():
	for i in range(0, len(clist)):
		channelEnabled = Enabled(i)
		if showDisabled or channelEnabled:
			if i > 0 and clist[i]["c"] != clist[i-1]["c"]:
				AddSeparator(categories[int(clist[i]["c"])-1]["name"])
			for n in range(0, len(clist[i]["s"])):
				AddItem(i, n)