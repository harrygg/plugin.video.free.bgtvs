import os
import sys
import time
import xbmc
import sqlite3
import xbmcgui
import traceback
import xbmcaddon
import xbmcplugin
from assets import Assets
from playlist import *
from ga import ga

__DEBUG__ = False
if __DEBUG__:
  sys.path.append(os.environ['PYSRC'])
  import pydevd
  pydevd.settrace('localhost', stdoutToServer=False, stderrToServer=False)

def log(msg, level=xbmc.LOGDEBUG):
  if settings.debug and level == xbmc.LOGDEBUG:
    level = xbmc.LOGNOTICE
    try:
      xbmc.log('%s | %s' % (__addon_id__, msg.encode('utf-8')), level)
    except Exception as e:
      try: xbmc.log('Logging Failure: %s' % (e), level)
      except: pass
            
def show_categories():
  update('browse', 'Categories')
  cats = []
  try:
    conn = sqlite3.connect(__db__)
    cursor = conn.execute('''SELECT * FROM categories''')
    
    li = xbmcgui.ListItem('Всички')
    url = "%s?id=0&mode=show_channels" % sys.argv[0]
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)

    #Add categories
    for row in cursor:
      li = xbmcgui.ListItem(row[1])
      url = "%s?id=%s&mode=show_channels" % (sys.argv[0], row[0])
      xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)

    li = xbmcgui.ListItem('******** Обнови базата данни ********')
    url = "%s?mode=update_tvdb" % sys.argv[0]
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li)     
     
  except Exception, er:
    log(str(er), xbmc.LOGERROR)
  return cats

def show_channels(id):
  channels = get_channels(id)
  for c in channels:      
    if c.disabled:
      c.name = '[COLOR brown]%s[/COLOR]' % c.name
    playable = c.streams == 1 and c.playpath != ''
    li = xbmcgui.ListItem(c.name, iconImage = c.logo, thumbnailImage = c.logo)
    li.setInfo( type = "Video", infoLabels = { "Title" : c.name } )
    li.setProperty("IsPlayable", str(playable))
    # self.playable = False if self.streams > 1 or self.player_url != '' else True

    if playable:
      u = c.playpath
    else:
      u = "%s?id=%s&mode=show_streams" % (sys.argv[0], c.id)
    
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, li, False) 

def get_channels(id):
  xbmc.log("Getting channel with id: " + id)
  channels = []
  try:
    conn = sqlite3.connect(__db__)
    sign = "="
    no_radio_rule = ""
    if id == str(0):
      sign = "<>"
      no_radio_rule = "AND c.category_id <> 7"
      
    q = '''
    SELECT c.id, c.disabled, c.name, cat.name AS category, c.logo, COUNT(s.id) AS streams, s.stream_url, s.page_url, s.player_url, c.epg_id, u.string, c.ordering
    FROM channels AS c 
    JOIN streams AS s ON c.id = s.channel_id 
    JOIN categories as cat ON c.category_id = cat.id
    JOIN user_agents as u ON u.id = s.user_agent_id
    WHERE c.category_id %s %s %s %s
    GROUP BY c.id, c.name 
    ORDER BY c.ordering''' % (sign, id, no_radio_rule, __disabled_query__)
    cursor = conn.execute(q)
    
    for row in cursor:
      c = Channel(row)
      channels.append(c)
  except Exception, er:
    log('get_channels() %s: %s ' % (str(er), xbmc.LOGERROR))
  return channels

def show_streams(id):
  streams = get_streams(id)
  select = 0
  if len(streams) > 1:
    dialog = xbmcgui.Dialog()
    select = dialog.select('Изберете стрийм', [s.comment for s in streams])
    if select == -1: 
      return False
  url = streams[select].url
  log('FreeBGTvs resolved url %s' % url)
  item = xbmcgui.ListItem(path=url)
  item.setInfo( type = "Video", infoLabels = { "Title" : ''} )
  item.setProperty("IsPlayable", str(True))
  xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded=True, listitem=item)
  
