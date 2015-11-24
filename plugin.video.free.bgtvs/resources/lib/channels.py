# -*- coding: utf-8 -*-
import urllib2, re, xbmc, sys
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
		
channels = []
channel = {}
bnt_hash = ''
bnt_channels = []

def getBntHash():
	global bnt_hash
	response = _Request('http://tv.bnt.bg/bnt1/16x9/')
	matches = re.compile('iframe.*src[\s=\"]*(.*?)["\'\s]+', re.DOTALL).findall(response)
	if len(matches) > 0:
		response = _Request(matches[0])
		matches = re.compile('stream\?at=(.*?)[\s"\']+').findall(response)
		if len(matches) > 0:
			bnt_hash = matches[0]
			return matches[0]

def _Request(url):
	req = urllib2.Request(url)
	req.add_header('Referer', 'http://bnt.bg')
	res = urllib2.urlopen(req)
	response = res.read()
	res.close()
	return response

class Channel:
	token = ''
	tcUrl = ''
	playlist = ''
	pageUrl = ''
	app = ''
	swfUrl = ''
	live = 'true'
	playpath = ''
	name = ''
	url = ''
	icon = ''
	url = ''
	
	def __init__(self, cname, cUrl = '', cIcon = ''):
		self.name = cname
		if 'БНТ' in cname and bnt_hash == '':
			getBntHash()
		if cUrl != '':
			self.url = cUrl
		if cIcon != '':
			self.icon = cIcon
			
	def toString(self):
		if self.playpath.find('?at') > -1:
			self.playpath += bnt_hash
		if self.playlist.find('?at') > -1:
			self.playlist += bnt_hash
		if self.playpath != '':
			return '%s pageUrl=%s app=%s playpath=%s token=%s swfUrl=%s live=%s' % (self.tcUrl, self.pageUrl, self.app, self.playpath, self.token, self.swfUrl, self.live)
		else:
			return self.playlist

c = Channel('БНТ 1')
c.icon = 'http://cdn.bg/images/www/bnt/16x9-BNT1.png'
c.tcUrl = 'rtmp://edge3.evolink.net:2020/fls'
c.pageUrl = 'http://cdn.bg/live/'
c.app = 'fls'
c.swfUrl = 'http://cdn.bg/eflash/jwplayer510/player.swf'
c. token = 'B@1R1st1077'
c.playpath = 'bnt.stream?at='
bnt_channels.append(c)

c = Channel('БНТ 2')
c.icon = 'http://cdn.bg/images/www/bnt/16x9-BNT2.png'
c.tcUrl = 'rtmp://edge3.evolink.net:2020/fls'
c.pageUrl = 'http://cdn.bg/live/'
c.app = 'fls'
c.swfUrl = 'http://cdn.bg/eflash/jwplayer510/player.swf'
c. token = 'B@1R1st1077'
c.playpath = 'bnt2.stream?at='
bnt_channels.append(c)

c = Channel('БНТ Свят')
c.icon = 'http://tv.bnt.bg/img/menu/logoBNTworld.png'
c.tcUrl = 'rtmp://193.43.26.198:1935/live/bntsat'
c.swfUrl = 'http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
c.app = 'live/'
c.playpath = 'bntsat'
c.pageUrl = 'http://tv.bnt.bg/bntworld/'
bnt_channels.append(c)

c = Channel('БНТ HD')
c.icon = 'http://i.cdn.bg/images/www/bnt/BNTliveHD.png'
c.playlist = 'http://ios.cdn.bg:2020/fls/bntHDt.stream/playlist.m3u8?at='
bnt_channels.append(c)

c = Channel('bTV')
c.icon = 'http://www.btv.bg//static/bg/microsites/btv/img/btv-logo.png'
c.url = 'rtmp://46.10.150.111:80/ios playpath=btvbglive pageURL=http://www.btv.bg/live/ app=ios swfUrl=http://images.btv.bg/fplayer/flowplayer.commercial-3.2.5.swf live=true'
channels.append(c)

c = Channel('Нова')
c.icon = 'http://static1.novatv.bg/layout/novatv/images/big_nav_logo.png'
c.url = 'rtmp://edge1.evolink.net:2010/fls playpath=ntv_2.stream pageURL=http://i.cdn.bg/live/ app=fls/_definst_ token=N0v4TV6#2 live=true'
channels.append(c)

c = Channel('ТВ 7', 'http://tv7-hls-eu-perm-live.hls.adaptive.level3.net/tv7live.m3u8', 'http://tv7.bg/img/public/logoTv7.png')
channels.append(c)

c = Channel('Bulgaria On Air', 'http://ios.cdn.bg:2006/fls/bonair.stream/playlist.m3u8', 'http://www.bgonair.bg/media/template/default/img/ico/logo.png')
channels.append(c)

c = Channel('BloombergTV Bulgaria', 'http://ios.cdn.bg:2091/fls/bloomberg.stream/playlist.m3u8', 'http://www.bgonair.bg/media/files/article/640x360/720/7208ce5c53416420f10143fdb6c26a6c.jpeg')
channels.append(c)

