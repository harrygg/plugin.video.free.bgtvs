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

def show_categories():
	cats = []
	try:
		conn = sqlite3.connect(local_db)
		cursor = conn.execute('''SELECT * FROM categories''')
		
		li = xbmcgui.ListItem('Всички')
		url = "%s?id=0&mode=show_channels" % sys.argv[0]
		xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)

		#Add categories
		for row in cursor:
			li = xbmcgui.ListItem(row[1])
			url = "%s?id=%s&mode=show_channels" % (sys.argv[0], row[0])
			xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)
			
	except Exception, er:
		xbmc.log(str(er), xbmc.LOGERROR)
	return cats

def show_channels(id):
	
	for c in get_channels(id):			
		li = xbmcgui.ListItem(c.name, iconImage = c.logo, thumbnailImage = c.logo)
		li.setInfo( type = "Video", infoLabels = { "Title" : c.name } )
		li.setProperty("IsPlayable", str(c.playable))
	
		if c.playable:
			u = c.stream_url
		else:
			u = "%s?id=%s&mode=show_streams" % (sys.argv[0], c.id)
		
		xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, li, False)	

def get_channels(id):
	channels = []
	try:
		conn = sqlite3.connect(local_db)
		sign = '<>' if id == str(0) else '='
		q = '''
		SELECT c.id, c.disabled, c.name, cat.name AS category, c.logo, COUNT(s.id) AS streams, s.stream_url, s.page_url, s.player_url 
		FROM channels AS c 
		JOIN streams AS s ON c.id = s.channel_id 
		JOIN categories as cat ON c.category_id = cat.id 
		WHERE c.category_id %s %s %s
		GROUP BY c.id, c.name 
		ORDER BY c.name''' % (sign, id, disabled_query)
		xbmc.log(q)
		cursor = conn.execute(q)
		
		for row in cursor:
			c = Channel(row)
			channels.append(c)
	except Exception, er:
		xbmc.log('get_channels() ' + str(er), xbmc.LOGERROR)
	return channels

def show_streams(id):
	streams = get_streams(id)
	dialog = xbmcgui.Dialog()
	select = dialog.select('Изберете стрийм', [s.name for s in streams])
	if select == -1: 
		return False
	else:
		url = streams[select].stream_url
		xbmc.log(url)
		item = xbmcgui.ListItem(path=url)
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded=True, listitem=item)
	
def get_streams(id):
	streams = []
	try:
		conn = sqlite3.connect(local_db)
		cursor = conn.execute('''
		SELECT s.stream_url, s.page_url, s.player_url, s.disabled, c.name ||' '|| s.comment, c.logo
		FROM streams AS s 
		JOIN channels AS c 
		ON s.channel_id = c.id 
		WHERE c.id = %s %s''' % (id, disabled_query))

		for row in cursor:
			c = Stream(row)
			
			streams.append(c)
	except Exception, er:
		xbmc.log(str(er), xbmc.LOGERROR)
	return streams	

def play_channel(channel_id, stream_index = 0):
	urls = get_streams(id)
	s = urls[stream_index]
	li = xbmcgui.ListItem(s.name, iconImage = s.logo, thumbnailImage = s.logo, path=s.stream_url)
	li.setInfo( type = "Video", infoLabels = { "Title" : s.name } )
	li.setProperty("IsPlayable", 'True')
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

class Category:
	def __init__(self, id, title):
		self.id = id
		self.title = title

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
		if self.disabled:
			self.name = '[COLOR brown]%s[/COLOR]' % self.name
			
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
		if self.disabled:
			self.name = '[COLOR brown]%s[/COLOR]' % self.name
		
	def resolve(self):
		if '3583019' in self.player_url: #BiT
			return self._livestream()
		
		res = request(self.player_url, self.page_url)
		#m = re.compile('video.+src[=\s"\']+(.+?)[\s"\']+', re.DOTALL).findall(res)
		#if len(m) == 0:
		m = re.compile('(http.*m3u.*?)[\'"]+').findall(res)
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
disabled_query = '''AND c.disabled = 0''' if show_disabled == False else ''
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