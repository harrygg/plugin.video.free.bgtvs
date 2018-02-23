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
from kodibgcommon.utils import *

if settings.use_local_db and settings.db_file_path != '' and os.path.isfile(settings.db_file_path):
  db_file = settings.db_file_path
else:
  db_file = os.path.join( get_profile_dir(), 'tv.db' )
backup_db_file = os.path.join( get_resources_dir() , 'tv.db' )

def show_categories():
  update('browse', 'Categories')
  if not settings.use_local_db:
    asset = Assets(db_file, backup_db_file)
    if asset.is_old():
      asset.update(settings.url_db)
  log("Loading data from DB file: %s" % db_file)
  
  try:
    conn = sqlite3.connect(db_file)
    cursor = conn.execute('''SELECT * FROM categories''')
    
    li = xbmcgui.ListItem('Всички')
    url = make_url({"id": 0, "action": "show_channels"})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)

    #Add categories
    for row in cursor:
      li = xbmcgui.ListItem(row[1])
      url = make_url({"id": row[0], "action": "show_channels"})
      xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)  
     
  except Exception as er:
    log(er, xbmc.LOGERROR)
    show_notification(str(er), True)
  
  if not settings.use_local_db:
    li = xbmcgui.ListItem('******** Обнови базата данни ********')
    url = make_url({"action": "update_tvdb"})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li)
    
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

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
      url = c.playpath
    else:
      url_items = {"id": c.id, "action": "show_streams"}
      url = make_url(url_items)
    
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, False) 

def get_channels(id):
  log("Getting channel with id: %s" % id)
  channels = []
  try:
    conn = sqlite3.connect(db_file)
    sign = "="
    no_radio_rule = ""
    if id == str(0):
      sign = "<>"
      no_radio_rule = "AND c.category_id <> 7"
    
    disabled_query = '''AND s.disabled = 0''' if not settings.show_disabled else ''

    query = '''
    SELECT c.id, c.disabled, c.name, cat.name AS category, c.logo, COUNT(s.id) AS streams, s.stream_url, s.page_url, s.player_url, c.epg_id, u.string, c.ordering
    FROM channels AS c 
    JOIN streams AS s ON c.id = s.channel_id 
    JOIN categories as cat ON c.category_id = cat.id
    JOIN user_agents as u ON u.id = s.user_agent_id
    WHERE c.category_id %s %s %s %s
    GROUP BY c.id, c.name 
    ORDER BY c.ordering''' % (sign, id, no_radio_rule, disabled_query)
    cursor = conn.execute(query)
    
    for row in cursor:
      c = Channel(row)
      channels.append(c)
      
  except Exception, er:
    log('get_channels() %s: %s ' % (str(er), xbmc.LOGERROR))
    show_notification(str(er), True)
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
  log('resolved url %s' % url)
  item = xbmcgui.ListItem(path=url)
  item.setInfo( type = "Video", infoLabels = { "Title" : ''} )
  item.setProperty("IsPlayable", str(True))
  xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded=True, listitem=item)
  
def get_streams(id):
  streams = []
  try:
    conn = sqlite3.connect(db_file)
    query = '''SELECT s.*, u.string AS user_agent FROM streams AS s JOIN user_agents as u ON s.user_agent_id==u.id WHERE channel_id=%s''' % id
    if not settings.show_disabled:
     query += ''' AND s.disabled=0''' 
    cursor = conn.execute(query)
    
    for row in cursor:
      c = Stream(row)
      streams.append(c)
  except Exception, er:
    log(str(er), xbmc.LOGERROR)
    show_notification(str(er), True)
  return streams  

def play_channel(channel_id, stream_index = 0):
  urls = get_streams(id)
  s = urls[stream_index]
  li = xbmcgui.ListItem(s.name, iconImage=s.logo, thumbnailImage=s.logo, path=s.stream_url)
  li.setInfo( type = "Video", infoLabels = { "Title" : s.name } )
  li.setProperty("IsPlayable", 'True')
  xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
  
def update(name, location, crash=None):
  lu = settings.last_update
  day = time.strftime("%d")
  if lu == "" or lu != day:
    import ga
    settings.last_update = day
    p = {}
    p['an'] = get_addon_name()
    p['av'] = get_addon_version()
    p['ec'] = 'Addon actions'
    p['ea'] = name
    p['ev'] = '1'
    p['ul'] = xbmc.getLanguage()
    p['cd'] = location
    ga.ga('UA-79422131-7').update(p, crash)

def update_tvdb():
  progress_bar = xbmcgui.DialogProgressBG()
  progress_bar.create(heading="Downloading database...")
  msg = "Базата данни НЕ бе обновена!"
  try:
    log('Force-updating tvdb')
    # recreated the db_file in case db_file is overwritten by use_local_db
    __db_file__ = os.path.join( get_resources_dir(), 'tv.db' )
    asset = Assets( __db_file__, backup_db_file )
    progress_bar.update(1, "Downloading database...")
    res = asset.update(settings.url_db)
    if res:
      msg = "Базата данни бе обновена успешно!"
    if settings.use_local_db:
      msg += " Използвате локална база данни!"

  except Exception as ex:
    log(ex, 4)
    show_notification(ex, True)
  
  show_notification(msg, not res)
  
  if progress_bar:
    progress_bar.close()

def show_notification(msg, is_error=False, time=3000):
  title = "Грешка" if is_error else "Успех"
  command = "Notification(%s,%s,%s)" % (title, str(msg).encode('utf-8'), time)
  xbmc.executebuiltin(command)  