c = Channel('News 7', 'http://tv7-hls-eu-perm-live.hls.adaptive.level3.net/news7live.m3u8', 'http://news7.bg/img/news7/logoNews7.png')
channels.append(c)

c = Channel('Канал 3', 'http://ios.cdn.bg:2017/fls/kanal3.stream/playlist.m3u8', 'http://kanal3.bg/assets/css/images/logo.png')
channels.append(c)

c = Channel('Евроком', 'rtmp://live.eurocom.bg:1935/live/ swfUrl=http://eurocom.bg/js/jwplayer/jwplayer.flash.swf pageUrl=http://eurocom.bg/live playpath=stream live=true')
channels.append(c)

c = Channel('City TV', 'http://nodeb.gocaster.net:1935/CGL/_definst_/mp4:TODAYFM_TEST2/playlist.m3u8', 'http://city.bg/themes/city/images/city-web.png')
channels.append(c)

c = Channel('The Voice', 'rtmp://31.13.217.76/rtplive app=rtplive playpath=thevoice_live.stream pageUrl=http://thevoice.bg/stream/ swfUrl=http://thevoice.bg/js/thevoice_videostreem.swf live=true', 'http://s.thevoice.bg/img/logo.png')
channels.append(c)

c = Channel('Magic TV', 'rtmp://31.13.217.76:1935/magictv app=magictv playpath=magictv_live.stream pageUrl=http://thevoice.bg/stream/ swfUrl=http://thevoice.bg/js/thevoice_videostreem.swf live=true', 'http://www.magictv.bg/web/img/logo.png')
channels.append(c)

c = Channel('Агро ТВ', 'rtmp://agrotvlive1.srfms.com:3021/live/ pageUrl=http://www.agrotv.bg/  app=live/ playpath=livestream swfUrl=http://www.agrotv.bg/flowplayer/flowplayer.rtmp-3.2.3.swf live=true', 'http://www.agrotv.bg/images/logo.png')
channels.append(c)

c = Channel('ТВ Черно Море Варна', 'http://ios.cdn.bg:2006/fls/chmore.stream/playlist.m3u8', 'http://www.chernomore.bg/media/template/default/img/img/logo.png')
channels.append(c)

c = Channel('Стойчев ТВ Стара Загора', 'http://ios.cdn.bg:2015/fls/tvstoichev.stream/playlist.m3u8')
channels.append(c)

c = Channel('ТВ Стара Загора', 'http://95.87.0.78:8080/tvstz.m3u8', 'http://tvstz.com/images/logo_TVSTZ.png')
channels.append(c)

c = Channel('Канал 6 Сливен', 'http://84.54.139.86:91', 'http://kanal6.bg/images/sampledata/parks/Kanal-6-logo-mini.png')
channels.append(c)

c = Channel('Римекс ТВ Враца', 'http://transcoder1.bitcare.eu:5516/flv/rimextv.flv', 'http://tv.rimex-ltd.com/wp-content/themes/RimexTV-MI/images/logo.png')
channels.append(c)

c = Channel('ТВ Микс Бургас', 'http://109.160.31.20:8090/tvmix_big.flv', 'http://www.tvmix.bg/wp-content/themes/shine/images/bg2.jpg')
channels.append(c)

c = Channel('Арт ТВ', 'http://80.72.95.9:1935/live/tvart/playlist.m3u8')
channels.append(c)

c = Channel('Алфа', 'rtmp://ataka.tv/live app=live swfUrl=http://www.ataka.tv/flash/flowplayer.commercial-3.2.7.swf pageURL=http://www.ataka.tv/ playpath=live', 'http://www.ataka.tv/images/logo_alfa.jpg')
channels.append(c)

c = Channel('Национално-патриотична телевизия', 'mms://bnptv.tv:10801', 'http://www.bnptv.info/tv/templates/rhuk_milkyway/images/mw_joomla_logo.png')
channels.append(c)

#c = Channel('DSTV', 'rtmp://46.249.95.140:1935/live app=live playpath=livestream pageUrl=http://dstv-bg.com/ swfUrl=http://fpdownload.adobe.com/strobe/FlashMediaPlayback.swf/[[DYNAMIC]]/1', 'http://dstv-bg.com/wp-content/uploads/2013/08/dstv-malko-Logogg.png')
#channels.append(c)

#c = Channel('Вест ТВ', 'rtmpe://31.13.223.103/vtv app=vtv playpath=vtv pageURL=player.neterra.net/vtv/player.php swfUrl=http://player.neterra.net/vtv/flowplayer/flowplayer.securestreaming-3.2.9.swf token=qqasw23evtv', 'http://vtv.bg/images/logo.gif')
#channels.append(c)

#Eвроком Царевец

#Кис 13 src=rtmp%3A%2F%2F109.160.96.230%2Flive%2FmyStream&streamType=live
#c = Channel('Кис 13', 'rtmp://109.160.96.230/myStream&streamType=live app=live swfUrl=http://109.160.96.230/StrobeMediaPlayback.swf pageURL=http://kiss13.net/live.html playpath=live', 'http://kiss13.net/templates/street_tv/images/style5/logo.png')


