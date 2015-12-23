# -*- coding: utf-8 -*-
import urllib, urllib2, re, xbmc, sys, json, os, xbmcgui
from bs4 import BeautifulSoup

clist = []
id = 'plugin.video.free.bgtvs'
			
try:
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'channels.json')
    with open(filename) as data_file: 
        clist = json.load(data_file)['channels']
except:
	xbmcgui.Dialog().ok('Free BG TVs - channels.json error', 'Проблем със зареждането на списъка с каналите.')
	pass            

def GetStream(i):
	stream = ''
	if 'pageUrl' not in clist[i].keys():
		if clist[i]['id'] != 'separator':
			stream = clist[i]['url'][0]
	elif 'bit' in clist[i]['id']: # Livestream
		stream = GetLiveStream(clist[i]['url'][0])
	else: # else return the url
		stream = GetStreamFromSource(i)
	xbmc.log("%s | GetStream() returned %s" % (id, stream))
	return stream
	
def GetIframeUrl(i, ref):
	try:
		res = Request(clist[i]['pageUrl'], ref)
		bs = BeautifulSoup(res)
		return bs.iframe["src"]
	except:
		xbmc.log("%s | GetIframeUrl() failed!" % id)
		return ''

ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
cookie = None

def GetReferer(i): #Referer needed to prevent 403
		return clist[i]['pageUrl'] if 'referer' not in clist[i].keys() else clist[i]['referer']
		
def GetStreamFromSource(i):
	try:
		url = clist[i]['pageUrl'] if not GetProperty(i, 'getIframe') else GetIframeUrl(i, GetReferer(i))
		bs = BeautifulSoup(Request(url, ref))
		src = bs.video["src"]
		return src if 'travelhd' not in clist[i]['id'] else src.replace('/community/community', '/travel/community')
	except: 
		return clist[i]['url'][0]

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

def GetIcon(i):
	if clist[i]['id'] != 'separator':
		return clist[i]['customLogo'] if GetProperty(i, 'useCustomLogo') else "http://logos.kodibg.org/%s.png" % clist[i]['id']
	return 'Default.png'
	
def GetName(i):
	name = clist[i]['name'].encode('utf-8')
	if clist[i]['id'] != 'separator':
		name = "%s. %s" % (val.next(), name)
	return name

def GetNumber():
	for i in range(1, len(clist) + 1):
		yield i
		
val = GetNumber()

def GetProperty(i, prop):
	val = True if 'properties' in clist[i].keys() and prop in clist[i]['properties'] else False
	return val

def Enabled(i):
	return not GetProperty(i, "disabled")