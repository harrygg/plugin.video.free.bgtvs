# -*- coding: utf8 -*-
import os
import gzip
import xbmcvfs
import urllib.request, urllib.error, urllib.parse
from kodibgcommon.logging import log_info, log_error

### Basic class to download assets on a given time interval
### If download fails, and the old file doesn't exist
### Use a local file

class Assets:
  file = None
  temp_dir = None
  
  def __init__(self, db_file, backup_file):
    self.file = db_file
    self.backup_file = backup_file
    temp_dir = os.path.dirname(os.path.realpath(db_file))
    if not os.path.isdir(temp_dir):
      xbmcvfs.mkdir(temp_dir)
  
  def update(self, url):
    try:
      log_info('Downloading assets from url: %s' % url)
      self.download(url)
      log_info('Assets file downloaded and saved as %s' % self.file)
      return True
    except Exception as ex:
      log_error('Unable to update assets file! %s' % ex)
      return False
 
  def is_old(self, interval=24):
    '''
      Checks whether the asset file is older than the time interval in hours
      or that its older than the back_up file (in case of addon updates)
    '''
    try:
      from datetime import datetime, timedelta
      if os.path.isfile(self.file):
        treshold = datetime.now() - timedelta(hours=interval)
        modified = datetime.fromtimestamp(os.path.getmtime(self.file))
        if modified < treshold: #file is more than a day old
          return True
        backup_modified = datetime.fromtimestamp(os.path.getmtime(self.backup_file))
        if modified < backup_modified:
          return True
        return False
      else: #file does not exist, perhaps first run
        return True
    except Exception as er:
      log_error(er)
      return True

  def download(self, url):
    '''
      Downloads a new asset from a given url
      If the asset is compressed, the file will be extracted
    '''
    file_name = os.path.basename(url).split("?")[0]
    is_compressed = file_name.endswith('gz')
    if is_compressed:
      downloaded_file = os.path.join(self.temp_dir, file_name)
    else:
      downloaded_file = self.file
    res = urllib.request.urlopen(url)
    with open(downloaded_file, "wb") as code:
      code.write(res.read())    
    if is_compressed:
      self.extract(downloaded_file)  

  
  def extract(self, compressed_file):
    log_info("Extracting file %s" % compressed_file)
    with gzip.GzipFile(self.file, 'rb') as gz:
      with open(self.file, 'wb') as out_file:
        out_file.write( gz.read() )
    log_info("Extracted file saved to %s" % self.file)
