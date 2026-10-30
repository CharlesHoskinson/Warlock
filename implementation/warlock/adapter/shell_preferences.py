"""Validated appearance, native-selected private storage, revision CAS and atomic save.

Share the existing private-directory/lock discipline with taskbar preferences.
Unknown schema is preserved; no frontend path, automatic migration or retry.
Explicit schema-1 upgrades retain exact original bytes before active replacement.
"""
import json, os, secrets
from endpoint import Refused, exact, canonical, unique
from taskbar_preferences import Store as PrivateStore, MAX_REVISION

DEFAULTS={'theme':'night','textScale':100,'effectsOff':False,'reducedTransparency':False}
def values(value,legacy=False):
 exact(value,['theme','textScale'] if legacy else list(DEFAULTS))
 if value['theme'] not in ('night','dawn','high-contrast') or type(value['theme']) is not str:raise Refused('Appearance theme')
 if type(value['textScale']) is not int or value['textScale'] not in (100,125,150,200):raise Refused('Appearance text scale')
 if not legacy and any(type(value[k]) is not bool for k in ('effectsOff','reducedTransparency')):raise Refused('Appearance flags')
 return {**DEFAULTS,**value}

def snapshot(value):
 exact(value,['schema','revision','values'])
 if type(value['schema']) is not int or value['schema'] not in (1,2):raise Refused('Unsupported settings schema; preserve the stored copy')
 canonical(value['revision'])
 if value['revision']=='0':raise Refused('Settings revision')
 return {'schema':2,'revision':value['revision'],'values':values(value['values'],legacy=value['schema']==1)}

class Store(PrivateStore):
 def _read_original(self,directory):
  try:fd=os.open('settings.json',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
  except FileNotFoundError:return {'schema':2,'revision':'1','values':dict(DEFAULTS)},None,2
  try:
   self._private(fd);body=os.read(fd,4097)
   if len(body)>4096:raise Refused('Settings storage bound')
   value=json.loads(body,object_pairs_hook=unique)
   return snapshot(value),body,value['schema']
  finally:os.close(fd)
 def _read(self,directory):return self._read_original(directory)[0]
 def _preserve_legacy(self,directory,body):
  """Already locked: never replace an existing original or activate before fsync."""
  name='settings.schema-1.json';temporary=None
  try:
   try:fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
   except FileNotFoundError:
    temporary='settings.backup.'+secrets.token_hex(12)+'.tmp'
    fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
    with os.fdopen(fd,'wb') as stream:stream.write(body);stream.flush();os.fsync(stream.fileno())
    # A link publishes a complete inode without overwriting an existing backup.
    os.link(temporary,name,src_dir_fd=directory,dst_dir_fd=directory,follow_symlinks=False)
    os.unlink(temporary,dir_fd=directory);temporary=None
   else:
    try:
     self._private(fd)
     if os.read(fd,4097)!=body:raise Refused('Settings migration original conflicts with preserved copy')
     os.fsync(fd)
    finally:os.close(fd)
   os.fsync(directory)
  finally:
   if temporary:
    try:os.unlink(temporary,dir_fd=directory)
    except FileNotFoundError:pass
 def save(self,proposal):
  current=snapshot(proposal)
  if proposal['schema']!=2:raise Refused('Settings write requires current schema')
  proposal=current;directory,lock=self._open();temporary=None;renamed=False
  try:
   old,original,schema=self._read_original(directory)
   if old['revision']!=proposal['revision'] or old['values']==proposal['values'] or int(old['revision'])==MAX_REVISION:return 'Refused',old
   if schema==1:self._preserve_legacy(directory,original)
   saved={'schema':2,'revision':str(int(old['revision'])+1),'values':proposal['values']}
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
