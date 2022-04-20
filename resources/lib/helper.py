import os
import sys
import time
import xbmc
import sqlite3
import xbmcgui
import xbmcplugin
from .assets import Assets
from .playlist import *
from kodibgcommon.settings import settings
from kodibgcommon.utils import get_profile_dir, get_resources_dir, make_url, get_addon_name, get_addon_version
from kodibgcommon.logging import log_info, log_error
       
#append_pydev_remote_debugger
if False:
    sys.path.append(os.environ["PYSRC"])
    sys.stdout = open(os.path.join(os.environ['TEMP'], 'stdout.txt'), 'w')
    sys.stderr = open(os.path.join(os.environ['TEMP'], 'stderr.txt'), 'w')
    import pydevd
    pydevd.settrace('127.0.0.1', stdoutToServer=False, stderrToServer=False)
#end_append_pydev_remote_debugger	

if settings.use_local_db and settings.db_file_path != '' and os.path.isfile(settings.db_file_path):
  db_file = settings.db_file_path
else:
  db_file = os.path.join( get_profile_dir(), 'tvs.db' )
backup_db_file = os.path.join( get_resources_dir() , 'tvs.db' )

def show_categories():
  update('browse', 'Categories')
  if not settings.use_local_db:
    asset = Assets(db_file, backup_db_file)
    if asset.is_old():
      asset.update(settings.url_to_db)
  log_info("Loading data from DB file: %s" % db_file)
  
  try:
    conn = sqlite3.connect(db_file)
    cursor = conn.execute('''SELECT * FROM freetvandradio_category''')
    
    li = xbmcgui.ListItem('Всички')
    url = make_url({"id": 0, "action": "show_channels"})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)

    #Add categories
    for row in cursor:
      li = xbmcgui.ListItem(row[1])
      url = make_url({"id": row[0], "action": "show_channels"})
      xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)  
     
  except Exception as er:
    log_error(er)
    show_notification(str(er), True)
  
  if not settings.use_local_db:
    li = xbmcgui.ListItem('******** Обнови базата данни ********')
    url = make_url({"action": "update_tvdb"})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li)
    
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def show_channels(id):
  
  channels = get_channels(id)
  
  for c in channels:
    if not c.enabled and not settings.show_only_enabled:
      c.name = '[COLOR brown]%s[/COLOR]' % c.name
    li = xbmcgui.ListItem(c.name)
    li.setInfo( type = "Video", infoLabels = { "Title" : c.name } )
    li.setProperty("IsPlayable", str(False))

    url_items = {"id": c.id, "action": "show_streams"}
    url = make_url(url_items)
    
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, False) 

def get_channels(category_id):
  '''
  '''
  channels = []
  log_info("Getting channel for category id: %s" % category_id)
  
  #try:
  conn = sqlite3.connect(db_file)
  query = '''SELECT channel_id FROM freetvandradio_channel_category AS cc ''' 
  
  # if we are showing all channels, that is category_id is 0 and show radios is disabled
  if int(category_id) > 0:
    query += "WHERE cc.category_id = %s;" % category_id
  
  # all results in a list
  conn.row_factory = lambda cursor, row: row[0]
  c = conn.cursor()
  ids = c.execute(query).fetchall()
  ids = ','.join(str(id) for id in ids)

  query_get_only_enabled = '''AND ch.enabled = 1''' if settings.show_only_enabled else ''
  query = '''SELECT ch.id, ch.name, ch.logo, ch.ordering, ch.enabled FROM freetvandradio_channel AS ch WHERE ch.id IN (%s) %s GROUP BY ch.id ORDER BY ch.ordering''' % (ids, query_get_only_enabled)
  conn.row_factory = lambda cursor, row: Channel(row)
  c = conn.cursor()
  channels = c.execute(query).fetchall()
  xbmc.log("Extracted %s channels" % len(channels), xbmc.LOGERROR)
  
  #except Exception as er:
  #log('Error in get_channels(): %s' % str(er), xbmc.LOGERROR)
  #show_notification(str(er), True)
  return channels

def show_streams(channel_id):
  
  streams = get_streams(channel_id)
  select = 0
  if len(streams) > 1:
    dialog = xbmcgui.Dialog()
    select = dialog.select('Изберете стрийм', [s.comment for s in streams])
    if select == -1: 
      return False
    
  url = streams[select].url
  log_info('resolved url: %s' % url)
  item = xbmcgui.ListItem(path=url)
  item.setInfo( type = "Video", infoLabels = { "Title" : ''} )
  item.setProperty("IsPlayable", str(True))
  xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded=True, listitem=item)
  
def get_streams(channel_id):
  '''
  '''
  streams = []
  
  conn = sqlite3.connect(db_file)
  query =  "SELECT s.id, s.channel_id, s.stream_url, s.page_url, s.player_url, s.enabled, s.comment, "
  query += "u.string AS user_agent "
  query += "FROM freetvandradio_stream AS s "
  query += "JOIN freetvandradio_user_agent as u ON s.user_agent_id==u.id "
  query += "WHERE channel_id=%s" % channel_id
  
  if settings.show_only_enabled:
    query += " AND s.enabled=1"
    
  conn.row_factory = lambda cursor, row: Stream(row)
  c = conn.cursor()
  streams = c.execute(query).fetchall()
    
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
    from ga import ga
    settings.last_update = day
    p = {}
    p['an'] = get_addon_name()
    p['av'] = get_addon_version()
    p['ec'] = 'Addon actions'
    p['ea'] = name
    p['ev'] = '1'
    p['ul'] = xbmc.getLanguage()
    p['cd'] = location
    ga('UA-79422131-7').update(p, crash)

def update_tvdb():
  progress_bar = xbmcgui.DialogProgressBG()
  progress_bar.create(heading="Downloading database...")
  msg = "Базата данни НЕ бе обновена!"
  try:
    log_info('Force-updating tvdb')
    # recreated the db_file in case db_file is overwritten by use_local_db
    __db_file__ = os.path.join( get_resources_dir(), 'tvs.sqlite3' )
    asset = Assets( __db_file__, backup_db_file )
    progress_bar.update(1, "Downloading database...")
    res = asset.update(settings.url_to_db)
    if res:
      msg = "Базата данни бе обновена успешно!"
    if settings.use_local_db:
      msg += " Използвате локална база данни!"

  except Exception as ex:
    log_error(ex)
    show_notification(ex, True)
  
  show_notification(msg, not res)
  
  if progress_bar:
    progress_bar.close()
  
def show_notification(msg, is_error=False, time=3000):
  title = "Грешка" if is_error else "Успех"
  command = "Notification(%s,%s,%s)" % (title, msg, time)
  xbmc.executebuiltin(command)  

