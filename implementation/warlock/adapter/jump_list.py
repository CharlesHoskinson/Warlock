"""Native catalog actions and application-bound local recent-file navigation.

Exec/URI/source paths stay native. XBEL executable attributes are never used.
The only submitted actions belong to the current catalog desktop identity.
"""
import copy,hashlib,json,os,pathlib,secrets,stat
from urllib.parse import urlparse,unquote
from catalog_authority import fingerprint,text
from endpoint import Refused,binding,canonical,exact

class Lists:
 def __init__(self,catalog):
  self.catalog=catalog;self.service=str(secrets.randbelow(2**64-1)+1);self.revision=0;self.previous=None;self.targets={};self.last=None;self.spent=set();self.high=0;self.scope=None
  self.recent=pathlib.Path(os.environ.get('XDG_DATA_HOME',str(pathlib.Path.home()/'.local/share')))/'recently-used.xbel'
 def __enter__(self):return self
 def __exit__(self,*_):pass
 def recent_items(self,entry,app):
  # Unsupported recent-item providers contribute no actionable records.
  if not (app.supports_files() or app.supports_uris()):return [],None,''
  try:fd=os.open(self.recent,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
  except FileNotFoundError:return [],None,''
  except OSError:return [],None,'Recent items unavailable.'
  try:
   before=os.fstat(fd)
   if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or before.st_mode&0o022 or before.st_size>1048576:raise Refused('Recent source unavailable')
   body=os.read(fd,1048577);after=os.fstat(fd)
   if len(body)>1048576 or (before.st_dev,before.st_ino,before.st_mtime_ns,before.st_size)!=(after.st_dev,after.st_ino,after.st_mtime_ns,after.st_size):raise Refused('Recent source changed')
  except (OSError,Refused):return [],None,'Recent items unavailable.'
  finally:os.close(fd)
  digest=hashlib.sha256(body).hexdigest()
  try:
   import gi;gi.require_version('GLib','2.0');from gi.repository import GLib
   bookmarks=GLib.BookmarkFile.new();bookmarks.load_from_data(body)
   uris=bookmarks.get_uris()
   if len(uris)>4096:raise Refused('Recent item capacity')
   items=[];desktop_id=entry['id']+'.desktop'
   for uri in uris:
    if desktop_id not in bookmarks.get_applications(uri):continue
    text(uri,8192)
    parsed=urlparse(uri)
    if parsed.scheme!='file' or parsed.netloc not in ('','localhost') or parsed.query or parsed.fragment:continue
    path=pathlib.Path(unquote(parsed.path))
    if not path.is_absolute() or '\0' in str(path) or not path.is_file():continue
    info=path.stat();title=bookmarks.get_title(uri) or path.name;text(title,256)
    identity='recent:'+hashlib.sha256((desktop_id+'\0'+uri).encode()).hexdigest()
    modified=bookmarks.get_modified_date_time(uri).to_unix()
    items.append({'id':identity,'label':'Open '+title,'kind':'recent','uri':uri,'proof':[info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns],'modified':modified})
   items.sort(key=lambda item:(-item['modified'],item['id']))
   return items[:12],digest,''
  except Exception:return [],digest,'Recent items unavailable.'
 def observe(self,entry_id,advance=False):
  value={'entry':entry_id,'name':entry_id,'available':False,'reason':'Application unavailable.','actions':[]};targets={};proof=None
  try:
   self.catalog.snapshot();entry=self.catalog.entries.get(entry_id)
   if entry is not None:
    import gi;gi.require_version('GioUnix','2.0');from gi.repository import GioUnix
    before=self.catalog.fingerprints[entry_id];app=GioUnix.DesktopAppInfo.new_from_filename(entry['path'])
    if app is None or fingerprint(entry)!=before:raise Refused('Desktop entry changed')
    declared={action['id'] for action in entry['actions']};actions=[]
    for action in app.list_actions():
     if action not in declared:continue
     text(action,128);label=app.get_action_name(action);text(label,256)
     identity='desktop:'+action;actions.append({'id':identity,'label':label,'kind':'desktop'});targets[identity]={'kind':'desktop','action':action}
    if len(actions)>32 or len({item['id'] for item in actions})!=len(actions):raise Refused('Desktop action capacity')
    recent,digest,reason=self.recent_items(entry,app)
    for item in recent:
     actions.append({k:item[k] for k in ('id','label','kind')});targets[item['id']]={k:item[k] for k in ('kind','uri','proof')}
    if fingerprint(entry)!=before:raise Refused('Desktop entry changed')
    value={'entry':entry_id,'name':entry['name'],'available':True,'reason':reason,'actions':actions}
    proof={'entry':before,'catalog':self.catalog.signature,'recent':digest,'targets':targets}
  except Exception:pass
  signature={'view':value,'proof':proof}
  if signature!=self.previous or advance:
   if self.revision>=2**64-1:raise Refused('Jump list revision exhausted')
   self.revision+=1;self.previous=copy.deepcopy(signature);self.targets=copy.deepcopy(targets);self.last=copy.deepcopy(value);self.spent={key for key in self.spent if key[0]>=self.revision-32}
  return {'service':self.service,'revision':str(self.revision),**copy.deepcopy(value)}
 def verify(self,request,client,effect):
  exact(request,['protocolVersion','kind','binding','requestId',*(['intent'] if effect else ['entry'])]);canonical(request['requestId'])
  if type(request['protocolVersion']) is not int or request['protocolVersion']!=3 or request['kind']!=('jump-list-effect' if effect else 'jump-list-request') or binding(request['binding'])!=client.bound:raise Refused('Jump list binding')
  client.verify_process();client.verify_paths()
 def read(self,request,client):
  self.verify(request,client,False);text(request['entry'],256);snapshot=self.observe(request['entry']);self.verify(request,client,False)
  return {'protocolVersion':3,'kind':'jump-list-snapshot','binding':client.bound,'requestId':request['requestId'],'snapshot':snapshot}
 def effect(self,request,client):
  self.verify(request,client,True);intent=request['intent'];exact(intent,['service','revision','entry','action']);canonical(intent['service']);canonical(intent['revision']);text(intent['entry'],256);text(intent['action'],256)
  current=self.observe(intent['entry']);status='Refused';key=(int(intent['revision']),intent['entry'],intent['action'])
  if self.scope!=client.bound:self.scope=copy.deepcopy(client.bound);self.high=0
  number=int(request['requestId'])
  if number>self.high:
   self.high=number
   if intent['service']==self.service and intent['revision']==current['revision'] and current['available'] and key not in self.spent and intent['action'] in self.targets:
    submitted=False
    try:
     import gi;gi.require_version('GioUnix','2.0');gi.require_version('Gio','2.0');from gi.repository import Gio,GioUnix
     entry=self.catalog.entries[intent['entry']];before=self.catalog.fingerprints[intent['entry']];app=GioUnix.DesktopAppInfo.new_from_filename(entry['path']);target=copy.deepcopy(self.targets[intent['action']])
     if app is None or fingerprint(entry)!=before:raise Refused('Desktop entry changed')
     if target['kind']=='recent':
      path=pathlib.Path(unquote(urlparse(target['uri']).path));info=path.stat()
      if [info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns]!=target['proof']:raise Refused('Recent item changed')
     self.spent.add(key);submitted=True;status='Unknown'
     if target['kind']=='desktop':
      if target['action'] not in app.list_actions():raise Refused('Desktop action withdrawn')
      app.launch_action(target['action'],Gio.AppLaunchContext());status='Submitted'
     elif app.launch([Gio.File.new_for_uri(target['uri'])],Gio.AppLaunchContext()):status='Submitted'
     if status=='Submitted':current=self.observe(intent['entry'],advance=True)
    except Exception:status='Unknown' if submitted else 'Refused'
  self.verify(request,client,True)
  return {'protocolVersion':3,'kind':'jump-list-outcome','binding':client.bound,'requestId':request['requestId'],'status':status,'snapshot':current}
