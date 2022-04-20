# -*- coding: utf8 -*-
import os
import re
import time
import requests
from kodibgcommon.settings import settings
from kodibgcommon.logging import log_info, log_error

import importlib

class Playlist:
  name = 'playlist.m3u'
  channels = []
  raw_m3u = None
  append = True
  
  def __init__(self, name = ''):
    if name != '':
      self.name = name
  
  def save(self, path):
    '''
    '''
    file_path = os.path.join(path, self.name)
    log_info("Запазване на плейлистата: %s " % file_path)
    if os.path.exists(path):
      with open(file_path, 'w') as f:
        f.write(self.to_string().encode('utf-8', 'replace'))
  
  def concat(self, new_m3u, append = True, raw = True):
    '''
    '''
    if raw: #TODO implement parsing playlists
      self.append = append
      with open(new_m3u, 'r') as f:
        self.raw_m3u = f.read().replace('#EXTM3U', '')
  
  def to_string(self):
    '''
    '''
    output = ''
    for c in self.channels:
      output += c.to_string()
      
    if self.raw_m3u != None:
      if self.append:
        output += self.raw_m3u
      else:
        output = self.raw_m3u + output
    
    return '#EXTM3U\n' + output

class Category:
	def __init__(self, id, title):
		self.id = id
		self.title = title
    
class Channel:

  def __init__(self, attr):
    '''
    '''
    self.id = attr[0]
    self.name = attr[1]
    self.logo = attr[2]
    self.ordering = attr[3]
    self.enabled = attr[4] == 1
    #self.is_radio = 
    
  def to_string(self):
    '''
    '''
    output = '#EXTINF:-1 radio="False" tvg-shift=0 group-title="%s" tvg-logo="%s" tvg-id="%s",%s\n' % (self.category, self.logo, self.epg_id, self.name)
    output += '%s\n' % self.playpath
    return output 
 
class Stream:
  '''
  '''
  def __init__(self, attr):
    '''
    '''
    self.id = attr[0] 
    log_info("stream id=%s" % attr[0])
    self.channel_id = attr[1]
    log_info("channel_id=%s" % attr[1])
    self.url = attr[2]
    log_info("url=%s" % attr[2])
    self.page_url = attr[3]
    self.player_url = attr[4]
    self.enabled = attr[5] == 1
    self.comment = attr[6]
    self.user_agent = False if attr[7] == None else attr[7]
    if self.url == None or self.url == "":
      log_info("Resolving playpath url from %s" % self.player_url)
      self.url = self.resolve()
    if self.url is not None and self.user_agent: 
      self.url += '|User-Agent=%s' % self.user_agent
    if self.url is not None and self.page_url:
      self.url += '&Referer=%s' % self.page_url
    log_info("Stream final playpath: %s" % self.url)
    
  def resolve(self):
    stream = None
    s = requests.session()
    headers = {'User-agent': self.user_agent, 'Referer':self.page_url}
    
    # If btv - custom dirty fix to force login
    if self.channel_id == 2:
      body = { "username": settings.btv_username, "password": settings.btv_password }
      headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
      r = s.post("https://btvplus.bg/lbin/social/login.php", headers=headers, data=body)
      log_info(r.text)
      if r.json()["resp"] != "success":
        log_error("Проблем при вписването в сайта btv.bg")
        return None

    self.player_url = self.player_url.replace("{timestamp}", str(time.time() * 100))
    log_info(self.player_url)
    r = s.get(self.player_url, headers=headers)
    # log_info("body before replacing escape backslashes: " + r.text)
    body = r.text.replace('\\/', '/').replace("\\\"", "\"")
    # log_info("body after replacing escape backslashes: " + body)

    regex = '(//.*?\.m3u.*?)[\s\'"]{1}'
    log_info("Използван регулярен израз: %s" % regex)
    m = re.compile(regex).findall(body)
    if len(m) > 0:
      log_info('Намерени %s съвпадения в %s' % (len(m), self.player_url))
      if self.player_url.startswith("https"):
        stream = "https:" + m[0]
      elif self.player_url.startswith("http"):
        stream = "http:" + m[0]
      log_info('Извлечен видео поток %s' % stream)
    else:
      log_error("Не са намерени съвпадения за m3u")
      
    return stream
