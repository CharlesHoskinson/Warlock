"""Explicit shell shortcut decisions; private atomic storage, revision CAS.

Chord strings and command paths never come from the frontend. Existing native
bindings are left intact; the native authority admits only fixed free chords.
"""
import json,os,secrets
from endpoint import Refused,exact,canonical,unique
from taskbar_preferences import Store as PrivateStore,MAX_REVISION
ROUTES=('applications','system','notifications')
CHOICES=('undecided','keep','default','alternate')
def choices(value):
 exact(value,ROUTES)
 if any(type(value[r]) is not str or value[r] not in CHOICES for r in ROUTES):raise Refused('Shortcut choice')
 return value
def snapshot(value):
 exact(value,['schema','revision','choices'])
 if type(value['schema']) is not int or value['schema']!=1:raise Refused('Unsupported shortcut preference version; stored copy preserved')
 canonical(value['revision']);choices(value['choices']);return value
def fingerprint(value):
 if type(value) is not str or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):raise Refused('Shortcut binding fingerprint')
 return value
class Store(PrivateStore):
 def _read(self,directory):
  try:fd=os.open('shortcuts.json',os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
  except FileNotFoundError:return {'schema':1,'revision':'1','choices':{r:'undecided' for r in ROUTES}}
  try:
   self._private(fd);body=os.read(fd,4097)
   if len(body)>4096:raise Refused('Shortcut preference storage bound')
   return snapshot(json.loads(body,object_pairs_hook=unique))
  finally:os.close(fd)
 def save(self,proposal):
  snapshot(proposal)
  if 'undecided' in proposal['choices'].values():raise Refused('Choose each shortcut explicitly before saving')
  directory,lock=self._open();temporary=None;renamed=False
  try:
   old=self._read(directory)
   if old['revision']!=proposal['revision']:return 'Refused',old
   # An explicit user action may apply unchanged saved choices to a new native
   # session. Reading never applies them, and this path performs no file write.
   if old['choices']==proposal['choices']:return 'Saved',old
   if int(old['revision'])==MAX_REVISION:return 'Refused',old
   saved={'schema':1,'revision':str(int(old['revision'])+1),'choices':proposal['choices']}
   body=json.dumps(saved,separators=(',',':')).encode();temporary='shortcuts.'+secrets.token_hex(12)+'.tmp'
   fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
   with os.fdopen(fd,'wb') as stream:stream.write(body);stream.flush();os.fsync(stream.fileno())
   os.rename(temporary,'shortcuts.json',src_dir_fd=directory,dst_dir_fd=directory);renamed=True;temporary=None;os.fsync(directory)
   return 'Saved',saved
  except (OSError,ValueError):
   if renamed:return 'Unknown',None
   raise
  finally:
   if temporary:
    try:os.unlink(temporary,dir_fd=directory)
    except FileNotFoundError:pass
   os.close(lock);os.close(directory)
