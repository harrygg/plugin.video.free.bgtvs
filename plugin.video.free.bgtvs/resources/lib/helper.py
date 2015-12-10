# -*- coding: utf-8 -*-
import urllib, urllib2, re, xbmc, sys, json, os
from xbmc import LOGERROR
# append pydev remote debugger
REMOTE_DBG = False
if REMOTE_DBG:
	try:
		sys.path.append("C:\\Software\\Java\\eclipse-luna\\plugins\\org.python.pydev_4.4.0.201510052309\\pysrc")
		import pydevd
		xbmc.log("After import pydevd")
		#import pysrc.pydevd as pydevd # with the addon script.module.pydevd, only use `import pydevd`
		# stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
		pydevd.settrace('localhost', stdoutToServer=False, stderrToServer=False, suspend=False)
	except ImportError:
		xbmc.log("Error: You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
		sys.exit(1)
	except:
		xbmc.log("Unexpected error:", sys.exc_info()[0]) 
		sys.exit(1)
		
clist = []

try:
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'channels.json')
    with open(filename) as data_file: 
        clist = json.load(data_file)['channels']
except Exception, er:
	xbmc.log("plugin.video.free.bgtvs | helper.py " + str(er), LOGERROR)
	pass            

def GetStream(i):
	s = ''
	try:
		if 'bnt' in clist[i]['id'] and 'world' not in clist[i]['id']: #if BNT channels, get the always changing hash
			hash = GetBntHash()
			s = clist[i]['url'] + hash
		elif 'bit' in clist[i]['id']: # Livestream
			s = GetLiveStream(clist[i]['url'])
		else: # else return the url
			s = clist[i]['url']
	except Exception, er:
		xbmc.log("plugin.video.free.bgtvs | GetStream() | Channel = " + clist[i]['id'] + " " + str(er), LOGERROR)
	return s

def GetBntHash():
	ref = 'http://bnt.bg'
	res = Request('http://tv.bnt.bg/bnt1/16x9/', ref)
	matches = re.compile('iframe.+src[\s=\"]+(.+?)["\'\s]+', re.DOTALL).findall(res)
	if len(matches) > 0:
		res = Request(matches[0], ref)
		m = re.compile('\?at=(.+?)[\s"\']+').findall(res)
		if len(m) > 0:
			return m[0]
	xbmc.log("plugin.video.free.bgtvs | GetBntHash() | Hash not found!", LOGERROR)
	return ''

ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
cookie = None

def Request(url, ref = ''):
	req = urllib2.Request(url)
	if ref == '': ref = url
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
	#except:
	#	xbmc.log("plugin.video.free.bgtvs | GetBiTStream() error")
	#	return ''

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

def GetIcon(c):
	if 'useIcon' in c.keys() and c['useIcon']:
		return c['icon']
	else:
		return "http://logos.kodibg.org/%s.png" % c['id']
#Eвроком Царевец

#Кис 13 src=rtmp%3A%2F%2F109.160.96.230%2Flive%2FmyStream&streamType=live
#c = Channel('Кис 13', 'rtmp://109.160.96.230/myStream&streamType=live app=live swfUrl=http://109.160.96.230/StrobeMediaPlayback.swf pageURL=http://kiss13.net/live.html playpath=live', 'http://kiss13.net/templates/street_tv/images/style5/logo.png')


