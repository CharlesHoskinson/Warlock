"""Validated appearance, native-selected private storage, revision CAS and atomic save.

Share the existing private-directory/lock discipline with taskbar preferences.
Unknown schema is preserved; no frontend path, automatic migration or retry.
"""
import json, os, secrets
from endpoint import Refused, exact, canonical, unique
from taskbar_preferences import Store as PrivateStore, MAX_REVISION

def values(value):
 exact(value,['theme','textScale'])
 if value['theme'] not in ('night','dawn','high-contrast') or type(value['theme']) is not str:raise Refused('Appearance theme')
 if type(value['textScale']) is not int or value['textScale'] not in (100,125,150,200):raise Refused('Appearance text scale')
 return value

def snapshot(value):
 exact(value,['schema','revision','values'])
 if type(value['schema']) is not int or value['schema']!=1:raise Refused('Unsupported settings schema; preserve the stored copy')
 canonical(value['revision']);values(value['values']);return value

class Store(PrivateStore):
 def _read(self,directory):
  try:fd=os.open('settings.json',os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
  except FileNotFoundError:return {'schema':1,'revision':'1','values':{'theme':'night','textScale':100}}
  try:
   self._private(fd);body=os.read(fd,4097)
   if len(body)>4096:raise Refused('Settings storage bound')
   return snapshot(json.loads(body,object_pairs_hook=unique))
  finally:os.close(fd)
 def save(self,proposal):
  snapshot(proposal);directory,lock=self._open();temporary=None;renamed=False
  try:
   old=self._read(directory)
   if old['revision']!=proposal['revision'] or old['values']==proposal['values'] or int(old['revision'])==MAX_REVISION:return 'Refused',old
   saved={'schema':1,'revision':str(int(old['revision'])+1),'values':proposal['values']}
   body=json.dumps(saved,separators=(',',':')).encode()
   temporary='settings.'+secrets.token_hex(12)+'.tmp'
   fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
   with os.fdopen(fd,'wb') as stream:stream.write(body);stream.flush();os.fsync(stream.fileno())
   os.rename(temporary,'settings.json',src_dir_fd=directory,dst_dir_fd=directory);renamed=True;temporary=None;os.fsync(directory)
   return 'Saved',saved
  except (OSError,ValueError):
   if renamed:return 'Unknown',None
   raise
  finally:
   if temporary:
    try:os.unlink(temporary,dir_fd=directory)
    except FileNotFoundError:pass
   os.close(lock);os.close(directory)
