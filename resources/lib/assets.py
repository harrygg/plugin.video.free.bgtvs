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
  
  def __init__(self,  temp_dir, url, backup_file, log, auto_update = False, interval = 24):
    self.interval = interval
    if os.path.isdir(temp_dir) is False:
      self.__create_dir__(temp_dir)
    
    if url == '':
      raise ValueError("Valid asset url must be provided!")
    else:
      self.log = log
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
      self.log("Forced update: %s" % forced_update)
      if self.is_expired() or forced_update:
        res = self.get_asset()
      if self.file.endswith('gz'):
        self.extract()
      return True
    except Exception as ex:
      self.log(str(ex), 4)
      self.log('Unable to download assets file!', 4)
      return False
 
  def is_expired(self):
    try:
      from datetime import datetime, timedelta
      #Check if the file in userdata folder is old
      if os.path.isfile(self.file):
        treshold = datetime.now() - timedelta(hours=self.interval)
        modified = datetime.fromtimestamp(os.path.getmtime(self.file))
        #self.log("modified: " + str(modified))
        if modified < treshold: #file is more than a day old
          return True
        #Check if the file is older than the backup (in case of addon update)
        backup_modified = datetime.fromtimestamp(os.path.getmtime(self.backup_file))
        #self.log("backup_modified: " + str(backup_modified))
        if modified < backup_modified:
          return True
        return False
      else: #file does not exist, perhaps first run
        return True
    except Exception, er:
      self.log(str(er), 4)
      return True

  def get_asset(self):
    self.log('Downloading assets from url: %s' % self.url)
    f = urllib2.urlopen(self.url)
    with open(self.file, "wb") as code:
      code.write(f.read())
    self.log('Assets file downloaded')

  
  def extract(self):
    gz = gzip.GzipFile(self.file, 'rb')
    s = gz.read()
    gz.close()
    self.file = self.file.replace('.gz', '')
    with file(self.file, 'wb') as out:
      out.write(s)
