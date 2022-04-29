# -*- coding: utf8 -*-
import os
import urllib.request, urllib.error, urllib.parse

class DbAsset:
  '''
  ''' 
  def __init__(self, **kwargs):
    self.file_path = kwargs.get('file_path')
    self._file_name = kwargs.get('file_name', 'tvs.sqlite3')
    self._temp_dir = kwargs.get('temp_dir')
    if not self.file_path:
      self.file_path = os.path.join(self._temp_dir, self._file_name)
    self._url = kwargs.get('url')
    self._log_delegate = kwargs.get('log_delegate')
    # temp_dir = os.path.dirname(os.path.realpath(db_file))
    # if not os.path.isdir(self.temp_dir):
    #   xbmcvfs.mkdir(self.temp_dir)
  
  def is_expired(self, interval_hours=24):
    '''
      Checks whether the asset file is older than the time interval in hours
      or that its older than the back_up file (in case of addon updates)
    '''
    try:
      from datetime import datetime, timedelta
      if os.path.isfile(self.file_path):
        treshold = datetime.now() - timedelta(hours=interval_hours)
        modified = datetime.fromtimestamp(os.path.getmtime(self.file_path))
        if modified < treshold: 
          return True
        return False
      else:
        return True
    except Exception as er:
      self.__log(er, 4)
      return True


  def update(self):
    '''
    Updates the local DB file
    '''
    temp_file_path = self.file_path + '_new'
    res = self.__download(self._url, temp_file_path)
    if res:
      try:
        if os.path.isfile(self.file_path):
          os.remove(self.file_path)
        os.rename(temp_file_path, self.file_path)
        return True
      except Exception as ex:
        self.__log('Unable to update assets file! %s' % ex, 4)
    return False
 
 
  def __download(self, url, local_file):
    '''
      Downloads a new asset from a given url
      If the asset is compressed, the file will be extracted
    '''
    try:
      self.__log('Downloading assets from url: %s' % url)
      res = urllib.request.urlopen(url)
      with open(local_file, "wb") as code:
        code.write(res.read())
      self.__log('Assets file downloaded and saved as %s' % local_file)
      return True
    except Exception as ex:
      self.__log(ex, 4)
      return False

  def __log(self, msg, level=2):
    if self._log_delegate:
      self._log_delegate(msg, level)