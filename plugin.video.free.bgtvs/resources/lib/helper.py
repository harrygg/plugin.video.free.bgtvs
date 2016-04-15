import sys, os, xbmc, xbmcgui, xbmcaddon, xbmcplugin, gzip, sqlite3, urllib, urllib2, re, json
from datetime import datetime, timedelta

def download_assets():
	try:
		remote_db = 'http://rawgit.com/harrygg/%s/master/%s/resources/storage/tv.db.gz?raw=true' % (id, id)
		xbmc.log('Downloading assets from url: %s' % remote_db)
		save_to_file = local_db if '.gz' not in remote_db else local_db + ".gz"
		f = urllib2.urlopen(remote_db)
		if not os.path.exists(os.path.dirname(save_to_file)):
			create_dir(save_to_file)
		with open(save_to_file, "wb") as code:
			code.write(f.read())
		extract(save_to_file)
	except Exception, er:
		xbmc.log(str(er), xbmc.LOGERROR)
		raise

def create_dir(path):
	try: os.makedirs(os.path.dirname(path))
	except OSError as exc: # Guard against race condition
		if exc.errno != errno.EEXIST:
			raise
			
def extract(path):
	try:
		gz = gzip.GzipFile(path, 'rb')
		s = gz.read()
		gz.close()
		out = file(local_db, 'wb')
		out.write(s)
		out.close()
	except:
		raise

		
def show_channels():
	for c in get_channels():
		if show_disabled or not c.disabled:
			name = c.name
			if c.disabled:
				name = '[COLOR brown]' + name + '[/COLOR]'
			li = xbmcgui.ListItem(name, iconImage = c.logo, thumbnailImage = c.logo)
			li.setInfo( type = "Video", infoLabels = { "Title" : c.name } )
			li.setProperty("IsPlayable", str(c.playable))
			if c.playable:
				u = c.stream_url
				is_dir = False
			else:
				u = "%s?id=%s&mode=show_streams" % (sys.argv[0], c.id)
				is_dir = True
			xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, li, is_dir)	
			
			
def get_channels():
	channels = []
	try:
		conn = sqlite3.connect(local_db)
		cursor = conn.execute('''
		SELECT c.id, c.disabled, c.name, cat.name AS category, c.logo, COUNT(s.id) AS streams, 
		s.stream_url, s.page_url, s.player_url FROM channels AS c 
		JOIN streams AS s ON c.id == s.channel_id 
		JOIN categories as cat ON c.category_id == cat.id 
		GROUP BY c.id, c.name''')
		
		for row in cursor:
			c = Channel(row)
			channels.append(c)
	except Exception, er:
		xbmc.log(str(er), xbmc.LOGERROR)
	return channels

		
def show_streams(id):
	streams = get_streams(id)
	i = 1
	for s in streams:
		if show_disabled or not s.disabled:
			name = '%s (поток %s)' % (s.name, i) 
			if s.disabled:
				name = '[COLOR brown] %s [/COLOR]' % name
			li = xbmcgui.ListItem(name, iconImage = s.logo, thumbnailImage = s.logo)
			li.setInfo( type = "Video", infoLabels = { "Title" : s.name } )
			li.setProperty("IsPlayable", 'True')
			xbmcplugin.addDirectoryItem(int(sys.argv[1]), s.stream_url, li, False)
			i += 1	
	
def get_streams(id):
	streams = []
	try:
		conn = sqlite3.connect(local_db)
		cursor = conn.execute('''
		SELECT s.stream_url, s.page_url, s.player_url, s.disabled, c.name, c.logo 
		FROM streams AS s 
		JOIN channels AS c 
		ON s.channel_id = c.id 
		WHERE c.id = ?''', [id])

		for row in cursor:
			c = Stream(row)
			streams.append(c)
	except Exception, er:
		xbmc.log(str(er), xbmc.LOGERROR)
	return streams	

def play_channel(id):
	urls = get_streams(id)
	s = urls[0]
	li = xbmcgui.ListItem(s.name, iconImage = s.logo, thumbnailImage = s.logo, path=s.stream_url)
	li.setInfo( type = "Video", infoLabels = { "Title" : s.name } )
	li.setProperty("IsPlayable", 'True')
	#xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url, listitem, isFolder=False)
	xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
	
	
def get_params():
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
	
class Channel:
	def __init__(self, attr):
		self.id = attr[0]
		self.disabled = attr[1] == 1
		self.name = attr[2]
		self.category = attr[3]
		self.logo = attr[4]
		self.streams = attr[5]
		self.stream_url = attr[6] + '|User-Agent=%s' % ua
		self.page_url = '' if attr[7] == None else attr[7]
		self.player_url = '' if attr[8] == None else attr[8]
		self.playable = False if self.streams > 1 or self.player_url != '' else True

class Stream:
	def __init__(self, attr):
		self.stream_url = attr[0] 
		self.page_url = attr[1]
		self.player_url = attr[2]
		self.disabled = attr[3] == 1
		self.name = attr[4]
		self.logo = attr[5]
		if self.player_url != None and self.player_url != '':
			self.resolve()
		
	def resolve(self):
		if '3583019' in self.player_url: #BiT
			return self._livestream()
		
		res = request(self.player_url, self.page_url)
		m = re.compile('video.+src[=\s"\']+(.+?)[\s"\']+', re.DOTALL).findall(res)
		self.stream_url = '' if len(m) == 0 else m[0]
		#travelhd wrong stream name hack
		if 'playerCommunity' in self.player_url:
			self.stream_url.replace('/community/community', '/travel/community')	
		self.stream_url += '|User-Agent=%s' % ua
		
	def _livestream(self):
		res = request(self.player_url, self.page_url)
		m3u = ''
		try:
			json_res = json.loads(res)
			pl = json_res['stream_info']['m3u8_url']
			res = request(pl, self.player_url)	
			m = re.compile('(http.+av\-p\.m3u8.+)').findall(res)
			m3u = '%s|User-Agent=%s&Cookie=%s' % (m[0], ua, cookie)
		except Exception, er:
			xbmc.log(str(er), xbmc.LOGERROR)
		return m3u
		
def request(url, ref = ''):
	req = urllib2.Request(url)
	if ref == '': 
		ref = url
	xbmc.log("Request() | url=%s, ref=%s" % (url, ref))
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

clist = []
categories = []
id = 'plugin.video.free.bgtvs'
addon = xbmcaddon.Addon(id=id)
ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
show_disabled =  True if addon.getSetting('show_disabled') == "true" else False
local_db = os.path.join(profile, 'tv.db')
cookie = ''

try:
	if os.path.exists(local_db):
		treshold = datetime.now() - timedelta(hours=6)
		fileModified = datetime.fromtimestamp(os.path.getmtime(local_db))
		if fileModified < treshold: #file is more than a day old
			download_assets()
	else: #file does not exist, perhaps first run
			download_assets()
except Exception, er:
	xbmc.log(str(er), xbmc.LOGERROR)
	xbmc.executebuiltin('Notification(%s,%s,10000,%s)' % ('БГ Камерите','Неуспешно сваляне на най-новия списък с камери',''))
	assets = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../storage/tv.db.gz')
	extract(assets)