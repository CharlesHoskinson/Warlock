"""Legacy catalog presentation and identity/generation-bound GIO submission.

Paths/Exec remain native; Submitted is not application readiness. This authority
is a component awaiting authenticated host/broker integration, not a public RPC.
"""
import copy,hashlib,json,secrets
from pathlib import Path
from taskbar_catalog import load_catalog
MAX_COUNTER=(1<<64)-1
MAX_SNAPSHOT_BYTES=1024*1024
class Refused(ValueError):pass
def counter(value):
 if not isinstance(value,str) or not value.isascii() or not value.isdecimal() or value.startswith('0') or len(value)>20 or int(value)>MAX_COUNTER:raise Refused('Noncanonical counter')
 return int(value)
def text(value,limit,empty=False):
 if not isinstance(value,str) or (not empty and not value) or len(value.encode('utf-16-le'))//2>limit or any(ord(c)<32 for c in value):raise Refused('Catalog text bound')
 return value
def fingerprint(entry):
 p=Path(entry['path']);before=p.stat();body=p.read_bytes();after=p.stat()
 stamps=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 if stamps(before)!=stamps(after):raise Refused('Desktop entry raced')
 return hashlib.sha256(json.dumps([entry,stamps(after),hashlib.sha256(body).hexdigest()],sort_keys=True,ensure_ascii=True).encode()).hexdigest()
class Authority:
 def __init__(self,data_home,data_dirs,cache_dir):
  self.roots=(data_home,data_dirs,cache_dir);self.lifetime=str(secrets.randbelow(MAX_COUNTER)+1);self.generation=0;self.signature=None;self.entries={};self.fingerprints={};self.available=False;self.last_request=0;self.last_payload=None;self.last_outcome=None
 def snapshot(self):
  self.available=False
  entries=load_catalog(*self.roots)
  if len(entries)>2048:raise Refused('Prototype catalog capacity')
  prints={};rows=[]
  for identity,entry in sorted(entries.items()):
   text(identity,256);text(entry['name'],512,True);text(entry['icon'],512,True)
   text(entry['genericName'],512,True)
   if len(entry['keywords'])>64:raise Refused('Keyword capacity')
   for word in entry['keywords']:text(word,128,True)
   if entry['wmclass']:text(entry['wmclass'],512)
   prints[identity]=fingerprint(entry)
   rows.append({'id':identity,'name':entry['name'],'iconHint':entry['icon'],'wmclass':entry['wmclass'],'genericName':entry['genericName'],'keywords':entry['keywords']})
  # Include native-only Exec/path/action/terminal bytes and file identity.
  signature=hashlib.sha256(json.dumps(prints,sort_keys=True).encode()).hexdigest()
  generation=self.generation
  if signature!=self.signature:
   if generation==MAX_COUNTER:raise Refused('Catalog generation exhausted')
   generation+=1
  snapshot={'catalogProtocol':2,'lifetime':self.lifetime,'generation':str(generation),'entries':rows}
  if len(json.dumps(snapshot,ensure_ascii=True,separators=(',',':')).encode())>MAX_SNAPSHOT_BYTES:raise Refused('Prototype catalog byte capacity')
  self.generation=generation;self.signature=signature
  self.entries=entries;self.fingerprints=prints;self.available=True
  return snapshot
 def launch(self,intent):
  if not isinstance(intent,dict) or set(intent)!={'request','lifetime','generation','entry'}:raise Refused('Launch intent fields')
  request=counter(intent['request']);counter(intent['lifetime']);counter(intent['generation']);text(intent['entry'],256)
  payload=json.dumps(intent,sort_keys=True)
  def outcome(status,reason):return {'catalogProtocol':1,'kind':'launch-outcome','intent':dict(intent),'status':status,'reason':reason}
  if intent['lifetime']!=self.lifetime:return outcome('Refused','retired-authority')
  if request==self.last_request:return copy.deepcopy(self.last_outcome) if payload==self.last_payload else outcome('Refused','request-reuse')
  if request<self.last_request:return outcome('Refused','retired-request')
  self.last_request=request;self.last_payload=payload;self.last_outcome=outcome('Unknown','submission-not-confirmed')
  def refuse(reason):self.last_outcome=outcome('Refused',reason);return copy.deepcopy(self.last_outcome)
  if not self.available:return refuse('catalog-unavailable')
  old_generation=self.generation
  try:self.snapshot()
  except (OSError,ValueError,UnicodeError):return refuse('catalog-unavailable')
  if str(old_generation)!=intent['generation'] or self.generation!=old_generation:return refuse('stale-catalog')
  entry=self.entries.get(intent['entry'])
  if entry is None:return refuse('removed-entry')
  # GIO loads the original filename into an owned DesktopAppInfo. Validate its
  # source again before submission; launch uses that native object, not JS text.
  import gi
  gi.require_version('GioUnix','2.0');gi.require_version('Gio','2.0')
  from gi.repository import Gio,GioUnix
  try:
   before=self.fingerprints[intent['entry']]
   app=GioUnix.DesktopAppInfo.new_from_filename(entry['path'])
   if app is None:return refuse('native-entry-unavailable')
   if fingerprint(entry)!=before:return refuse('desktop-entry-raced')
  except (OSError,ValueError,UnicodeError):return refuse('desktop-entry-raced')
  try:
   if app.launch([],Gio.AppLaunchContext()):self.last_outcome=outcome('Submitted','native-submission-accepted')
  except Exception:pass # Preserve Unknown; never automatically retry.
  return copy.deepcopy(self.last_outcome)
