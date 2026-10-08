"""Versioned motion override, native-selected private file and revision CAS.

None removes the explicit override. Reading never migrates or rewrites a file.
"""
import json,os,secrets
from endpoint import Refused,exact,canonical,unique
from taskbar_preferences import Store as PrivateStore,MAX_REVISION

def snapshot(value):
 exact(value,['schema','revision','override'])
 if type(value['schema']) is not int or value['schema']!=1:raise Refused('Unsupported motion preference version; stored copy preserved')
 canonical(value['revision'])
 if value['override'] is not None and (type(value['override']) is not str or value['override'] not in ('reduced','full')):raise Refused('Motion override')
 return value

class Store(PrivateStore):
 def _read(self,directory):
  try:fd=os.open('motion.json',os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
  except FileNotFoundError:return {'schema':1,'revision':'1','override':None}
  try:
   self._private(fd);body=os.read(fd,4097)
   if len(body)>4096:raise Refused('Motion preference storage bound')
   return snapshot(json.loads(body,object_pairs_hook=unique))
  finally:os.close(fd)
 def save(self,proposal):
  snapshot(proposal);directory,lock=self._open();temporary=None;renamed=False
  try:
   old=self._read(directory)
   if old['revision']!=proposal['revision'] or old['override']==proposal['override'] or int(old['revision'])==MAX_REVISION:return 'Refused',old
   saved={'schema':1,'revision':str(int(old['revision'])+1),'override':proposal['override']}
   body=json.dumps(saved,separators=(',',':')).encode()
   temporary='motion.'+secrets.token_hex(12)+'.tmp'
   fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
   with os.fdopen(fd,'wb') as stream:stream.write(body);stream.flush();os.fsync(stream.fileno())
   os.rename(temporary,'motion.json',src_dir_fd=directory,dst_dir_fd=directory);renamed=True;temporary=None;os.fsync(directory)
   return 'Saved',saved
  except (OSError,ValueError):
   if renamed:return 'Unknown',None
   raise
  finally:
   if temporary:
    try:os.unlink(temporary,dir_fd=directory)
    except FileNotFoundError:pass
   os.close(lock);os.close(directory)