def get_streams(id):
  streams = []
  try:
    conn = sqlite3.connect(__db__)
    cursor = conn.execute('''SELECT s.*, u.string AS user_agent FROM streams AS s JOIN user_agents as u ON s.user_agent_id == u.id WHERE channel_id = %s %s''' %  (id, __disabled_query__))
    for row in cursor:
      c = Stream(row)
      streams.append(c)
  except Exception, er:
    log(str(er), xbmc.LOGERROR)
  return streams  

def play_channel(channel_id, stream_index = 0):
  urls = get_streams(id)
  s = urls[stream_index]
  li = xbmcgui.ListItem(s.name, iconImage = s.logo, thumbnailImage = s.logo, path=s.stream_url)
  li.setInfo( type = "Video", infoLabels = { "Title" : s.name } )
  li.setProperty("IsPlayable", 'True')
  xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
  
def get_params():
  param = {}
  paramstring = sys.argv[2]
  if len(paramstring) >= 2:
    params = sys.argv[2]
    cleanedparams = params.replace('?','')
    if (params[len(params)-1] == '/'):
      params = params[0:len(params) - 2]
    pairsofparams = cleanedparams.split('&')
    for i in range(len(pairsofparams)):
      splitparams = {}
      splitparams = pairsofparams[i].split('=')
      if (len(splitparams)) == 2:
        param[splitparams[0]] = splitparams[1]
  return param
  
def update(name, location, crash=None):
  lu = __addon__.getSetting('last_update')
  day = time.strftime("%d")
  if lu == "" or lu != day:
    __addon__.setSetting('last_update', day)
    p = {}
    p['an'] = __addon__.getAddonInfo('name')
    p['av'] = __addon__.getAddonInfo('version')
    p['ec'] = 'Addon actions'
    p['ea'] = name
    p['ev'] = '1'
    p['ul'] = xbmc.getLanguage()
    p['cd'] = location
    ga('UA-79422131-7').update(p, crash)

def update_tvdb():
  progress_bar = xbmcgui.DialogProgressBG()
  progress_bar.create(heading="Downloading database.")
  msg1 = "Грешка"
  msg2 = "Базата данни НЕ бе обновена!".encode('utf-8')
  try:
    log('Force-updating tvdb', 2)
    a = Assets(__working_dir__, __url__, __backup_db__)
    log('a')
    progress_bar.update(1, "Downloading database...")
    if a.update(True):
      msg1 = "Успех"
      msg2 = "Базата данни бе обновена успешно!".encode('utf-8')

    if settings.is_local_db:
      msg2 += " Използвате локална база данни!".encode('utf-8')

  except Exception as ex:
    log(str(ex), 4)
    
  command = "Notification(%s,%s,%s)" % (msg1, msg2, 2000)
  xbmc.executebuiltin(command)
  
  if progress_bar:
    progress_bar.close()

class Settings():

  def __getattr__(self, name):
    temp = __addon__.getSetting(name)
    if temp in ['true', 'True']:
      return True
    if temp in ['false', 'False']:
      return False
    if temp.isdigit():
      return int(temp)
    return temp

  def __setattr__(self, name, value):
    __addon__.setSetting(name, str(value))

settings = Settings()

__addon_id__ = 'plugin.video.free.bgtvs'
__addon__ = xbmcaddon.Addon(id=__addon_id__)
__working_dir__ = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__disabled_query__ = '''AND s.disabled = 0''' if settings.show_disabled == False else ''
__cwd__ = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode('utf-8')
__backup_db__ = xbmc.translatePath(os.path.join( __cwd__, 'resources', 'tv.db' ))
__url__ = 'http://github.com/harrygg/plugin.program.freebgtvs/raw/master/resources/tv.db'

###
if settings.is_local_db and settings.db_file_path != '' and os.path.isfile(settings.db_file_path):
  __db__ = settings.db_file_path
  log("Using local DB file %s" % settings.db_file_path)
else:
  a = Assets(__working_dir__, __url__, __backup_db__, True)
  __db__ = a.file