# -*- coding: utf-8 -*-
import urllib, urllib2, re, xbmc, sys, json, os, xbmcgui
from xbmc import LOGERROR

clist = []

try:
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'channels.json')
    with open(filename) as data_file: 
        clist = json.load(data_file)['channels']
except Exception, er:
	xbmc.log("plugin.video.free.bgtvs | helper.py " + str(er), LOGERROR)
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
		stream = GetStreamFromPage(i)
	return stream
	
def GetIframeUrl(url, ref):
	res = Request(url, ref)
	m = re.compile('iframe.+src[=\s\'"]+(.+?)["\'\s]+', re.DOTALL).findall(res)
	if len(m) > 0: 
		return m[0]
	return ''

ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
cookie = None

def GetStreamFromPage(i):
	stream = ''
	ref = '' #Referer needed to prevent 403
	if 'referer' in clist[i].keys():
		ref = clist[i]['referer']
	else:
		ref = clist[i]['pageUrl']

	if 'getIframe' in clist[i].keys() and clist[i]['getIframe']:
		url = GetIframeUrl(clist[i]['pageUrl'], ref)
	else:
		url = clist[i]['pageUrl']
	
	xbmc.log("GetStreamFromPage: url=" + str(url) + ", ref=" + ref)
	
	res = Request(url, ref)
	m = re.compile('video.+src[\'"\s=]+(.+m3u8.+?)[\'"\s]+', re.DOTALL).findall(res)
	if len(m) > 0:
		xbmc.log("GetStreamFromPage: found video tag src=" + m[0])
		if 'travelhd' in clist[i]['id']: #traveltvhd wrong path in source fix
			stream = m[0].replace('/community/community', '/travel/community')
		else:
			stream = m[0]
	else: 
		stream = clist[i]['url'][0]
		
	return stream

def Request(url, ref = ''):
	req = urllib2.Request(url)
	if ref == '': ref = url
	xbmc.log("Request: url=" + url + ", ref=" + ref)
	req.add_header('Referer', ref)
	req.add_header('User-Agent', ua)
	res = urllib2.urlopen(req)
	global cookie
	cookie = res.info().getheader('Set-Cookie')
	if cookie != None:
		cookie = urllib.quote(cookie)
	response = res.read()
	res.close()
	return response

def GetLiveStream(url):
	response = Request(url)
	json_res = json.loads(response)
	pl = json_res['stream_info']['m3u8_url']
	response = Request(pl)	
	m = re.compile('(http.+av\-p\.m3u8.+)').findall(response)
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
		if 'useIcon' in clist[i].keys() and clist[i]['useIcon']:
			return clist[i]['icon']
		else:
			return "http://logos.kodibg.org/%s.png" % clist[i]['id']
	else:
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