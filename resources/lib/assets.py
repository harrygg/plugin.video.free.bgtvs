# -*- coding: utf8 -*-
import os
import sys
import gzip
import urllib2

### Basic class to download assets on a given time interval
### If download fails, and the old file doesn't exist
### Use a local file

class Assets:
  interval = 24 #Hours Interval to check for new version of the asset
  
  def __init__(self, temp_dir, url, backup_file, auto_update=False, interval=24):
    from helper import log
    self.__log__ = log
    log("Asset initialization: temp_dir=%s, url=%s, backup_file=%s, auto_update=%s" % (temp_dir, url, backup_file, auto_update))
    self.interval = interval
    if not os.path.isdir(temp_dir):
      self.__create_dir__(temp_dir)
    
    if url == '':
      raise ValueError("Valid asset url must be provided!")
    else:
      self.url = url
      self.file_name = os.path.basename(url)
      self.file = os.path.join(temp_dir, self.file_name)
      self.backup_file = backup_file
      
    if auto_update:
      if not self.update():
        if not os.path.isfile(self.file) and os.path.isfile(self.backup_file): 
          #if asset was never downloaded and backup exists
          self.file = self.backup_file
    
  def __create_dir__(self, dir):
    try: os.makedirs(dir)
    except OSError as exc: # Guard against race condition
      if exc.errno != errno.EEXIST:
        raise
  
  def update(self, forced_update=False):
    try:
      self.__log__("Forced DB update: %s" % forced_update)
      if forced_update:
        self.get_asset()
      else:
        expired = self.is_expired()
        if expired:
          self.__log__("The DB file is old and will be updated")
          self.get_asset()
        else:
          self.__log__("The DB file is not old and will not be updated")
          
      if self.file.endswith('gz'):
        self.extract()
      return True
    except Exception as ex:
      self.__log__(str(ex), 4)
      self.__log__('Unable to download assets file!', 4)
      return False
 
  def is_expired(self):
    try:
      from datetime import datetime, timedelta
      #Check if the file in userdata folder is old
      if os.path.isfile(self.file):
        treshold = datetime.now() - timedelta(hours=self.interval)
        modified = datetime.fromtimestamp(os.path.getmtime(self.file))
        #self.__log__("modified: " + str(modified))
        if modified < treshold: #file is more than a day old
          return True
        #Check if the file is older than the backup (in case of addon update)
        backup_modified = datetime.fromtimestamp(os.path.getmtime(self.backup_file))
        #self.__log__("backup_modified: " + str(backup_modified))
        if modified < backup_modified:
          return True
        return False
      else: #file does not exist, perhaps first run
        return True
    except Exception, er:
      self.__log__(str(er), 4)
      return True

  def get_asset(self):
    self.__log__('Downloading assets from url: %s' % self.url, 2)
    f = urllib2.urlopen(self.url + "?t=1234567890")
    with open(self.file, "wb") as code:
      code.write(f.read())
    self.__log__('Assets file downloaded and saved as %s' % self.file)

  
  def extract(self):
    log("Extracting file %s" % self.file)
    gz = gzip.GzipFile(self.file, 'rb')
    s = gz.read()
    gz.close()
    self.file = self.file.replace('.gz', '')
    with file(self.file, 'wb') as out:
      out.write(s)
    log("Extracted file saved to %s" % self.file)
